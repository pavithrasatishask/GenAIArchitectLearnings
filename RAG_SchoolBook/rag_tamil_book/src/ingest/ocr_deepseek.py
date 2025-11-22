# ingest/ocr_deepseek.py
"""
DeepSeek OCR client – supports:
- Image OCR
- Tamil OCR (default)
- Layout extraction (blocks, bounding boxes)
"""

import os
import requests
from dotenv import load_dotenv

load_dotenv()

# Load environment variables
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
DEEPSEEK_OCR_URL = os.getenv("DEEPSEEK_OCR_URL")

if not DEEPSEEK_API_KEY:
    raise RuntimeError("DEEPSEEK_API_KEY missing in .env")

if not DEEPSEEK_OCR_URL:
    raise RuntimeError("DEEPSEEK_OCR_URL missing in .env")

HEADERS = {
    "Authorization": f"Bearer {DEEPSEEK_API_KEY}"
}


def ocr_image_bytes(image_bytes, language="ta", return_layout=False):
    """
    Sends image bytes to DeepSeek OCR and returns extracted text or full layout.

    Args:
        image_bytes (bytes): Raw PNG/JPG bytes of the image
        language (str): Language code, default 'ta' (Tamil)
        return_layout (bool): Whether to return structured OCR blocks

    Returns:
        dict: OCR result JSON:
              {
                "text": "...",
                "blocks": [...]
              }
    """

    files = {
        "file": ("image.png", image_bytes, "image/png")
    }

    params = {
        "language": language
    }

    # Enable block-level layout extraction
    if return_layout:
        params["layout"] = "true"

    try:
        resp = requests.post(
            DEEPSEEK_OCR_URL,
            headers=HEADERS,
            files=files,
            params=params,
            timeout=120
        )
        resp.raise_for_status()
        return resp.json()

    except requests.exceptions.HTTPError as http_err:
        raise RuntimeError(f"DeepSeek OCR HTTP error: {http_err}")

    except Exception as e:
        raise RuntimeError(f"DeepSeek OCR request failed: {e}")


def ocr_file(path, language="ta", return_layout=False):
    """
    OCR an image file directly from disk.

    Args:
        path (str): Path to PNG/JPG file
    """
    with open(path, "rb") as f:
        raw = f.read()
    return ocr_image_bytes(raw, language=language, return_layout=return_layout)
