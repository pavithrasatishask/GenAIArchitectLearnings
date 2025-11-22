# ingest/ocr_deepseek.py
import os
import requests
from dotenv import load_dotenv
from requests.adapters import HTTPAdapter, Retry

load_dotenv()

DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
DEEPSEEK_OCR_URL = os.getenv("DEEPSEEK_OCR_URL")

if not DEEPSEEK_API_KEY or not DEEPSEEK_OCR_URL:
    raise RuntimeError("DeepSeek OCR configuration missing in .env")

HEADERS = {"Authorization": f"Bearer {DEEPSEEK_API_KEY}"}

# Setup session with retries
session = requests.Session()
retries = Retry(total=3, backoff_factor=1, status_forcelist=[429, 500, 502, 503, 504])
session.mount("https://", HTTPAdapter(max_retries=retries))

def ocr_image_bytes(image_bytes: bytes, language: str = "ta", return_layout: bool = True, timeout: int = 120):
    """
    Send image bytes to DeepSeek OCR endpoint and return JSON with:
      - text: full extracted plain text
      - blocks: optional structured blocks (each with text, bbox, confidence)
    """
    files = {"file": ("image.png", image_bytes, "image/png")}
    params = {"language": language, "layout": "true" if return_layout else "false"}

    resp = session.post(DEEPSEEK_OCR_URL, headers=HEADERS, files=files, params=params, timeout=timeout)
    resp.raise_for_status()
    data = resp.json()

    # Basic normalization: ensure keys exist
    text = data.get("text") or ""
    blocks = data.get("blocks") or []
    # Some implementations include confidence per block; preserve them
    return {"text": text, "blocks": blocks, "raw": data}
