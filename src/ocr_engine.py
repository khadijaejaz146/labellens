
from functools import lru_cache
from PIL import Image
from paddleocr import PaddleOCR
import numpy as np


@lru_cache(maxsize=1)
def get_ocr_engine():
    """Load OCR once and reuse it during the app session."""
return PaddleOCR(
    use_angle_cls=False,
    lang="en",
    show_log=False
)


def extract_text(image: Image.Image) -> dict:
    """Extract visible text and return it with confidence scores."""

    image_array = np.array(image.convert("RGB"))
    engine = get_ocr_engine()

    result = engine.ocr(image_array, cls=True)

    lines = []
    scores = []

    if result and result[0]:
        for item in result[0]:
            text = item[1][0]
            confidence = float(item[1][1])

            lines.append(text)
            scores.append(confidence)

    extracted_text = "\n".join(lines)

    if not extracted_text.strip():
        return {
            "text": "",
            "average_confidence": 0.0,
            "warning": "No readable text was detected. Try a clearer image."
        }

    average_confidence = sum(scores) / len(scores)

    warning = None
    if average_confidence < 0.70:
        warning = (
            "Some text may be inaccurate. Please check the original "
            "package and try a clearer image."
        )

    return {
        "text": extracted_text,
        "average_confidence": round(average_confidence, 2),
        "warning": warning
    }
