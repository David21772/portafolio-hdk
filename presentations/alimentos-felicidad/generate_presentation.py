import argparse
import os
import re
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import List, Optional
import requests
from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import PP_ALIGN
from pptx.util import Inches, Pt

DARK_BG = RGBColor(28, 44, 56)       # azul grisáceo oscuro
ACCENT_GREEN = RGBColor(46, 204, 113)
ACCENT_GREEN_2 = RGBColor(39, 174, 96)
ORANGE_TITLE = RGBColor(255, 140, 0)
WHITE = RGBColor(245, 245, 245)
GRAY_PLACEHOLDER = RGBColor(90, 98, 104)

def _set_slide_background(slide):
    fill = slide.background.fill
    fill.solid()
    fill.fore_color.rgb = DARK_BG

    shapes = slide.shapes

    tri_left = shapes.add_shape(
        MSO_SHAPE.RIGHT_TRIANGLE,
        Inches(-1.0), Inches(0.0), Inches(3.5), Inches(7.5)
    )
    tri_left.fill.solid()
    tri_left.fill.fore_color.rgb = ACCENT_GREEN
    tri_left.line.fill.background()

    tri_right = shapes.add_shape(
        MSO_SHAPE.RIGHT_TRIANGLE,
        Inches(11.2), Inches(-0.2), Inches(3.5), Inches(7.9)
    )
    tri_right.rotation = 180
    tri_right.fill.solid()
    tri_right.fill.fore_color.rgb = ACCENT_GREEN_2
    tri_right.line.fill.background()

def _add_title(slide, title: str, subtitle: Optional[str] = None):
    tx = slide.shapes.add_textbox(Inches(0.8), Inches(0.4), Inches(10.8), Inches(1.2))
    tf = tx.text_frame
    tf.clear()
    p = tf.paragraphs[0]
    run = p.add_run()
    run.text = title
    run.font.bold = True
    run.font.size = Pt(40)
    run.font.color.rgb = ORANGE_TITLE
    p.alignment = PP_ALIGN.CENTER

    if subtitle:
        sub = slide.shapes.add_textbox(Inches(0.8), Inches(1.3), Inches(10.8), Inches(0.7))
        stf = sub.text_frame
        stf.clear()
        sp = stf.paragraphs[0]
        srun = sp.add_run()
        srun.text = subtitle
        srun.font.size = Pt(22)
        srun.font.color.rgb = ACCENT_GREEN
        sp.alignment = PP_ALIGN.CENTER

def _add_bullets(slide, bullets: List[str]):
    box = slide.shapes.add_textbox(Inches(0.8), Inches(2.0), Inches(6.8), Inches(4.6))
    tf = box.text_frame
    tf.word_wrap = True
    tf.clear()

    for i, text in enumerate(bullets):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.text = text
        p.level = 0
        p.font.size = Pt(21)
        p.font.color.rgb = WHITE
        p.space_after = Pt(8)

def _safe_filename_from_url(url: str) -> str:
    name = url.split("?")[0].split("/")[-1]
    name = re.sub(r"[^A-Za-z0-9._-]", "_", name)
    if not os.path.splitext(name)[1]:
        name += ".jpg"
    return name

def _download_image(url: str, tmpdir: Path) -> Optional[Path]:
    try:
        if os.path.exists(url):
            return Path(url)
        headers = {"User-Agent": "Mozilla/5.0 (compatible; pptx-generator/1.0)"}
        with requests.get(url, headers=headers, stream=True, timeout=20) as r:
            r.raise_for_status()
            fname = _safe_filename_from_url(url)
            fpath = tmpdir / fname
            with open(fpath, "wb") as f:
                for chunk in r.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
            return fpath
    except Exception:
        return None

