
from functools import lru_cache

import numpy as np
from PIL import Image
from paddleocr import PaddleOCR


@lru_cache(maxsize=1)
def get_ocr_engine():
    return PaddleOCR(
        use_angle_cls=False,
        lang="en",
        show_log=False
    )


def extract_text(image: Image.Image) -> dict:
    image_array = np.array(image.convert("RGB"))
    engine = get_ocr_engine()

    result = engine.ocr(image_array, cls=False)

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
            "warning": (
                "No readable text detected. "
                "Try a clearer, upright image."
            )
        }

    average_confidence = sum(scores) / len(scores)

    warning = None
    if average_confidence < 0.70:
        warning = (
            "Some text may be inaccurate. "
            "Check the original package."
        )

    return {
        "text": extracted_text,
        "average_confidence": round(average_confidence, 2),
        "warning": warning
    }
