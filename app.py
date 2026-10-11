
import streamlit as st
from PIL import Image
from io import BytesIO

from src.ocr_engine import extract_text
from src.crew_setup import analyze_label


# --------------------------------------------------
# PAGE CONFIGURATION
# --------------------------------------------------

st.set_page_config(
    page_title="LabelLens | Accessible Packaging",
    page_icon=None,
    layout="wide",
    initial_sidebar_state="expanded",
)


# --------------------------------------------------
# SESSION STATE
# --------------------------------------------------

defaults = {
    "label_memory": [],
    "last_report": "",
    "last_ocr_text": "",
    "last_warning": "",
    "last_confidence": None,
    "last_image_id": "",
}

for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value


# --------------------------------------------------
# ACCESSIBILITY SETTINGS
# --------------------------------------------------

with st.sidebar:
    st.markdown("## LabelLens")
    st.caption("Packaging accessibility assistant")
    st.divider()

    st.markdown("### Reading preferences")

    font_size = st.slider(
        "Text size",
        min_value=16,
        max_value=32,
        value=20,
        step=2,
    )

    high_contrast = st.toggle(
        "High-contrast dark mode",
        value=False,
    )

    st.divider()

    st.markdown("### Session")
    st.write(
        f"Saved session notes: {len(st.session_state.label_memory)}"
    )

    if st.button(
        "Clear session data",
        use_container_width=True,
    ):
        st.session_state.label_memory = []
        st.session_state.last_report = ""
        st.session_state.last_ocr_text = ""
        st.session_state.last_warning = ""
        st.session_state.last_confidence = None
        st.session_state.last_image_id = ""
        st.rerun()

    st.divider()

    st.caption(
        "Privacy: avoid uploading images containing personal "
        "information. Uploaded images are sent to the configured "
        "AI provider for analysis."
    )


# --------------------------------------------------
# THEME COLORS
# --------------------------------------------------

if high_contrast:
    background = "#10141D"
    foreground = "#F9FAFB"
    panel = "#1B2332"
    muted = "#D1D9E6"
    border = "#596579"
    accent = "#7DB4FF"
    input_background = "#111827"
    button_text = "#10141D"
    secondary_background = "#253147"
else:
    background = "#F4F7FC"
    foreground = "#172033"
    panel = "#FFFFFF"
    muted = "#475467"
    border = "#D3DCE9"
    accent = "#2855D9"
    input_background = "#FFFFFF"
    button_text = "#FFFFFF"
    secondary_background = "#FFFFFF"


# --------------------------------------------------
# CUSTOM DESIGN AND ACCESSIBLE CSS
# --------------------------------------------------