def _add_image_or_placeholder(slide, image_path: Optional[Path]):
    left, top, width = Inches(7.8), Inches(2.0), Inches(4.4)
    if image_path and image_path.exists():
        try:
            slide.shapes.add_picture(str(image_path), left, top, width=width)
            return
        except Exception:
            pass

    rect = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, left, top, width, Inches(3.6))
    rect.fill.solid()
    rect.fill.fore_color.rgb = GRAY_PLACEHOLDER
    rect.line.fill.background()
    tf = rect.text_frame
    tf.clear()
    p = tf.paragraphs[0]
    run = p.add_run()
    run.text = "Imagen no disponible"
    run.font.size = Pt(20)
    run.font.color.rgb = WHITE
    p.alignment = PP_ALIGN.CENTER

def create_presentation(author: str, output_path: Path) -> Path:
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)

    slides = [
        {
            "title": "Alimentos que deben consumirse para sentirse feliz",
            "subtitle": f"Guía práctica basada en evidencia • Autor: {author}",
            "bullets": [
                "La alimentación influye en neurotransmisores, inflamación, energía y microbiota, factores clave para el estado de ánimo.",
                "Incluir ciertos alimentos de forma regular puede favorecer la producción de serotonina y dopamina, y reducir el estrés oxidativo.",
                "Objetivo: propuestas concretas, porciones sugeridas y consejos prácticos para el día a día."
            ],
            "image_url": "https://upload.wikimedia.org/wikipedia/commons/1/15/Strawberries.jpg"
        },
        {
            "title": "Chocolate negro (≥ 70% cacao)",
            "subtitle": "Polifenoles, magnesio y precursores de serotonina",
            "bullets": [
                "El cacao aporta flavonoides que mejoran la vasodilatación y podrían modular la respuesta al estrés.",
                "Contiene triptófano y feniletilamina, asociados a sensación de bienestar (consumo moderado).",
                "Sugerencia: 1–2 onzas (30–40 g) al día, eligiendo opciones con poco azúcar y sin rellenos.",
                "Evitar versiones ultraprocesadas con grasas añadidas o jarabes."
            ],
            "image_url": "https://upload.wikimedia.org/wikipedia/commons/7/70/Chocolate_%28blue_background%29.jpg"
        },
        {
            "title": "Pescados grasos (omega‑3)",
            "subtitle": "Salmón, sardina, caballa, atún claro",
            "bullets": [
                "Los ácidos grasos EPA y DHA participan en la estructura neuronal y la señalización sináptica.",
                "Un mejor balance omega‑3/omega‑6 se asocia a menor inflamación sistémica.",
                "Sugerencia: 2–3 porciones por semana; alternativa vegetal: chía, linaza y nueces (ALA).",
                "Preferir preparaciones al horno o a la plancha para conservar nutrientes."
            ],
            "image_url": "https://upload.wikimedia.org/wikipedia/commons/3/3a/Salmon_Sashimi.jpg"
        },
        {
            "title": "Fermentados y probióticos",
            "subtitle": "Eje intestino‑cerebro",
            "bullets": [
                "Yogur, kéfir, kimchi y chucrut aportan microorganismos beneficiosos para la microbiota.",
                "Una microbiota diversa produce metabolitos (ej. ácidos grasos de cadena corta) con efectos neuromoduladores.",
                "Evidencia emergente: menor ansiedad y mejor manejo del estrés cuando se combinan con fibra prebiótica.",
                "Sugerencia: 1 ración diaria; vigilar azúcares añadidos en yogures saborizados."
            ],
            "image_url": "https://upload.wikimedia.org/wikipedia/commons/0/02/Kimchi.jpg"
        },
        {
            "title": "Frutas y verduras coloridas",
            "subtitle": "Antioxidantes, folato y vitamina C",
            "bullets": [
                "Bayas, cítricos, espinaca y brócoli ayudan a combatir el estrés oxidativo y la inflamación.",
                "El folato se asocia con mejor función cognitiva y síntesis de neurotransmisores.",
                "Sugerencia: al menos 5 porciones al día variando colores (rojo, morado, verde, naranja).",
                "Preferir frescas o al vapor para conservar vitaminas termo‑sensibles."
            ],
            "image_url": "https://upload.wikimedia.org/wikipedia/commons/0/0b/Blueberries.jpg"
        },
        {
            "title": "Cereales integrales y legumbres",
            "subtitle": "Energía estable y saciedad",
            "bullets": [
                "Avena, quinoa, lentejas y garbanzos aportan fibra que estabiliza la glucosa en sangre.",
                "Los picos glucémicos se asocian con cambios de humor; mantener energía constante favorece el equilibrio emocional.",
                "Sugerencia: incluir al menos una porción en cada comida principal (½ taza cocida).",
                "Combinar con proteínas magras para optimizar absorción y saciedad."
            ],
            "image_url": "https://upload.wikimedia.org/wikipedia/commons/4/4a/Quinoa.jpg"
        },
        {
            "title": "Resumen y recomendaciones finales",
            "subtitle": "Implementación práctica",
            "bullets": [
                "Combinar estos alimentos en un patrón alimentario equilibrado, sin obsesionarse con uno solo.",
                "La constancia es más importante que la perfección: pequeños cambios sostenibles generan mayor impacto.",
                "Considerar factores individuales: alergias, preferencias culturales y presupuesto disponible.",
                "Recordar que la alimentación es solo una parte: ejercicio, sueño y apoyo social también influyen en el bienestar."
            ],
            "image_url": "https://upload.wikimedia.org/wikipedia/commons/6/64/Foods_%28cropped%29.jpg"
        }
    ]

    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir_path = Path(tmpdir)
        
        for slide_data in slides:
            slide_layout = prs.slide_layouts[6]  # blank layout
            slide = prs.slides.add_slide(slide_layout)
            
            _set_slide_background(slide)
            _add_title(slide, slide_data["title"], slide_data.get("subtitle"))
            _add_bullets(slide, slide_data["bullets"])
            
            image_path = None
            if "image_url" in slide_data:
                image_path = _download_image(slide_data["image_url"], tmpdir_path)
            
            _add_image_or_placeholder(slide, image_path)

    prs.save(str(output_path))
    return output_path

