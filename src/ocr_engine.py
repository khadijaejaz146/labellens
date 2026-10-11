
import base64
import io
import os

from groq import Groq
from PIL import Image


def extract_text(image: Image.Image) -> dict:
    api_key = os.getenv("GROQ_API_KEY")

    if not api_key:
        raise ValueError("GROQ_API_KEY is missing from Streamlit Secrets.")

    buffer = io.BytesIO()
    image.convert("RGB").save(buffer, format="JPEG")
    encoded = base64.b64encode(buffer.getvalue()).decode("utf-8")

    client = Groq(api_key=api_key)

    response = client.chat.completions.create(
        model="qwen/qwen3.8-27b",
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": (
                            "Extract all visible text from this package image. "
                            "Preserve wording, numbers, and units. Mark unreadable "
                            "words as [uncertain]. Never guess missing text."
                        ),
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{encoded}"
                        },
                    },
                ],
            }
        ],
        temperature=0,
        max_completion_tokens=2048,
    )

    text = response.choices[0].message.content or ""

    return {
        "text": text.strip(),
        "average_confidence": None,
        "warning": (
            "AI-extracted text may contain errors. "
            "Verify important details against the original package."
        ),
    }
