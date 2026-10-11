
# LabelLens

LabelLens is a packaging accessibility assistant that helps users
read small printed text on household products and packaging.

## Features

- Upload a packaging image
- Extract visible text with OCR
- Organize extracted text using CrewAI agents
- Identify uncertain or missing information
- Display a readable version of the extracted text
- Download an organized label report

## Technology Stack

- Streamlit
- CrewAI
- Groq LLM
- PaddleOCR
- Python

## Safety

LabelLens does not verify the physical package or provide medical advice.
OCR and AI output may contain errors. Always verify important information
against the original packaging.

## Setup

The app is designed for deployment through Streamlit Community Cloud.
Configure the GROQ_API_KEY secret before using the AI analysis feature.
