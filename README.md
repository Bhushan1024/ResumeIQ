# ResumeIQ

# ResumeIQ Prep

**100% Local AI Resume Analyzer & Interview Question Generator**

A privacy-first Python application that parses your resume (PDF/DOCX), extracts structured data using local LLMs (Ollama), analyzes experience level, and generates tailored technical + behavioral interview questions with expected answers — all running **offline** on your laptop.

Perfect for personal interview preparation and as a strong AI Engineering portfolio project.

### Current Status
- **Phase 0**: Environment Setup → Completed ✅
- **Phase 1**: Resume Parsing → In Progress

---

## How to Set Up from Scratch (Windows)

Follow these steps exactly to get the project running on a fresh Windows machine.

### Phase 0: Environment Setup

1. **Create Project Folder**
   - Create a new folder named `ResumeIQ` (e.g., `C:\Projects\ResumeIQ`).

2. **Initialize Virtual Environment**
   ```powershell
   cd C:\Path\To\ResumeIQ
   python -m venv venv
   .\venv\Scripts\Activate.ps1
   
   (You should see (venv) in your PowerShell prompt)

3. Create requirements.txt in the root folder with this content:txtstreamlit
pymupdf
python-docx
pydantic
pydantic-settings
langchain
langchain-ollama
langchain-core
structlog
pytest

4. Install Dependencies
PowerShell
pip install -r requirements.txt

5. Install Ollama
Download and run the installer from: https://ollama.com/download
Or install via winget:
PowerShell
winget install Ollama.Ollama
Restart PowerShell after installation.

6. Pull Recommended LLM Model
PowerShell
ollama pull llama3.3:8b or ollama pull qwen3:8b
(Alternative strong model for extraction: ollama pull qwen3:8b)

7. verufy by  ollama run qwen3:8b
Hello! Tell me you are ready for resume analysis project

To exit Ollama chat:
/bye


Common Issues
1) ModuleNotFoundError

If you see something like:

ModuleNotFoundError: No module named 'langchain_ollama'

Fix:

pip install -r requirements.txt

Or install directly:

pip install langchain-ollama
2) PowerShell Activation Error

If this fails:

.\venv\Scripts\Activate.ps1

Run:

Set-ExecutionPolicy -Scope CurrentUser RemoteSigned

Then try again.

3) Ollama Not Recognized

If this happens:

'ollama' is not recognized as an internal or external command

Fix:

Restart PowerShell
Reinstall Ollama if needed
Check if Ollama is added to PATH
4) Permission Denied While Creating venv

If you get a permission error:

Close any terminal/editor using the folder
Delete the partially created venv folder
Run again:
python -m venv venv