st.markdown(
    f"""
    <style>
    :root {{
        color-scheme: {"dark" if high_contrast else "light"};
    }}

    .stApp,
    [data-testid="stAppViewContainer"],
    [data-testid="stMain"] {{
        background-color: {background} !important;
        color: {foreground} !important;
    }}

    [data-testid="stHeader"] {{
        background-color: {background} !important;
    }}

    [data-testid="stSidebar"] {{
        background-color: {panel} !important;
        border-right: 1px solid {border};
    }}

    [data-testid="stSidebar"] > div {{
        background-color: {panel} !important;
    }}

    .block-container {{
        max-width: 1250px;
        padding-top: 2rem;
        padding-bottom: 3rem;
    }}

    /* General text */
    .stApp p,
    .stApp li,
    .stApp label,
    .stApp h1,
    .stApp h2,
    .stApp h3,
    .stApp h4,
    .stApp [data-testid="stMarkdownContainer"],
    .stApp [data-testid="stCaptionContainer"],
    .stApp [data-testid="stWidgetLabel"] {{
        color: {foreground};
    }}

    .stApp [data-testid="stCaptionContainer"] p {{
        color: {muted} !important;
    }}

    /* Header panel */
    .hero {{
        padding: 1.8rem;
        border-radius: 18px;
        background-color: {panel};
        border: 1px solid {border};
        margin-bottom: 1.5rem;
    }}

    .hero .eyebrow {{
        color: {accent} !important;
        text-transform: uppercase;
        font-size: 0.78rem;
        letter-spacing: 1.5px;
        font-weight: 700;
    }}

    .hero h1 {{
        color: {foreground} !important;
        font-size: 2.5rem;
        line-height: 1.2;
        margin: 0.6rem 0;
    }}

    .hero p {{
        color: {muted} !important;
        font-size: 1.05rem;
        margin-bottom: 0;
    }}

    /* Cards and containers */
    [data-testid="stVerticalBlockBorderWrapper"] {{
        background-color: {panel} !important;
        border: 1px solid {border} !important;
        border-radius: 14px;
    }}

    /* Text inputs, text areas and select boxes */
    .stApp input,
    .stApp textarea,
    .stApp [data-baseweb="select"] > div {{
        background-color: {input_background} !important;
        color: {foreground} !important;
        border-color: {border} !important;
        -webkit-text-fill-color: {foreground} !important;
    }}

    .stApp input::placeholder,
    .stApp textarea::placeholder {{
        color: {muted} !important;
        opacity: 1;
    }}

    /* Disabled text areas remain readable */
    .stApp textarea:disabled {{
        opacity: 1 !important;
        -webkit-text-fill-color: {foreground} !important;
    }}

    /* Primary buttons */
    .stApp div.stButton > button[kind="primary"] {{
        background-color: {accent} !important;
        color: {button_text} !important;
        border: 1px solid {accent} !important;
        border-radius: 9px;
        min-height: 3rem;
        font-weight: 650;
    }}

    /* Secondary and download buttons */
    .stApp div.stButton > button,
    .stApp div.stDownloadButton > button {{
        background-color: {secondary_background} !important;
        color: {foreground} !important;
        border: 1px solid {border} !important;
        border-radius: 9px;
        min-height: 2.5rem;
    }}

    .stApp div.stButton > button p,
    .stApp div.stDownloadButton > button p {{
        color: inherit !important;
    }}

    /* Tabs */
    .stApp [data-testid="stTabs"] button {{
        color: {foreground} !important;
    }}

    .stApp [data-testid="stTabs"] button[aria-selected="true"] {{
        color: {accent} !important;
        border-bottom-color: {accent} !important;
    }}

    /* File upload area */
    [data-testid="stFileUploader"] {{
        background-color: {panel} !important;
        border-radius: 12px;
    }}

    [data-testid="stFileUploader"] section {{
        background-color: {panel} !important;
        border-color: {border} !important;
    }}

    [data-testid="stFileUploader"] button {{
        background-color: {secondary_background} !important;
        color: {foreground} !important;
        border-color: {border} !important;
    }}

    /* Alerts and status messages */
    [data-testid="stAlert"] {{
        background-color: {panel} !important;
        border: 1px solid {border} !important;
        color: {foreground} !important;
    }}

    [data-testid="stAlert"] p,
    [data-testid="stAlert"] span {{
        color: {foreground} !important;
    }}

    [data-testid="stStatusWidget"] {{
        background-color: {panel} !important;
        border-color: {border} !important;
        color: {foreground} !important;
    }}

    /* Slider and toggle labels */
    .stApp [data-testid="stSlider"] *,
    .stApp [data-testid="stToggle"] {{
        color: {foreground};
    }}

    /* Separators */
    .stApp hr {{
        border-color: {border} !important;
    }}

    /* Accessible text sizing */
    .stApp p,
    .stApp li,
    .stApp [data-testid="stMarkdownContainer"] {{
        font-size: max(1rem, {font_size}px);
        line-height: 1.65;
    }}

    .stApp [data-testid="stCaptionContainer"] p {{
        font-size: max(0.85rem, {font_size - 4}px);
    }}

    /* Keyboard focus */
    .stApp button:focus-visible,
    .stApp input:focus-visible,
    .stApp textarea:focus-visible {{
        outline: 3px solid {accent} !important;
        outline-offset: 2px !important;
    }}
    </style>
    """,
    unsafe_allow_html=True,
)


# --------------------------------------------------
# HEADER
# --------------------------------------------------

