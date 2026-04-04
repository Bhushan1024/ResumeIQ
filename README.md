# ResumeIQ

> **100% Local AI Resume Analyzer & Interview Question Generator**

A privacy-first Python application that parses your resume (PDF/DOCX), extracts structured data using local LLMs (Ollama), analyzes experience level, and generates tailored technical + behavioral interview questions with expected answers — all running **offline** on your laptop.

Perfect for personal interview preparation and as a strong AI Engineering portfolio project.

---

## Project Status

| Phase | Description | Status |
|-------|-------------|--------|
| Phase 0 | Environment Setup | ✅ Completed |
| Phase 1 | Resume Parsing | ✅ Completed |

---

## Setup Guide (Windows)

Follow these steps exactly to get the project running on a fresh Windows machine.

### Phase 0: Environment Setup

#### 1. Create Project Folder

Create a new folder named `ResumeIQ`, for example:

```
C:\Projects\ResumeIQ
```

#### 2. Initialize Virtual Environment

```powershell
cd C:\Path\To\ResumeIQ
python -m venv venv
.\venv\Scripts\Activate.ps1
```

> ✅ You should see `(venv)` in your PowerShell prompt after activation.

#### 3. Create `requirements.txt`

Create a file named `requirements.txt` in the root folder with the following content:

```txt
streamlit
pymupdf
python-docx
pydantic
pydantic-settings
langchain
langchain-ollama
langchain-core
structlog
pytest
```

#### 4. Install Dependencies

```powershell
pip install -r requirements.txt
```

#### 5. Install Ollama

Download and run the installer from: [https://ollama.com/download](https://ollama.com/download)

Or install via `winget`:

```powershell
winget install Ollama.Ollama
```

> ⚠️ Restart PowerShell after installation.

#### 6. Pull a Recommended LLM Model

```powershell
ollama pull llama3.3:8b
```

Alternative strong model for extraction:

```powershell
ollama pull qwen3:8b
```

#### 7. Verify Installation

Run the following to confirm the model is working:

```powershell
ollama run qwen3:8b
```

Then type:

```
Hello! Tell me you are ready for resume analysis project.
```

To exit the Ollama chat:

```
/bye
```

---

### Phase 1: Resume Parsing (Text Extraction)

#### 1. Create Project Folder Structure

```powershell
mkdir -p src/parser, src/extractor, src/analyzer, src/generator, src/models, src/utils
mkdir -p app, data, tests, docker
```

#### 2. Create `src/config.py`

```python
from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")
    
    LLM_MODEL: str = "llama3.3:8b"
    LLM_TEMPERATURE: float = 0.0
    LLM_MAX_TOKENS: int = 2048
    
    BASE_DIR: Path = Path(__file__).parent.parent.parent
    DATA_DIR: Path = BASE_DIR / "data"
    TEMP_DIR: Path = BASE_DIR / "temp"

settings = Settings()
settings.DATA_DIR.mkdir(exist_ok=True)
settings.TEMP_DIR.mkdir(exist_ok=True)
```

#### 3. Create `.env.example` in the Root Folder

```env
LLM_MODEL=llama3.3:8b
```

#### 4. Test Ollama Setup *(Optional but Recommended)*

Create `test_setup.py` in the root folder and run it to verify everything works.

#### 5. Create Parser Module → `src/parser/document_parser.py`

```python
import pymupdf  # fitz
from docx import Document
from pathlib import Path
from typing import Dict, Any, Tuple
import re

class DocumentParser:
    """Handles text extraction from PDF and DOCX resumes."""

    SUPPORTED_EXTENSIONS = {".pdf", ".docx"}

    @staticmethod
    def validate_file(file_path: str | Path) -> None:
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"File not found: {path}")
        if path.suffix.lower() not in DocumentParser.SUPPORTED_EXTENSIONS:
            raise ValueError(f"Unsupported file type: {path.suffix}. Only PDF and DOCX allowed.")

    @staticmethod
    def extract_text_from_pdf(file_path: str | Path) -> Tuple[str, Dict[str, Any]]:
        DocumentParser.validate_file(file_path)
        path = Path(file_path)
        
        metadata = {
            "filename": path.name,
            "file_type": "pdf",
            "page_count": 0,
            "extraction_method": "pymupdf_text"
        }
        
        text_blocks = []
        with pymupdf.open(path) as doc:
            metadata["page_count"] = len(doc)
            for page_num, page in enumerate(doc, 1):
                page_text = page.get_text("text")
                page_text = DocumentParser._clean_text(page_text)
                if page_text.strip():
                    text_blocks.append(f"--- Page {page_num} ---\n{page_text}")
        
        full_text = "\n\n".join(text_blocks)
        return full_text.strip(), metadata

    @staticmethod
    def extract_text_from_docx(file_path: str | Path) -> Tuple[str, Dict[str, Any]]:
        DocumentParser.validate_file(file_path)
        path = Path(file_path)
        
        doc = Document(path)
        metadata = {
            "filename": path.name,
            "file_type": "docx",
            "paragraph_count": len(doc.paragraphs),
            "extraction_method": "python-docx"
        }
        
        paragraphs = [DocumentParser._clean_text(para.text) for para in doc.paragraphs if para.text.strip()]
        full_text = "\n\n".join(paragraphs)
        return full_text.strip(), metadata

    @staticmethod
    def _clean_text(text: str) -> str:
        if not text:
            return ""
        text = re.sub(r'\s+', ' ', text).strip()
        text = re.sub(r'[\u200b\u200c\u200d]', '', text)
        return text

    @staticmethod
    def parse_resume(file_path: str | Path) -> Tuple[str, Dict[str, Any]]:
        path = Path(file_path)
        suffix = path.suffix.lower()
        
        if suffix == ".pdf":
            return DocumentParser.extract_text_from_pdf(file_path)
        elif suffix == ".docx":
            return DocumentParser.extract_text_from_docx(file_path)
        else:
            raise ValueError(f"Unsupported file: {suffix}")

if __name__ == "__main__":
    # Test with your sample resume (place file in data/ folder)
    test_file = "data/sample_resume.pdf"   # Change filename as needed
    try:
        text, meta = DocumentParser.parse_resume(test_file)
        print("Metadata:", meta)
        print("\nExtracted Text (first 500 chars):")
        print(text[:500] + "..." if len(text) > 500 else text)
    except Exception as e:
        print("Error:", e)
```

#### 6. Create Streamlit Test App → `app/app.py`

```python
import streamlit as st
from pathlib import Path
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
```

#### 7. Run the Application

```powershell
streamlit run app/app.py
```

#### 8. Test the Parser

1. Place 1–2 anonymized resume files (PDF or DOCX) inside the `data/` folder.
2. Open the Streamlit app in your browser.
3. Upload a resume and verify that the extracted text is readable and sections are preserved.

---

## Troubleshooting

### `ModuleNotFoundError: No module named 'langchain_ollama'`

Reinstall all dependencies:

```powershell
pip install -r requirements.txt
```

Or install the missing package directly:

```powershell
pip install langchain-ollama
```

---

### PowerShell Activation Error

If `.\venv\Scripts\Activate.ps1` fails, run:

```powershell
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
```

Then try activating the virtual environment again.

---

### `'ollama' is not recognized as an internal or external command`

1. Restart PowerShell.
2. Reinstall Ollama if needed.
3. Verify that Ollama is added to your system `PATH`.

---

### Permission Denied While Creating `venv`

1. Close any terminal or editor that is using the project folder.
2. Delete the partially created `venv` folder.
3. Run the command again:

```powershell
python -m venv venv
```