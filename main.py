from pathlib import Path
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from app.config import settings
from app.routes import router

BASE_DIR = Path(__file__).resolve().parent.parent
STATIC_DIR = BASE_DIR / "static"
(STATIC_DIR / "panels").mkdir(parents=True, exist_ok=True)
(STATIC_DIR / "exports").mkdir(parents=True, exist_ok=True)

app = FastAPI(
    title=settings.app_name,
    description="AI Comic Story Creator using Gemini and Stable Diffusion",
    version="1.0.0",
)
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")
app.include_router(router)

@app.get("/health")
async def health():
    return {
        "status": "ok",
        "application": settings.app_name,
        "image_provider": settings.image_provider,
        "gemini_configured": bool(settings.gemini_api_key),
    }