st.markdown(
    """
    <div class="hero">
        <div class="eyebrow">Accessible technology</div>
        <h1>Read every label with confidence.</h1>
        <p>
            Turn packaging photos into readable, organized text.
            Review uncertain information before relying on it.
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown("## Scan a package")

st.write(
    "Upload a clear photo of a household product or medicine label "
    "to get started."
)


# --------------------------------------------------
# IMAGE UPLOAD AND PREVIEW
# --------------------------------------------------

upload_col, preview_col = st.columns([1, 1], gap="large")

image = None

with upload_col:
    with st.container(border=True):
        st.markdown("### 1. Upload image")

        uploaded_file = st.file_uploader(
            "Choose a label photo",
            type=["png", "jpg", "jpeg"],
            help="Use a clear, well-lit, upright image.",
            label_visibility="visible",
        )

        st.caption(
            "Supported formats: PNG and JPEG. "
            "Avoid glare, blur, and cropped text."
        )

with preview_col:
    with st.container(border=True):
        st.markdown("### 2. Image preview")

        if uploaded_file is not None:
            try:
                image = Image.open(
                    BytesIO(uploaded_file.getvalue())
                ).convert("RGB")

                st.image(
                    image,
                    width="stretch",
                )

                st.caption(
                    f"Image dimensions: {image.width} × {image.height}"
                )

            except Exception:
                st.error("This image could not be opened.")
        else:
            st.info(
                "Your package preview will appear here after you upload "
                "an image."
            )


# --------------------------------------------------
# ANALYSIS
# --------------------------------------------------

if uploaded_file is not None and image is not None:
    image_id = uploaded_file.getvalue().hex()[:100]

    if image_id != st.session_state.last_image_id:
        st.session_state.last_report = ""
        st.session_state.last_ocr_text = ""
        st.session_state.last_warning = ""
        st.session_state.last_confidence = None

    if st.button(
        "Extract and analyze label",
        type="primary",
        use_container_width=True,
    ):
        try:
            with st.status(
                "Analyzing your label...",
                expanded=True,
            ) as status:
                st.write("Reading text from the image...")

                ocr_result = extract_text(image)
                extracted_text = ocr_result.get("text", "")
                confidence = ocr_result.get("average_confidence")
                warning = ocr_result.get("warning") or ""

                if not extracted_text.strip():
                    status.update(
                        label="No readable text found",
                        state="error",
                    )
                    st.session_state.last_ocr_text = ""
                    st.session_state.last_report = ""
                    st.session_state.last_warning = (
                        warning or "Try uploading a clearer image."
                    )
                    st.stop()

                st.write("Organizing and reviewing extracted text...")

                report = analyze_label(
                    extracted_text=extracted_text,
                    confidence=(
                        confidence if confidence is not None else 0
                    ),
                    memory_store=st.session_state.label_memory,
                )

                st.session_state.last_ocr_text = extracted_text
                st.session_state.last_report = report
                st.session_state.last_warning = warning
                st.session_state.last_confidence = confidence
                st.session_state.last_image_id = image_id

                status.update(
                    label="Analysis complete",
                    state="complete",
                    expanded=False,
                )

        except Exception as exc:
            st.error(
                "Analysis failed. Please check the app logs for details."
            )
            st.caption(f"Technical detail: {type(exc).__name__}: {exc}")

    if st.session_state.last_warning:
        st.warning(st.session_state.last_warning)


# --------------------------------------------------
# RESULTS
# --------------------------------------------------

if st.session_state.last_ocr_text:
    st.divider()
    st.markdown("## Your label results")

    text_tab, report_tab, image_tab = st.tabs(
        [
            "Extracted text",
            "Organized report",
            "Original image",
        ]
    )

    with text_tab:
        st.markdown("### Extracted packaging text")

        st.caption(
            "This is the text returned by the image-reading model. "
            "Check it against the original package."
        )

        st.text_area(
            "Extracted text",
            value=st.session_state.last_ocr_text,
            height=350,
            disabled=True,
            label_visibility="collapsed",
        )

        if st.session_state.last_confidence is not None:
            st.caption(
                "OCR confidence estimate: "
                f"{st.session_state.last_confidence:.0%}"
            )
        else:
            st.caption("Extraction method: Groq vision AI")

        st.download_button(
            "Download extracted text",
            data=st.session_state.last_ocr_text,
            file_name="labellens_extracted_text.txt",
            mime="text/plain",
            use_container_width=True,
        )

    with report_tab:
        st.markdown("### AI-organized label information")

        st.warning(
            "AI can misread numbers, ingredients, and warnings. "
            "Verify important information against the original package."
        )

        st.markdown(st.session_state.last_report)

        st.download_button(
            "Download analysis report",
            data=st.session_state.last_report,
            file_name="labellens_report.txt",
            mime="text/plain",
            use_container_width=True,
        )

    with image_tab:
        st.markdown("### Compare with original")

        st.image(
            image,
            caption="Original uploaded package image",
            width="stretch",
        )

    st.divider()
    st.markdown("### Accessible reading view")

    st.caption(
        "Use this larger text view to make the extracted label easier "
        "to read. It does not correct OCR mistakes."
    )

    st.text_area(
        "Large text",
        value=st.session_state.last_ocr_text,
        height=300,
        disabled=True,
        label_visibility="collapsed",
        key="accessible_reading_view",
    )

    st.download_button(
        "Save complete report",
        data=(
            "LABELLENS — EXTRACTED TEXT\n\n"
            + st.session_state.last_ocr_text
            + "\n\nAI-ORGANIZED REPORT\n\n"
            + st.session_state.last_report
        ),
        file_name="labellens_complete_report.txt",
        mime="text/plain",
        use_container_width=True,
    )


# --------------------------------------------------
# FOOTER
# --------------------------------------------------

st.divider()

st.caption(
    "LabelLens is an accessibility assistant, not a medical or "
    "product-safety authority. Always verify important details "
    "against the original packaging."
)
