# Create BedrockChat
# bedrock_chat.py
from typing import Optional, Dict, Any
import requests

# Model ID
MODEL_ID = "llama3.2:1b"

class OllamaChat:
    """Initialize Ollama chat client"""

    def __init__(self, model_id: str = MODEL_ID):
        self.model_id = model_id
        self.ollama_url = "http://localhost:11434/api/generate"

    def generate_response(
        self,
        message: str,
        inference_config: Optional[Dict[str, Any]] = None
    ) -> Optional[str]:
        """Generate a response using local Ollama"""
        if inference_config is None:
            inference_config = {
                "temperature": 0.7
            }
        payload = {
            "model": self.model_id,
            "prompt": message,
            "stream": False,
            "options": inference_config
        }
        try:
            response = requests.post(self.ollama_url, json=payload)
            response.raise_for_status()
            return response.json()["response"]
        except Exception as e:
            print(f"Error generating response: {str(e)}")
            return None

if __name__ == "__main__":
    chat = OllamaChat()

    while True:
        user_input = input("You: ")
        if user_input.lower() == '/exit':
            break

        response = chat.generate_response(user_input)
        print("Bot:", response)
