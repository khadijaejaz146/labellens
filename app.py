
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
        "High-contrast reading",
        value=False,
    )

    st.divider()

    st.markdown("### Session")

    st.write(
        f"Saved session notes: {len(st.session_state.label_memory)}"
    )

    if st.button("Clear session data", use_container_width=True):
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
# CUSTOM DESIGN
# --------------------------------------------------

background = "#111827" if high_contrast else "#F5F7FB"
foreground = "#FFFFFF" if high_contrast else "#172033"
panel = "#1F2937" if high_contrast else "#FFFFFF"
muted = "#D1D5DB" if high_contrast else "#667085"
border = "#4B5563" if high_contrast else "#E5EAF2"
accent = "#60A5FA" if high_contrast else "#315EFB"

st.markdown(
    f"""
    <style>
    
/* Global readable text */
.stApp,
.stApp p,
.stApp label,
.stApp li,
.stApp h1,
.stApp h2,
.stApp h3,
.stApp span,
.stApp [data-testid="stMarkdownContainer"] {
    color: var(--ll-text) !important;
}

/* Streamlit theme variables */
:root {
    --ll-text: #172033;
    --ll-panel: #FFFFFF;
    --ll-border: #D1D9E6;
}

.stApp {
    color: var(--ll-text);
}

[data-testid="stAppViewContainer"],
[data-testid="stMain"] {
    background-color: #F5F7FB;
}

[data-testid="stSidebar"] {
    background-color: #FFFFFF;
}

[data-testid="stVerticalBlockBorderWrapper"],
[data-testid="stFileUploader"],
[data-testid="stAlert"] {
    border-color: #D1D9E6 !important;
}

/* Input fields */
.stApp input,
.stApp textarea,
.stApp [data-baseweb="select"] > div {
    background-color: #FFFFFF !important;
    color: #172033 !important;
    border-color: #B8C3D4 !important;
}

/* Tabs */
.stTabs [role="tab"] {
    color: #344054 !important;
}

.stTabs [role="tab"][aria-selected="true"] {
    color: #2448C7 !important;
    border-bottom-color: #315EFB !important;
}

/* Secondary buttons */
.stApp div.stButton > button[kind="secondary"],
.stApp div.stDownloadButton > button {
    background-color: #FFFFFF !important;
    color: #172033 !important;
    border: 1px solid #B8C3D4 !important;
}

/* Primary action button */
.stApp div.stButton > button[kind="primary"] {
    background-color: #315EFB !important;
    color: #FFFFFF !important;
}

/* Alerts: keep text readable */
.stAlert p,
.stAlert span {
    color: #172033 !important;
}
    .stApp {{
        background: {background};
        color: {foreground};
    }}

    [data-testid="stHeader"] {{
        background: transparent;
    }}

    [data-testid="stSidebar"] {{
        background: {panel};
        border-right: 1px solid {border};
    }}

    .block-container {{
        max-width: 1250px;
        padding-top: 2rem;
        padding-bottom: 3rem;
    }}

    .hero {{
        padding: 1.8rem;
        border-radius: 18px;
        background: {panel};
        border: 1px solid {border};
        margin-bottom: 1.5rem;
    }}

    .eyebrow {{
        color: {accent};
        text-transform: uppercase;
        font-size: 0.78rem;
        letter-spacing: 1.5px;
        font-weight: 700;
    }}

    .hero h1 {{
        color: {foreground};
        font-size: 2.5rem;
        line-height: 1.2;
        margin: 0.6rem 0;
    }}

    .hero p {{
        color: {muted};
        font-size: 1.05rem;
        margin-bottom: 0;
    }}

    div[data-testid="stVerticalBlockBorderWrapper"] {{
        border-radius: 14px;
        border-color: {border};
    }}

    div.stButton > button[kind="primary"] {{
        background: {accent};
        color: white;
        border: none;
        border-radius: 9px;
        min-height: 3rem;
        font-weight: 650;
    }}

    div.stButton > button {{
        border-radius: 9px;
    }}

    .section-label {{
        color: {muted};
        font-size: 0.85rem;
        margin-bottom: 0.35rem;
    }}

    textarea {{
        font-size: {font_size}px !important;
        line-height: 1.7 !important;
        background-color: {panel} !important;
        color: {foreground} !important;
    }}

    [data-testid="stFileUploader"] {{
        border-radius: 12px;
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
# IMAGE UPLOAD
# --------------------------------------------------

upload_col, preview_col = st.columns([1, 1], gap="large")

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

        image = None

        if uploaded_file is not None:
            try:
                image = Image.open(
                    BytesIO(uploaded_file.getvalue())
                ).convert("RGB")

                st.image(
                    image,
                    use_container_width=True,
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

    st.write("")

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
                confidence = ocr_result.get(
                    "average_confidence"
                )
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

        except Exception:
            st.error(
                "Analysis failed. Check your Streamlit logs for the "
                "technical error and verify your Groq secret."
            )

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
            use_container_width=True,
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
