import google.generativeai as genai
import threading
import os
import logging

from src.core.config import GEMINI_MODEL

import threading
import logging
import requests
import json
import base64

PROXY_URL = "http://127.0.0.1:8000"

class AIService:
    def __init__(self, api_key=None):
        # api_key is no longer needed; the proxy holds it.
        self.api_key = api_key

    def _post_to_proxy(self, endpoint: str, image_bytes: bytes, instructions: str | None = None):
        """Send image and optional instructions to the local proxy.
        Returns the raw text response or raises an exception.
        """
        payload = {
            "image": base64.b64encode(image_bytes).decode("utf-8"),
            "instructions": instructions or "",
        }
        try:
            resp = requests.post(f"{PROXY_URL}{endpoint}", json=payload, timeout=30)
            resp.raise_for_status()
            return resp.text
        except Exception as e:
            logging.error(f"Proxy request failed: {e}")
            raise

    def analyze_image(self, image, callback, error_callback, instructions=None):
        if not image:
            error_callback("No image provided.")
            return
        def _run():
            try:
                # image is a PIL Image; convert to bytes (PNG)
                from io import BytesIO
                buf = BytesIO()
                image.save(buf, format="PNG")
                result = self._post_to_proxy("/analyze", buf.getvalue(), instructions)
                callback(result, is_custom=bool(instructions))
            except Exception as e:
                error_callback(str(e))
        threading.Thread(target=_run, daemon=True).start()

    def smart_fill_analysis(self, image, callback, error_callback, instructions=None):
        if not image:
            error_callback("No image provided.")
            return
        def _run():
            try:
                from io import BytesIO
                buf = BytesIO()
                image.save(buf, format="PNG")
                result = self._post_to_proxy("/smart_fill", buf.getvalue(), instructions)
                callback(result)
            except Exception as e:
                error_callback(str(e))
        threading.Thread(target=_run, daemon=True).start()

    def __init__(self, api_key=None):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")

    def analyze_image(self, image, callback, error_callback, instructions=None):
        if not self.api_key:
            error_callback("No API Key configured.")
            return

        def _run():
            try:
                genai.configure(api_key=self.api_key)
                model = genai.GenerativeModel(GEMINI_MODEL)
                
                base_prompt = "Analyze this screenshot. Provide a suggested Title, a brief summary for Notes, and 3-5 relevant tags. Format: Title: <title> | Tags: <tags> | Summary: <summary>"
                
                if instructions:
                    print(f"Running Custom Analysis: {instructions}")
                    base_prompt = f"USER INSTRUCTION: {instructions}\n\nAnalyze the image specifically following the user's instruction above. Provide the result in clear text."
                
                response = model.generate_content([
                    base_prompt,
                    image
                ])
                callback(response.text, is_custom=bool(instructions))
            except Exception as e:
                logging.error(f"AI Error: {e}")
                error_callback(str(e))

        threading.Thread(target=_run, daemon=True).start()

    def smart_fill_analysis(self, image, callback, error_callback, instructions=None):
        if not self.api_key:
            error_callback("No API Key configured.")
            return

        def _run():
            try:
                genai.configure(api_key=self.api_key)
                model = genai.GenerativeModel(GEMINI_MODEL)
                
                custom_instruct = ""
                if instructions:
                    custom_instruct = f"\nIMPORTANT - USER INSTRUCTIONS: {instructions}\n(Prioritize these instructions for the analysis/filling)\n"

                prompt = f"""
                Analyze this screenshot and determine these details. {custom_instruct} return a valid JSON object:
                {{
                    "title": "A short, summarized, and highly readable title (max 5-7 words)",
                    "tags": "3-5 comma-separated tags",
                    "summary": "A brief analysis/summary of the visual content",
                    "deadline": "YYYY-MM-DD (only if clearly visible date found, else null)",
                    "type": "One of: ['Nota', 'Screen', 'Minuta', 'Archivo', 'Task', 'Hito'] (Default: Screen)",
                    "software": "Name of the active program if visible (e.g. VS Code, Chrome, Blender, Excel)",
                    "file_path": "Full file path if visible in title bar or address bar, else null"
                }}
                """
                
                response = model.generate_content(
                    [prompt, image],
                    generation_config={"response_mime_type": "application/json"}
                )
                callback(response.text)
            except Exception as e:
                logging.error(f"AI Auto-Fill Error: {e}")
                error_callback(str(e))

        threading.Thread(target=_run, daemon=True).start()
