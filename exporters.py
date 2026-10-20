from __future__ import annotations
import re
from datetime import datetime
from pathlib import Path
from urllib.parse import urlparse
from fpdf import FPDF
from app.config import BASE_DIR
from app.schemas import ComicLayout

def get_image_path(image_url: str) -> Path:
    parsed = urlparse(image_url)
    relative_path = parsed.path.lstrip("/")
    if not relative_path.startswith("static/"):
        raise ValueError("Invalid image path.")
    path = (BASE_DIR / relative_path).resolve()
    static_dir = (BASE_DIR / "static").resolve()
    if static_dir not in path.parents:
        raise ValueError("Image path is outside static directory.")
    return path

def pdf_text(text: str) -> str:
    return text.encode("latin-1", "replace").decode("latin-1")

def save_pdf(layout: list[ComicLayout], title: str = "ComicCraft Comic") -> str:
    export_dir = BASE_DIR / "static" / "exports"
    export_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_title = re.sub(r"[^a-zA-Z0-9_-]+", "_", title).strip("_") or "comic"
    output_path = export_dir / f"{safe_title}_{timestamp}.pdf"

    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)

    for panel in layout:
        pdf.add_page()
        pdf.set_font("Helvetica", "B", 18)
        pdf.multi_cell(0, 10, pdf_text(f"Panel {panel.panel_number}: {panel.title}"))
        image_path = get_image_path(panel.image_url)

        if image_path.exists():
            pdf.image(str(image_path), x=15, y=35, w=180)
            pdf.ln(105)
        else:
            pdf.ln(10)
            pdf.set_font("Helvetica", "", 11)
            pdf.multi_cell(0, 7, "[Image unavailable]")

        for label, content in [
            ("Scene", panel.scene_description),
            ("Caption", panel.caption),
            ("Narration", panel.narration),
            ("Dialogue", panel.dialogue),
        ]:
            pdf.set_font("Helvetica", "B", 11)
            pdf.multi_cell(0, 7, pdf_text(label))
            pdf.set_font("Helvetica", "", 10)
            pdf.multi_cell(0, 6, pdf_text(content or "-"))
            pdf.ln(2)

    pdf.output(str(output_path))
    return f"/static/exports/{output_path.name}"
