
import os
import streamlit as st

from src.ocr_engine import extract_text
from src.crew_setup import analyze_label


st.set_page_config(
    page_title="LabelLens",
    page_icon=None,
    layout="wide"
)

st.title("LabelLens")
st.subheader("Packaging Accessibility Assistant")

st.write(
    "Upload a packaging photo to extract, organize, and listen to "
    "visible text. Always check important information against the "
    "original package."
)

# Session memory belongs to this user's current app session.
if "label_memory" not in st.session_state:
    st.session_state.label_memory = []

if "last_report" not in st.session_state:
    st.session_state.last_report = None

if "last_ocr_text" not in st.session_state:
    st.session_state.last_ocr_text = ""

uploaded_file = st.file_uploader(
    "Upload a package image",
    type=["png", "jpg", "jpeg"]
)

if uploaded_file:
    from PIL import Image

    image = Image.open(uploaded_file).convert("RGB")

    left, right = st.columns(2)

    with left:
        st.image(image, caption="Original package image", use_container_width=True)

    with right:
        st.write("Image details")
        st.write(f"Image size: {image.width} × {image.height}")

    if st.button("Extract and analyze label", type="primary"):
        try:
            with st.spinner("Extracting text with OCR..."):
                ocr_result = extract_text(image)

            extracted_text = ocr_result["text"]
            confidence = ocr_result["average_confidence"]

            st.session_state.last_ocr_text = extracted_text
            st.session_state.last_report = None

            if not extracted_text.strip():
                st.error(
                    "No readable text was detected. Try a clearer, "
                    "well-lit image."
                )
            else:
                st.success("Text extraction finished.")

                if ocr_result["warning"]:
                    st.warning(ocr_result["warning"])

                st.write(f"OCR confidence estimate: {confidence:.0%}")

                with st.spinner("CrewAI is organizing and reviewing the text..."):
                    report = analyze_label(
                        extracted_text=extracted_text,
                        confidence=confidence,
                        memory_store=st.session_state.label_memory
                    )

                st.session_state.last_report = report

                # Save only a short, non-sensitive session note.
                st.session_state.label_memory.append(
                    f"Last analysis: {len(extracted_text)} characters extracted. "
                    f"Average OCR confidence: {confidence:.0%}."
                )
                st.session_state.label_memory = (
                    st.session_state.label_memory[-10:]
                )

        except Exception as error:
            st.error(
                "The analysis failed. Check the app logs and verify "
                "that the API key and dependencies are configured."
            )
            st.caption(f"Technical details: {error}")

if st.session_state.last_ocr_text:
    st.divider()
    st.header("Original extracted text")

    st.text_area(
        "OCR result — check this against the image",
        value=st.session_state.last_ocr_text,
        height=220
    )

if st.session_state.last_report:
    st.divider()
    st.header("Organized label report")
    st.markdown(st.session_state.last_report)

    st.download_button(
        "Download report",
        data=st.session_state.last_report,
        file_name="labellens_report.txt",
        mime="text/plain"
    )

    st.caption(
        "AI-organized content can contain errors. Verify all important "
        "details against the original package."
    )

st.divider()
st.subheader("Accessibility settings")

font_size = st.slider(
    "Reading text size",
    min_value=16,
    max_value=32,
    value=20
)

if st.session_state.last_ocr_text:
    st.markdown(
        f'<div style="font-size:{font_size}px; line-height:1.7;">'
        f'{st.session_state.last_ocr_text}</div>',
        unsafe_allow_html=True
    )

st.caption(
    "Read-aloud support can be added next. This first version focuses "
    "on reliable extraction and accessible text."
)

if st.button("Clear session memory"):
    st.session_state.label_memory = []
    st.session_state.last_report = None
    st.session_state.last_ocr_text = ""
    st.rerun()