def export_to_pdf(pptx_path: Path, pdf_path: Path) -> bool:
    """Export PPTX to PDF using LibreOffice if available."""
    try:
        result = subprocess.run([
            "libreoffice", "--headless", "--convert-to", "pdf",
            "--outdir", str(pdf_path.parent), str(pptx_path)
        ], capture_output=True, text=True, timeout=60)
        
        if result.returncode == 0:
            # LibreOffice creates file with same name but .pdf extension
            generated_pdf = pdf_path.parent / f"{pptx_path.stem}.pdf"
            if generated_pdf.exists() and generated_pdf != pdf_path:
                generated_pdf.rename(pdf_path)
            return pdf_path.exists()
        else:
            print(f"LibreOffice conversion failed: {result.stderr}")
            return False
    except (subprocess.TimeoutExpired, FileNotFoundError) as e:
        print(f"PDF export failed: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description="Generate happiness foods presentation")
    parser.add_argument("--author", default="Autor", help="Author name for the presentation")
    parser.add_argument("--output", default="alimentos-felicidad.pptx", help="Output PPTX file path")
    parser.add_argument("--export-pdf", action="store_true", help="Also export to PDF (requires LibreOffice)")
    
    args = parser.parse_args()
    
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    print(f"Creating presentation: {output_path}")
    create_presentation(args.author, output_path)
    print(f"PPTX created successfully: {output_path}")
    
    if args.export_pdf:
        pdf_path = output_path.with_suffix('.pdf')
        print(f"Exporting to PDF: {pdf_path}")
        if export_to_pdf(output_path, pdf_path):
            print(f"PDF created successfully: {pdf_path}")
        else:
            print("PDF export failed (LibreOffice may not be available)")
    
    print("Presentation generation completed!")

if __name__ == "__main__":
    main()