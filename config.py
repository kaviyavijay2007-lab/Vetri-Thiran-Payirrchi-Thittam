from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent

class Settings(BaseSettings):
    app_name: str = "ComicCraft"
    debug: bool = True
    gemini_api_key: str = ""
    gemini_flash_model: str = "gemini-2.5-flash"
    gemini_pro_model: str = "gemini-2.5-pro"
    hf_api_key: str = ""
    image_provider: str = "placeholder"
    image_model: str = "stable-diffusion-v1-5/stable-diffusion-v1-5"
    image_steps: int = 20
    image_width: int = 512
    image_height: int = 512
    image_guidance_scale: float = 7.5
    max_panels: int = 5
    model_config = SettingsConfigDict(
        env_file=BASE_DIR / ".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

settings = Settings()
