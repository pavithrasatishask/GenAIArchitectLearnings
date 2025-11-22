from sentence_transformers import SentenceTransformer
from PIL import Image
import numpy as np

class UnifiedEmbedder:

    def __init__(self, model_name="clip-ViT-B-32"):
        # loads once on startup
        self.model = SentenceTransformer(model_name)

    def embed_text(self, text: str):
        """Returns 512-dim embedding for text."""
        emb = self.model.encode(text, convert_to_numpy=True, normalize_embeddings=True)
        return emb.tolist()

    def embed_image(self, image_path: str):
        """Returns 512-dim embedding for image."""
        img = Image.open(image_path).convert("RGB")
        emb = self.model.encode(img, convert_to_numpy=True, normalize_embeddings=True)
        return emb.tolist()

    def embed_query(self, input_value):
        """
        Automatically detects: text string or image file path.
        Use this for unified handling.
        """
        if isinstance(input_value, str) and input_value.lower().endswith((".png", ".jpg", ".jpeg", ".webp")):
            return self.embed_image(input_value)
        else:
            return self.embed_text(input_value)
