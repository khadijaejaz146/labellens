
import os

from crewai import Agent, Task, Crew, Process, LLM

from src.tools import create_agent_tools


def analyze_label(
    extracted_text: str,
    confidence: float,
    memory_store: list
) -> str:
    """Run the LabelLens CrewAI workflow."""

    api_key = os.getenv("GROQ_API_KEY")

    if not api_key:
        raise ValueError(
            "GROQ_API_KEY is missing. Add it to Streamlit Secrets."
        )

    llm = LLM(
        model="groq/openai/gpt-oss-120b",
        api_key=api_key,
        temperature=0.1
    )

    agent_tools = create_agent_tools(memory_store)

    organizer = Agent(
        role="Packaging Label Information Organizer",
        goal=(
            "Organize only the text provided by OCR into clear "
            "packaging label sections."
        ),
        backstory=(
            "You help people read small packaging labels. "
            "You never invent missing text, warnings, ingredients, "
            "dosage instructions, or expiry dates."
        ),
        llm=llm,
        tools=agent_tools,
        allow_delegation=False,
        verbose=False
    )

    reviewer = Agent(
        role="Accessibility and Text Verification Reviewer",
        goal=(
            "Review the organized output against the original OCR text "
            "and identify uncertainty or unsupported claims."
        ),
        backstory=(
            "You are careful with packaging information. "
            "You distinguish information that was not detected from "
            "information that is absent from the actual package."
        ),
        llm=llm,
        tools=agent_tools,
        allow_delegation=False,
        verbose=False
    )

    organize_task = Task(
        description="""
        Organize the following OCR text into suitable sections, such as:
        - Product name
        - Ingredients
        - Directions
        - Warnings
        - Storage
        - Expiry or batch details
        - Other detected information

        OCR TEXT:
        {extracted_text}

        OCR AVERAGE CONFIDENCE:
        {confidence}

        Previous session memory may help with accessibility preferences.
        It must not be used as evidence about this package.

        Rules:
        1. Preserve the meaning and wording of the source.
        2. Do not invent information or complete missing words.
        3. If a field cannot be found, say "Not detected in this image".
        4. Clearly label any AI-generated organization or summary.
        5. Retain a section for the original extracted text.
        """,
        expected_output=(
            "Readable sections of extracted label information, "
            "with missing or uncertain fields clearly identified."
        ),
        agent=organizer
    )

    review_task = Task(
        description="""
        Review the organizer's output against the original OCR text.

        ORIGINAL OCR TEXT:
        {extracted_text}

        Check for:
        - Information that is not supported by the OCR text
        - Changed numbers, units, warnings, or instructions
        - Missing uncertainty warnings
        - Fields incorrectly described as absent from the package

        Use the validation tool when useful.
        Do not claim that the physical package has been verified.
        Do not provide medical advice or invent dosage instructions.

        Return a corrected, user-friendly report and a clear warning
        that OCR output must be checked against the original image.
        """,
        expected_output=(
            "A checked label report with uncertainty and verification warnings."
        ),
        agent=reviewer
    )

    crew = Crew(
        agents=[organizer, reviewer],
        tasks=[organize_task, review_task],
        process=Process.sequential,
        memory=False,
        verbose=False
    )

    result = crew.kickoff(
        inputs={
            "extracted_text": extracted_text,
            "confidence": confidence
        }
    )

    return str(result)
