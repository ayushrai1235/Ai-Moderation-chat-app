from sqlalchemy import Column, String, ForeignKey, DateTime, text, Index
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func
from app.db.base import Base

class User(Base):
    __tablename__ = "users"
    
    id = Column(UUID(as_uuid=True), primary_key=True, server_default=text("uuid_generate_v4()"))
    email = Column(String, unique=True, nullable=False)
    username = Column(String, unique=True, nullable=False)
    password_hash = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

class Conversation(Base):
    __tablename__ = "conversations"
    
    id = Column(UUID(as_uuid=True), primary_key=True, server_default=text("uuid_generate_v4()"))
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

class Participant(Base):
    __tablename__ = "participants"
    
    conversation_id = Column(UUID(as_uuid=True), ForeignKey("conversations.id", ondelete="CASCADE"), primary_key=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    joined_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

class Message(Base):
    __tablename__ = "messages"
    
    id = Column(UUID(as_uuid=True), primary_key=True, server_default=text("uuid_generate_v4()"))
    # In earlier schema room_id was string (for 'general' etc), but in private chat update we moved to conversation_id?
    # Wait, the task.md says "Update WebSocket to use conversation_id" was done. 
    # But schema.sql for messages was not fully replaced, just ALTERED.
    # The existing 'messages' table likely still has 'room_id' from original implementation.
    # We should define it as is.
    room_id = Column(String, nullable=True) # Could be conversation UUID or 'general'
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    content = Column(String, nullable=True)
    type = Column(String, server_default="text")
    file_url = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    status = Column(String, nullable=True) # moderation status
    moderation_status = Column(String, server_default='pending')
    moderation_status = Column(String, server_default='pending')
    moderation_details = Column(JSONB, nullable=True)

class ModerationLog(Base):
    __tablename__ = "moderation_logs"
    
    id = Column(UUID(as_uuid=True), primary_key=True, server_default=text("uuid_generate_v4()"))
    message_id = Column(String, nullable=False) # storing as string for flexibility/legacy matching
    category = Column(String)
    severity = Column(String)
    action = Column(String)
    confidence = Column(String) # or Float
    explanation = Column(String)
    raw_response = Column(JSONB)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
