# ResumeIQ

> **100% Local AI Resume Analyzer & Interview Question Generator**

A privacy-first Python application that parses your resume (PDF/DOCX), extracts structured data using local LLMs (Ollama), analyzes experience level, and generates tailored technical + behavioral interview questions with expected answers — all running **offline** on your laptop.

Perfect for personal interview preparation and as a strong AI Engineering portfolio project.

---

## Tech Stack

| Technology | Purpose |
|------------|---------|
| Python 3.11+ | Core language |
| Ollama | Running LLMs locally |
| LangChain + Pydantic | LLM orchestration & data validation |
| Streamlit | Web UI |
| PyMuPDF + python-docx | PDF and DOCX parsing |

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

> 💡 Pull the repo and check the relevant files directly in the codebase. File paths are referenced below.

#### 1. Create Project Folder Structure

Run the following commands to scaffold the project directories:

```powershell
mkdir -p src/parser, src/extractor, src/analyzer, src/generator, src/models, src/utils
mkdir -p app, data, tests, docker
```

#### 2. Review Key Files in the Codebase

After pulling the repo, check the following files:

| File | Purpose |
|------|---------|
| `src/config.py` | App settings using `pydantic-settings`; configures LLM model, temperature, and data/temp directory paths |
| `.env.example` | Template for your local `.env` file; copy and rename to `.env` before running |
| `src/parser/document_parser.py` | Core parser module; handles text extraction from PDF (via PyMuPDF) and DOCX (via python-docx) with text cleaning |
| `app/app.py` | Streamlit UI for uploading a resume and previewing extracted text and metadata |
| `test_setup.py` | *(Optional)* Run this from the root to verify Ollama and dependencies are working correctly |

#### 3. Configure Your Environment

Copy `.env.example` to `.env` in the root folder:

```powershell
copy .env.example .env
```

#### 4. Run the Application

```powershell
streamlit run app/app.py
```

#### 5. Test the Parser

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