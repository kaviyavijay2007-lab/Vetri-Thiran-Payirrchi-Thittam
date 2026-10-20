from __future__ import annotations
import hashlib
from pathlib import Path
from threading import Lock
from PIL import Image, ImageDraw, ImageFont
from app.config import BASE_DIR, settings

PIPELINE = None
PIPELINE_LOCK = Lock()

def create_filename(prompt: str, panel_number: int) -> str:
    digest = hashlib.sha256(prompt.encode("utf-8")).hexdigest()[:16]
    return f"panel_{panel_number}_{digest}.png"

def create_placeholder(prompt: str, panel_number: int, output_path: Path):
    image = Image.new("RGB", (settings.image_width, settings.image_height), "white")
    draw = ImageDraw.Draw(image)
    try:
        font = ImageFont.truetype("arial.ttf", 22)
    except Exception:
        font = ImageFont.load_default()
    draw.rectangle((15, 15, image.width - 15, image.height - 15), outline="black", width=4)
    draw.text((35, 35), f"ComicCraft Panel {panel_number}", fill="black", font=font)
    draw.multiline_text((35, 90), prompt[:600], fill="black", font=font, spacing=8)
    image.save(output_path)

def get_pipeline():
    global PIPELINE
    if PIPELINE is not None:
        return PIPELINE
    with PIPELINE_LOCK:
        if PIPELINE is not None:
            return PIPELINE
        import torch
        from diffusers import StableDiffusionPipeline
        dtype = torch.float16 if torch.cuda.is_available() else torch.float32
        kwargs = {"torch_dtype": dtype, "use_safetensors": True}
        if settings.hf_api_key:
            kwargs["token"] = settings.hf_api_key
        pipeline = StableDiffusionPipeline.from_pretrained(settings.image_model, **kwargs)
        pipeline = pipeline.to("cuda" if torch.cuda.is_available() else "cpu")
        if torch.cuda.is_available():
            try:
                pipeline.enable_attention_slicing()
            except Exception:
                pass
        PIPELINE = pipeline
    return PIPELINE

def generate_image(prompt: str, panel_number: int) -> str:
    output_dir = BASE_DIR / "static" / "panels"
    output_dir.mkdir(parents=True, exist_ok=True)
    filename = create_filename(prompt, panel_number)
    output_path = output_dir / filename

    if settings.image_provider.lower() == "placeholder":
        create_placeholder(prompt, panel_number, output_path)
        return f"/static/panels/{filename}"

    if settings.image_provider.lower() != "diffusers":
        raise RuntimeError("IMAGE_PROVIDER must be 'diffusers' or 'placeholder'.")

    pipeline = get_pipeline()
    result = pipeline(
        prompt=(
            "comic book illustration, high quality, detailed environment, "
            "expressive character, cinematic composition, consistent character "
            f"design, clean line art, {prompt}"
        ),
        negative_prompt=(
            "blurry, low quality, distorted face, bad anatomy, extra fingers, "
            "malformed hands, watermark, logo, text, letters"
        ),
        width=settings.image_width,
        height=settings.image_height,
        num_inference_steps=settings.image_steps,
        guidance_scale=settings.image_guidance_scale,
    )
    result.images[0].save(output_path)
    return f"/static/panels/{filename}"
