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
| Phase 2 | Structured Data Extraction | ✅ Completed |
| Phase 3 | Experience Level Analysis + Candidate Summary | ✅ Completed
| Phase 4 | Interview Questions & Expected Answers Generator | 🔄In Progress

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

### Phase 0: Environment Setup
- Create virtual environment and install dependencies from `requirements.txt`
- Install Ollama and pull recommended model: `ollama pull qwen3:8b`
- Set up project structure and `src/config.py`

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

### Phase 2: Structured Data Extraction with Pydantic + LLM

**Key Features Added:**
- Created structured Pydantic models in `src/models/resume.py` (ResumeData, Experience, Education, etc.)
- Built `src/extractor/resume_extractor.py` using LangChain + Ollama with `with_structured_output()`
- Optimized prompt for qwen3:8b to improve accuracy and reduce hallucination
- Enhanced Streamlit UI with:
  - Clear step-by-step progress messages
  - Metrics dashboard (name, skills count, experience entries)
  - Tabs for Experience, Skills, and Education
  - Cancel button during long LLM processing
  - Sidebar showing Ollama backend status
- Fixed common extraction issues and improved error handling

Raw resume text is now reliably converted into clean, structured Python objects.

---

### Phase 3: Experience Level Analysis + Candidate Summary

**Key Features Added:**
- Created `src/analyzer/experience_analyzer.py` with `ExperienceAnalyzer` class
- Implemented rule-based experience level calculation:
  - Junior (< 2 years)
  - Mid-level (2–5 years)
  - Senior (> 5 years)
- Generated professional **candidate profile summary** based on extracted data
- Fixed hallucinated experience levels coming from Phase 2
- Added summary display and metrics in Streamlit UI
- Updated data flow: Phase 2 → Phase 3 → Ready for Question Generation

---

### Phase 4: Interview Questions & Expected Answers Generator

**Key Features Added:**
- Developed a smart interview question generator that creates personalized and relevant questions based on the candidate’s actual resume data, experience, skills, and projects.
- Generated high-quality expected answers that are grounded in the candidate’s real background using dynamic prompt engineering.
- Supported multiple question categories including Technical, Behavioral (STAR method), and Situational/Project-based questions.
- Integrated the generator seamlessly into the Streamlit UI with clean, readable markdown output.
- Added one-click download functionality to save the generated questions and answers as a Markdown file.
- Completed the full end-to-end AI workflow: from resume upload to ready-to-practice personalized interview preparation.


This phase turns the application into a complete, practical interview preparation tool by providing tailored questions and model answers specific to the user's resume.

---
 
## Verifying Ollama is Running
 
Before launching the app, run these commands in PowerShell to confirm the LLM backend is active.
 
#### 1. Check if the Ollama Server is Responding
 
```powershell
curl http://localhost:11434
```
 
> ✅ If you see `"Ollama is running"` or a JSON response, the server is up.
 
#### 2. List All Downloaded Models
 
```powershell
ollama list
```
 
#### 3. Check Which Models are Loaded in Memory
 
```powershell
ollama ps
```
 
- If your model (e.g., ` llama3.2:3b` or `qwen3:8b`) appears under the `NAME` column, it is active and loaded.
- The `PROCESSOR` column shows `GPU` or `CPU` — GPU means faster inference via your graphics card.
 
#### 4. Quick Interactive Test
 
```powershell
ollama run llama3.3:8b
```
 
Type the following prompt:
 
```
Say hello and confirm you are ready for resume analysis.
```
 
Then exit with:
 
```
/bye
```
 
> ✅ If Ollama responds to your prompt, the LLM is working perfectly.
 
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


Prerequisites before running this project run ollam on local through powershell using ollama run llama3
verify it is running by hitting curl.exe http://localhost:11434 or curl http://localhost:11434 or after use stop ollama by doing quit ollama from hidden icons from bottom of you taskbar and verufy again if it is running or not by 
by hitting curl.exe http://localhost:11434 or curl http://localhost:11434
---

# Prerequisites

Before running this project, make sure that **Ollama** is installed and running locally.

---

# Setting Up Ollama

## 1. Start Ollama Locally

Open **PowerShell** and run:

```powershell
ollama run llama3
```

This command starts Ollama and loads the `llama3` model locally.

---

## 2. Verify Ollama Is Running

To verify that Ollama is running correctly, open **PowerShell** and run either of the following commands:

```powershell
curl.exe http://localhost:11434
```

or

```powershell
curl http://localhost:11434
```

If Ollama is running successfully, you should see a response similar to:

```text
Ollama is running
```

> **Note:**  
> In PowerShell, `curl` may map to `Invoke-WebRequest`, which can behave differently.  
> If you encounter issues, prefer using:

```powershell
curl.exe http://localhost:11434
```

---

# Stopping Ollama After Use

After using the project, you can stop Ollama to free up system resources.

## Option 1: Quit from the Taskbar

1. Click the hidden icons arrow in the bottom-right corner of the taskbar.
2. Locate the **Ollama** icon.
3. Right-click the icon.
4. Select **Quit Ollama**.

---

## 3. Verify Ollama Has Stopped

After quitting Ollama, verify that it has stopped by running:

```powershell
curl.exe http://localhost:11434
```

or

```powershell
curl http://localhost:11434
```

If Ollama has stopped successfully, you should receive a response similar to:

```text
Failed to connect
```

or

```text
Connection refused
```