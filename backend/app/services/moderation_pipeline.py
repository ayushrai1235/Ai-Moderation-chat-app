from app.services.redis_service import redis_client
from app.services.gemini_service import gemini_service
import json
import time
import uuid

class ModerationPipeline:
    async def process_message(self, message_data: dict, room_id: str):
        """
        Full pipeline: Buffer -> Moderate -> Decision -> Broadcast/Block
        """
        message_id = str(uuid.uuid4())
        message_data['id'] = message_id
        message_data['timestamp'] = time.time()
        message_data['status'] = 'pending'

        # 1. Buffer in Redis (Temporary storage)
        # Store for 1 hour just in case
        await redis_client.set_value(f"msg:{message_id}", json.dumps(message_data), ttl=3600)

        # 2. Moderation
        # For now, we assume text messages. Future: handle file attachments.
        text_content = message_data.get('content', '')
        
        # Skip moderation for system messages or if empty
        if not text_content:
            decision = {"action": "allow", "category": "safe"}
        else:
            decision = await gemini_service.moderate_content(text=text_content)

        # 3. Apply Decision
        message_data['moderation'] = decision
        
        if decision['action'] == 'block':
            message_data['status'] = 'blocked'
            # message_data['content'] = "[Message Blocked by AI Moderation]" 
            # ^ REMOVED: Keep original content so Sender can see it.
            # The WebSocket Manager will filter it out for recipients.
        elif decision['action'] == 'warn':
            message_data['status'] = 'warning'
        else:
            message_data['status'] = 'allowed'

        # 4. Broadcast (Publish to Redis Channel)
        # We broadcast EVERYTHING to the Redis channel.
        # The WebSocketManager (subscriber) will handle visibility logic (Sender vs Recipient).
        await redis_client.publish(room_id, message_data)
        
        if decision['action'] == 'block':
             await self.log_flagged_message(message_data)

        # 5. Store in Database (Supabase)
        try:
            from app.services.supabase_service import supabase_service
            # We fire and forget, or await. Await is safer for consistency.
            # We insert the message regardless of status (even blocked, so we have record),
            # OR we only insert allowed? 
            # Usually blocked messages are kept for audit but marked blocked.
            await supabase_service.insert_message(message_data)
            
            if 'moderation' in message_data:
                await supabase_service.log_moderation(message_id, message_data['moderation'])
                
        except Exception as e:
            print(f"Persistence Error: {e}")

    async def log_flagged_message(self, message_data: dict):
        """Log flagged/blocked messages to a Redis list for Admin UI"""
        await redis_client.push_to_queue("admin:flagged_messages", message_data)

moderation_pipeline = ModerationPipeline()

