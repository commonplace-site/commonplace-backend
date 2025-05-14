import os
import httpx
from typing import Optional, Dict, Any
from dotenv import load_dotenv

load_dotenv()

SYNESTHESIA_API_KEY = os.getenv("SYNESTHESIA_API_KEY")
SYNESTHESIA_API_URL = "https://api.synesthesia.ai/v1"  # Replace with actual API endpoint

class AvatarService:
    def __init__(self):
        self.api_key = SYNESTHESIA_API_KEY
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

    async def generate_avatar(
        self,
        text: str,
        voice_id: str,
        style: Optional[str] = "natural",
        emotion: Optional[str] = "neutral",
        background: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate an avatar video with synchronized speech
        
        Args:
            text: The text to be spoken
            voice_id: The voice ID to use
            style: The avatar style (natural, cartoon, etc.)
            emotion: The emotional expression
            background: Optional background image/video URL
            
        Returns:
            Dict containing video URL and metadata
        """
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{SYNESTHESIA_API_URL}/generate",
                    headers=self.headers,
                    json={
                        "text": text,
                        "voice_id": voice_id,
                        "style": style,
                        "emotion": emotion,
                        "background": background
                    }
                )
                
                if response.status_code != 200:
                    raise Exception(f"Synesthesia API error: {response.text}")
                
                return response.json()
                
        except Exception as e:
            raise Exception(f"Avatar generation failed: {str(e)}")

    async def get_available_avatars(self) -> Dict[str, Any]:
        """Get list of available avatars and their properties"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{SYNESTHESIA_API_URL}/avatars",
                    headers=self.headers
                )
                
                if response.status_code != 200:
                    raise Exception(f"Synesthesia API error: {response.text}")
                
                return response.json()
                
        except Exception as e:
            raise Exception(f"Failed to fetch avatars: {str(e)}")

# Create a singleton instance
avatar_service = AvatarService() 