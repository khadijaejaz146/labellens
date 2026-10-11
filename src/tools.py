
from crewai.tools import tool


def create_agent_tools(memory_store: list):
    """Create tools connected to this user's session memory."""

    @tool("Recall LabelLens Session Memory")
    def recall_memory(query: str) -> str:
        """Recall relevant notes from the current user's session.
        Use this for previous context or accessibility preferences.
        Do not use old label text as evidence for a new package.
        """
        if not memory_store:
            return "No previous session notes are available."

        return "\n".join(memory_store[-5:])

    @tool("Save LabelLens Session Memory")
    def save_memory(note: str) -> str:
        """Save a short, non-sensitive note for later in this session.
        Save useful accessibility preferences, not private label data.
        """
        note = note.strip()

        if not note:
            return "No note was saved."

        memory_store.append(note[:300])
        del memory_store[:-10]

        return "Note saved for this session."

    @tool("Validate Extracted Label Text")
    def validate_label_text(text: str) -> str:
        """Check extracted label text for obvious missing or uncertain
        information. Do not guess words or supply missing instructions.
        """
        if not text.strip():
            return "No text was supplied for validation."

        warnings = []

        if len(text.strip()) < 20:
            warnings.append(
                "Very little text was extracted. The image may be incomplete."
            )

        if "[uncertain]" in text.lower():
            warnings.append(
                "The extracted text contains an uncertainty marker."
            )

        if not warnings:
            warnings.append(
                "No obvious text-length issue was detected. "
                "This does not prove that OCR is accurate."
            )

        return "\n".join(warnings)

    return [recall_memory, save_memory, validate_label_text]
