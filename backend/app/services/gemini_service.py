import google.generativeai as genai
from app.config import get_settings
import json
from typing import Optional

settings = get_settings()

genai.configure(api_key=settings.GEMINI_API_KEY)

class GeminiService:
    def __init__(self):
        self.model = genai.GenerativeModel('gemini-2.5-flash')

    async def moderate_content(self, text: str = None, image_parts: list = None, mime_type: str = None):
        """
        Moderate text or image content using Gemini.
        Returns a structured JSON decision.
        """
        
        prompt = """
        You are a content moderation AI. Analyze the input and provide a moderation decision in STRICT JSON format.
        
        Rules:
        - Categories: safe, spam, harassment, hate, sexual, violence
        - Severity: low, medium, high
        - Action: allow, warn, block
        
        Output JSON schema:
        {
            "category": "string",
            "severity": "string",
            "confidence": float,
            "explanation": "string",
            "action": "string"
        }
        
        If the content is safe, set category to "safe", severity to "low", and action to "allow".
        """
        
        content = [prompt]
        if text:
            content.append(f"Text to moderate: {text}")
        
        if image_parts:
            # image_parts should be a list of dictionaries compatible with Gemini API
            # e.g. [{"mime_type": "image/jpeg", "data": bytes}]
            content.extend(image_parts)

        try:
            response = self.model.generate_content(content)
            # Debug: Print raw text
            print(f"Gemini Raw Response: {response.text}")
            
            # Clean up the response to ensure it's valid JSON
            text_response = response.text.replace("```json", "").replace("```", "").strip()
            return json.loads(text_response)
        except Exception as e:
            print(f"Gemini Moderation Error: {e}")
            # Debug: Print full error details
            import traceback
            traceback.print_exc()
            
            # Help debug model issues
            if "404" in str(e) or "not found" in str(e):
                print("\nAvailable Models:")
                try:
                    for m in genai.list_models():
                        if 'generateContent' in m.supported_generation_methods:
                            print(f"- {m.name}")
                except Exception as list_e:
                    print(f"Failed to list models: {list_e}")

            # Fail safe: block if moderation fails? Or allow with warning? 
            # Let's return a fail-safe block for now to be safe.
            return {
                "category": "unknown",
                "severity": "high",
                "confidence": 0.0,
                "explanation": f"Moderation failed: {str(e)}",
                "action": "block"
            }

gemini_service = GeminiService()
