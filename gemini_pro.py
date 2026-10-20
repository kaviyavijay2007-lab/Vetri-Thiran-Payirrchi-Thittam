import json
from typing import List
from google import genai
from google.genai import types
from app.config import settings
from app.schemas import PanelOutline, PanelStory, PromptRequest

def get_client():
    if not settings.gemini_api_key:
        raise RuntimeError("GEMINI_API_KEY is not configured. Add your Gemini API key to the .env file.")
    return genai.Client(api_key=settings.gemini_api_key)

def generate_story(request: PromptRequest, outlines: List[PanelOutline]) -> List[PanelStory]:
    client = get_client()
    outline_json = json.dumps([p.model_dump() for p in outlines], indent=2, ensure_ascii=False)
    prompt = f"""
Create a complete five-panel comic script from this outline.

Story idea: {request.story_prompt}
Main character: {request.character_name}
Setting: {request.setting}
Tone: {request.tone}
Art style: {request.art_style}

Outline:
{outline_json}

For every panel create:
panel_number, title, scene_description, caption, narration, dialogue, image_prompt.

Keep dialogue short and natural. Keep character names consistent.
Return only valid JSON.
"""
    response = client.models.generate_content(
        model=settings.gemini_pro_model,
        contents=prompt,
        config=types.GenerateContentConfig(
            temperature=0.9,
            response_mime_type="application/json",
            response_schema=list[PanelStory],
        ),
    )
    if not response.text:
        raise RuntimeError("Gemini Pro returned an empty response.")
    try:
        data = json.loads(response.text)
        stories = [PanelStory.model_validate(item) for item in data]
    except Exception as exc:
        raise RuntimeError(f"Failed to parse Gemini story: {exc}") from exc
    if len(stories) != settings.max_panels:
        raise RuntimeError(f"Expected {settings.max_panels} panels but received {len(stories)}.")
    return stories
