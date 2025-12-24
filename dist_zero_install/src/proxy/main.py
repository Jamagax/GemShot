import os
import base64
import logging
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import google.generativeai as genai

app = FastAPI()

class GeminiRequest(BaseModel):
    image: str  # base64 encoded PNG
    instructions: str = ""

def get_gemini_client():
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError("GEMINI_API_KEY not set in environment")
    genai.configure(api_key=api_key)
    return genai.GenerativeModel("gemini-1.5-flash")

def decode_image(b64_str: str):
    try:
        return base64.b64decode(b64_str)
    except Exception as e:
        raise HTTPException(status_code=400, detail="Invalid base64 image")

@app.post("/analyze")
def analyze(req: GeminiRequest):
    try:
        client = get_gemini_client()
        image_bytes = decode_image(req.image)
        # Convert bytes to a genai.Image object
        img = genai.upload_file(content=image_bytes, mime_type="image/png")
        prompt = req.instructions or "Analyze this screenshot. Provide Title, Tags, and Summary."
        response = client.generate_content([prompt, img])
        return {"result": response.text}
    except Exception as e:
        logging.error(f"Analyze error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/smart_fill")
def smart_fill(req: GeminiRequest):
    try:
        client = get_gemini_client()
        image_bytes = decode_image(req.image)
        img = genai.upload_file(content=image_bytes, mime_type="image/png")
        base_prompt = """
        Analyze this screenshot and return a JSON with fields: title, tags, summary, deadline, type, software, file_path.
        """
        if req.instructions:
            base_prompt = f"{req.instructions}\n{base_prompt}"
        response = client.generate_content([base_prompt, img], generation_config={"response_mime_type": "application/json"})
        return {"result": response.text}
    except Exception as e:
        logging.error(f"Smart fill error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
