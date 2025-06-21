import litellm
from PIL import Image, ImageEnhance
from config import Config
import os
import base64
import io


class LLMHandler:
    def __init__(self):
        litellm.set_verbose = False
        
        os.environ["GEMINI_API_KEY"] = Config.GEMINI_API_KEY
        self.model_name = Config.LLM_MODEL

    def _encode_image_to_base64(self, image_path):
        img = Image.open(image_path)
        img = img.convert("L")
        img = ImageEnhance.Contrast(img).enhance(3.0)
        
        buffered = io.BytesIO()
        img.save(buffered, format="PNG")
        img_base64 = base64.b64encode(buffered.getvalue()).decode('utf-8')
        return f"data:image/png;base64,{img_base64}"

    def generate_response(self, prompt, image_path=None):
        try:
            messages = []
            if image_path and os.path.exists(image_path):
                image_base64 = self._encode_image_to_base64(image_path)
                messages.append({
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {"type": "image_url", "image_url": {"url": image_base64}}
                    ]
                })
            else:
                messages.append({
                    "role": "user",
                    "content": prompt
                })
            
            response = litellm.completion(
                model=self.model_name,
                messages=messages,
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            raise Exception(f"Error generating response: {str(e)}")
