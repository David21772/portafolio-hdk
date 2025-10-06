# Presentación: "Alimentos que deben consumirse para sentirse feliz"

Este proyecto genera una presentación de 7 diapositivas con estilo oscuro (títulos en naranja, acentos verdes) y una imagen relacionada en cada diapositiva. El archivo se exporta a `.pptx` y, si está disponible LibreOffice, también a `.pdf`.

## Requisitos
- Python 3.9+
- Paquetes: `python-pptx`, `requests`, `Pillow`
- (Opcional local) LibreOffice para exportar a PDF

Instalación de dependencias:
```bash
pip install -r presentations/alimentos-felicidad/requirements.txt
```

## Uso local
```bash
python presentations/alimentos-felicidad/generate_presentation.py --author "David21772" --output "presentations/alimentos-felicidad/alimentos-felicidad.pptx" --export-pdf
```

## Workflow de GitHub Actions
- Ejecuta la generación automáticamente (manual o en cada cambio) y **commitea** los archivos `.pptx` y `.pdf` al repositorio, en `presentations/alimentos-felicidad/`.
- También publica ambos archivos como artefactos del workflow para descarga rápida.