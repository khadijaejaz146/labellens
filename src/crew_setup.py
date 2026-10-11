
import os
from groq import Groq
from src.tools import create_agent_tools


def analyze_label(
    extracted_text: str,
    confidence: float,
    memory_store: list
) -> str:
    """Organize and review packaging label text using Groq."""

    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise ValueError(
            "GROQ_API_KEY is missing. Add it to Streamlit Secrets."
        )

    client = Groq(api_key=api_key)
    tools = create_agent_tools(memory_store)

    tool_notes = []
    for tool in tools:
        if "Validate Extracted Label Text" in str(tool):
            try:
                tool_notes.append(tool.run(text=extracted_text))
            except Exception:
                pass

    validation_notes = "\n".join(tool_notes) or "No tool notes available."

    organizer_prompt = f"""
You organize packaging label text for accessibility.

Use only the OCR text below. Do not invent or complete missing words.
If a field cannot be found, write "Not detected in this image".
Preserve numbers, units, warnings, ingredients and instructions.
Keep the original extracted text in your output.

OCR TEXT:
{extracted_text}

OCR CONFIDENCE:
{confidence}

VALIDATION NOTES:
{validation_notes}
"""

    first = client.chat.completions.create(
        model="openai/gpt-oss-120b",
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a careful packaging-label organizer. "
                    "Never invent product information."
                )
            },
            {"role": "user", "content": organizer_prompt}
        ],
        temperature=0.1,
        max_completion_tokens=2048
    )

    organized_text = first.choices[0].message.content or ""

    review_prompt = f"""
Review the organized report against the original OCR text.

ORIGINAL OCR TEXT:
{extracted_text}

ORGANIZED REPORT:
{organized_text}

Identify unsupported claims, changed numbers or units, missing warnings,
and uncertainty. Correct the report without inventing information.
Do not claim the physical package has been verified.
Do not provide medical advice or invent dosage instructions.

End with a warning that the original package must be checked.
"""

    second = client.chat.completions.create(
        model="openai/gpt-oss-120b",
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a strict reviewer of packaging-label text. "
                    "Use only the supplied evidence."
                )
            },
            {"role": "user", "content": review_prompt}
        ],
        temperature=0.1,
        max_completion_tokens=2048
    )

    return second.choices[0].message.content or organized_text
