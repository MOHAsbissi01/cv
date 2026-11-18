"""Render scripts/og-template.html to site/assets/images/og.png (1200x630).

Requires: pip install playwright pillow && playwright install chromium
Run from the repo root:  python scripts/make_og.py
"""
from pathlib import Path
from playwright.sync_api import sync_playwright
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "site" / "assets" / "images" / "og.png"

with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page(viewport={"width": 1200, "height": 630})
    page.goto((ROOT / "scripts" / "og-template.html").as_uri())
    page.screenshot(path=str(OUT))
    browser.close()

# Quantise to a small palette PNG: keeps the file well under 100 KB.
Image.open(OUT).convert("RGB").quantize(colors=96, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE).save(OUT, optimize=True)
print("wrote", OUT, OUT.stat().st_size, "bytes")
