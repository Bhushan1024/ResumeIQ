import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import streamlit as st
from pathlib import Path
from src.config import settings
import requests
from src.parser.document_parser import DocumentParser
from src.extractor.resume_extractor import ResumeExtractor
from src.config import settings

st.set_page_config(page_title="ResumeIQ Prep", page_icon="📄", layout="wide")
st.title("📄 ResumeIQ Prep")
st.markdown("### Local AI Resume Analyzer & Interview Prep Tool")

# ==================== LLM Backend Status Check ====================
st.sidebar.header("🔧 Backend Status")

try:
    # Check if Ollama server is alive
    response = requests.get("http://localhost:11434", timeout=3)
    if response.status_code == 200:
        st.sidebar.success("✅ Ollama Server is Running")
    else:
        st.sidebar.error("❌ Ollama Server not responding")
except:
    st.sidebar.error("❌ Ollama is not running. Start Ollama first!")

# Show current model
st.sidebar.info(f"**Model:** {settings.LLM_MODEL}")

# Optional: Show running models
if st.sidebar.button("Refresh LLM Status"):
    try:
        ps_response = requests.get("http://localhost:11434/api/ps", timeout=5)
        if ps_response.status_code == 200:
            data = ps_response.json()
            if data.get("models"):
                st.sidebar.success("Models currently loaded:")
                for model in data["models"]:
                    st.sidebar.write(f"• {model.get('name')} ({model.get('size', 'N/A')})")
            else:
                st.sidebar.info("No model loaded yet (will load when you upload resume)")
    except:
        st.sidebar.warning("Could not fetch running models")

# Session state to handle cancellation
if "processing" not in st.session_state:
    st.session_state.processing = False

uploaded_file = st.file_uploader(
    "Upload your resume (PDF or DOCX)", 
    type=["pdf", "docx"],
    help="Your resume will be processed locally. No data is sent to any server."
)

if uploaded_file and not st.session_state.processing:
    # Create temp directory if not exists
    temp_dir = Path("temp")
    temp_dir.mkdir(exist_ok=True)
    temp_path = temp_dir / uploaded_file.name

    # Save uploaded file temporarily
    with open(temp_path, "wb") as f:
        f.write(uploaded_file.getbuffer())

    try:
        # st.session_state.processing = True
        # ------------------- Phase 1: Text Extraction -------------------
        st.subheader("🔍 Step 1: Extracting Raw Text from Resume")
        with st.spinner("Reading resume file and extracting text..."):
            raw_text, metadata = DocumentParser.parse_resume(temp_path)
        
        st.success("✅ Step 1 Complete: Raw text extracted successfully!")
        
        col1, col2 = st.columns([1, 2])
        with col1:
            st.caption("File Information")
            st.json(metadata)
        
        with col2:
            st.caption("Preview of Extracted Text")
            st.text_area("First 800 characters", raw_text[:800] + "..." if len(raw_text) > 800 else raw_text, height=200)

        st.divider()

        # ------------------- Phase 2: Structured Extraction -------------------
        st.subheader("🧠 Step 2: AI Understanding Your Resume")
        st.info("The AI model is now reading your resume and structuring the data (name, skills, experience, etc.).\nThis step usually takes 10–40 seconds depending on your laptop speed.")

        # Cancel button
        if st.button("⛔ Cancel Analysis & Start Over", type="secondary"):
            st.session_state.processing = False
            st.rerun()

        with st.spinner("Analyzing resume with local AI model...\nThis may take 10-30 seconds depending on your laptop."):
            extractor = ResumeExtractor()
            structured_data = extractor.extract(raw_text)
        
        st.success("✅ AI has successfully understood and structured your resume!")

        # Show nice summary of what was extracted
        st.subheader("📋 What was extracted from your resume:")
        
        col_a, col_b = st.columns(2)
        with col_a:
            st.metric("Full Name", structured_data.full_name or "Not found")
            st.metric("Experience Level", structured_data.experience_level)
            st.metric("Total Experience", f"{structured_data.total_experience_years or 0:.1f} years")
        
        with col_b:
            skills_count = len(structured_data.skills)
            exp_count = len(structured_data.experience)
            st.metric("Skills Detected", skills_count)
            st.metric("Experience Entries", exp_count)

        # Display full structured data
        with st.expander("🔍 View Complete Structured Data (JSON)", expanded=False):
            st.json(structured_data.model_dump())

        # Show key sections in readable format
        st.subheader("📝 Key Sections Extracted")
        
        tab1, tab2, tab3 = st.tabs(["💼 Experience", "🛠️ Skills", "🎓 Education"])
        
        with tab1:
            if structured_data.experience:
                for i, exp in enumerate(structured_data.experience):
                    st.write(f"**{exp.role}** at **{exp.company}**")
                    if exp.responsibilities:
                        st.write("Responsibilities:")
                        for resp in exp.responsibilities[:5]:  # Show first 5
                            st.write(f"• {resp}")
                    st.divider()
            else:
                st.info("No experience entries extracted.")

        with tab2:
            if structured_data.skills:
                st.write(", ".join(structured_data.skills))
            else:
                st.info("No skills extracted.")

        with tab3:
            if structured_data.education:
                for edu in structured_data.education:
                    st.write(f"**{edu.degree}** in {edu.field_of_study or 'N/A'}")
                    st.write(f"From: {edu.institution}")
            else:
                st.info("No education details extracted.")
        
        st.divider()

        # ------------------- Phase 3: Experience Analysis -------------------

        st.subheader("📊 Phase 3: Experience Analysis & Summary")
        
        with st.spinner("Analyzing experience level and generating profile summary..."):
            from src.analyzer.experience_analyzer import ExperienceAnalyzer
            analyzer = ExperienceAnalyzer()
            updated_data, candidate_summary = analyzer.analyze(structured_data)
        
        st.success("✅ Phase 3 Complete!")
        st.info(candidate_summary)
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Final Experience Level", updated_data.experience_level)
            st.metric("Total Experience Years", f"{updated_data.total_experience_years or 0:.1f} years")
        with col2:
            st.metric("Skills Count", len(updated_data.skills))

    except Exception as e:
        st.error(f"❌ Something went wrong: {str(e)}")
        st.info("Tip: Try with a well-formatted resume. Scanned PDFs may not work well yet.")

    finally:
        # Clean up temporary file
        temp_path.unlink(missing_ok=True)
        # st.session_state.processing = False
else:
    if st.session_state.processing:
        st.warning("Processing was cancelled. Upload your resume again to start fresh.")
    else:
        st.info("👆 Please upload your resume to begin the analysis.")
        st.caption("All processing happens locally using Ollama. No internet required after model download.")