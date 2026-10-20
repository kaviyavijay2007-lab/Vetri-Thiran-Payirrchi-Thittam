import json
from typing import List
from google import genai
from google.genai import types
from app.config import settings
from app.schemas import PanelOutline, PromptRequest

def get_client():
    if not settings.gemini_api_key:
        raise RuntimeError("GEMINI_API_KEY is not configured. Add your Gemini API key to the .env file.")
    return genai.Client(api_key=settings.gemini_api_key)

def generate_outline(request: PromptRequest) -> List[PanelOutline]:
    client = get_client()
    prompt = f"""
Create exactly 5 connected comic panels.
Story idea: {request.story_prompt}
Main character: {request.character_name}
Setting: {request.setting}
Tone: {request.tone}
Art style: {request.art_style}

Each panel needs:
panel_number, title, scene_description, image_prompt.

Return only valid JSON. Do not put written text inside image prompts.
"""
    response = client.models.generate_content(
        model=settings.gemini_flash_model,
        contents=prompt,
        config=types.GenerateContentConfig(
            temperature=0.8,
            response_mime_type="application/json",
            response_schema=list[PanelOutline],
        ),
    )
    if not response.text:
        raise RuntimeError("Gemini Flash returned an empty response.")
    try:
        data = json.loads(response.text)
        outlines = [PanelOutline.model_validate(item) for item in data]
    except Exception as exc:
        raise RuntimeError(f"Failed to parse Gemini outline: {exc}") from exc
    if len(outlines) != settings.max_panels:
        raise RuntimeError(f"Expected {settings.max_panels} panels but received {len(outlines)}.")
    return outlines
