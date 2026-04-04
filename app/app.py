import streamlit as st
from pathlib import Path
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.parser.document_parser import DocumentParser

st.title("ResumeAI Prep - Phase 1: Resume Parser Test")

uploaded_file = st.file_uploader("Upload your resume (PDF or DOCX)", type=["pdf", "docx"])

if uploaded_file:
    temp_path = Path("temp") / uploaded_file.name
    temp_path.parent.mkdir(exist_ok=True)
    
    with open(temp_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    
    try:
        with st.spinner("Extracting text from resume..."):
            text, metadata = DocumentParser.parse_resume(temp_path)
        
        st.success("✅ Text extracted successfully!")
        st.json(metadata)
        
        st.subheader("Extracted Resume Text")
        st.text_area("Full Extracted Text", text, height=500)
        
    except Exception as e:
        st.error(f"Error: {str(e)}")
    
    # Cleanup temporary file
    temp_path.unlink(missing_ok=True)