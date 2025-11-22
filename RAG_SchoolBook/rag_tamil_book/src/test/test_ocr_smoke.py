# tests/test_ocr_smoke.py

import sys, os

# Add src/ to Python path so imports work
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC_DIR = os.path.join(BASE_DIR, "src")
sys.path.insert(0, SRC_DIR)

from ingest.ocr_deepseek import ocr_image_bytes
from PIL import Image
import io

def test_ocr_sample():
    img = Image.open("tests/samples/tamil_clear.png")
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    res = ocr_image_bytes(buf.getvalue(), language="ta")
    assert len(res["text"]) > 20
    assert isinstance(res["blocks"], list)
