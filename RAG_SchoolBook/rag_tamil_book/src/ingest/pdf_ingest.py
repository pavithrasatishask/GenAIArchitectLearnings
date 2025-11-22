# ingest/pdf_ingest.py
import pdfplumber
from io import BytesIO
from PIL import Image
import unicodedata
from ingest.ocr_deepseek import ocr_image_bytes


def normalize_text(text):
    """Normalize text (Tamil-safe) and strip whitespace."""
    if not text:
        return ""
    return unicodedata.normalize("NFKC", text).strip()


def image_from_page(page, img_dict):
    """
    Extract a PDF-embedded image using its bbox.
    Returns: (image_bytes, bbox) or (None, None)
    """
    bbox = (img_dict["x0"], img_dict["top"], img_dict["x1"], img_dict["bottom"])
    try:
        # Render only the region inside the bounding box
        cropped_img = page.within_bbox(bbox).to_image(resolution=300).original
        buf = BytesIO()
        cropped_img.save(buf, format="PNG")
        return buf.getvalue(), bbox
    except Exception:
        return None, None


def extract_full_page_ocr(page, ocr_language="ta"):
    """
    OCR for full page — used when there is NO selectable text.
    Returns: (text, blocks)
    """
    try:
        page_img = page.to_image(resolution=300).original
        buf = BytesIO()
        page_img.save(buf, format="PNG")
        image_bytes = buf.getvalue()

        ocr_res = ocr_image_bytes(image_bytes, language=ocr_language, return_layout=True)
        text = normalize_text(ocr_res.get("text", ""))
        blocks = ocr_res.get("blocks", [])

        return text, blocks
    except Exception:
        return "", []


def extract_pages(pdf_path, ocr_language="ta"):
    """
    Extract text + OCR from a PDF.

    Returns a list:
    [
      {
        "page": 1,
        "text": "...",
        "blocks": [...],    # OCR layout blocks (full-page or per-image)
        "images": [
            {
                "bbox": (x0, top, x1, bottom),
                "ocr": {...}   # DeepSeek OCR output
            }
        ]
      }
    ]
    """

    pages_output = []

    with pdfplumber.open(pdf_path) as pdf:
        for idx, page in enumerate(pdf.pages, start=1):

            # 1️⃣ Try extracting text directly (for digital PDFs)
            selectable_text = normalize_text(page.extract_text() or "")

            # 2️⃣ If no text → scanned page → OCR whole page
            if not selectable_text.strip():
                full_text, blocks = extract_full_page_ocr(page, ocr_language)

                pages_output.append({
                    "page": idx,
                    "text": full_text,
                    "blocks": blocks,
                    "images": []
                })
                continue

            # 3️⃣ If text exists → also extract embedded images
            images_info = []

            for img_dict in page.images:
                img_bytes, bbox = image_from_page(page, img_dict)

                if img_bytes:
                    try:
                        ocr_res = ocr_image_bytes(img_bytes, language=ocr_language, return_layout=True)
                        images_info.append({
                            "bbox": bbox,
                            "ocr": ocr_res
                        })
                    except Exception as e:
                        images_info.append({
                            "bbox": bbox,
                            "error": str(e)
                        })

            # Combine
            pages_output.append({
                "page": idx,
                "text": selectable_text,
                "blocks": [],       # only used in full-page OCR mode
                "images": images_info
            })

    return pages_output
