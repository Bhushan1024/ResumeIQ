from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate
from src.models.resume import ResumeData
from src.config import settings
from pathlib import Path
import time

class ResumeExtractor:
    def __init__(self):
        self.llm = ChatOllama(
            model=settings.LLM_MODEL,
            temperature=settings.LLM_TEMPERATURE,           # Critical for speed + consistency
            num_ctx=8192,              # Reduced from 8192 → much faster on most laptops  # how much input the model can remember
            num_predict=2048,          # Limit output length # how much output the model can generate
        )
        # Use structured output (most reliable way)
        self.structured_llm = self.llm.with_structured_output(ResumeData)

    def extract(self, resume_text: str) -> ResumeData:
        """Stable extraction with strict optimized prompt and fallback parsing."""
        
        # Optimized prompt - concise, strict, and effective
        prompt= ChatPromptTemplate.from_template("""
You are an expert resume parser.

Your ONLY task is to extract information strictly and accurately from the resume text
and return ONLY valid JSON matching the ResumeData schema.

## STRICT RULES (Follow exactly)
- Pay special attention to contact information (email, phone, LinkedIn).
- Do NOT add any explanation, reasoning, or extra text outside the JSON.
- If a field is not present, use null or empty list [].
- For experience_level, choose only: "Junior", "Mid-level", or "Senior" based on total years and role seniority. Do NOT add any description.
- For skills, list them as short, clean strings (e.g. "Java", "Python", "SQL").
- For experience, create one entry per job with responsibilities as short bullet points.

## EXTRACTION RULES
- full_name: Extract candidate full name if clearly present.
- email: Extract only the main personal email if present.
- phone: Extract only the main contact number if present.
- linkedin: Extract LinkedIn URL if explicitly present.
- github: Extract GitHub URL if explicitly present.
- location: Extract city/state/country only if explicitly written.
- summary: Extract professional summary/objective if present.
- skills: Extract technical and professional skills as short clean strings.
  Example: ["Java", "Spring Boot", "SQL", "React"]
- education: Extract each education entry separately.
- certifications: Extract certification names only.
- projects: Extract each project separately with title, description, technologies, and links if available.
- experience: Extract each job/internship separately with:
  - company
  - role
  - start_date
  - end_date
  - location
  - responsibilities (as short bullet-like strings)
- total_experience_years:
  - Extract ONLY if explicitly mentioned in the resume.
  - If not explicitly mentioned, calculate cirrect total experience years or return null.

## IMPORTANT
- Preserve date formats as written in the resume where possible.
- If current role is ongoing, keep end_date as written (e.g. "Present", "Current").
- Do not merge multiple jobs into one.
- Do not invent missing skills, projects, education, dates, or links.

Resume Text:
{resume_text}

Return ONLY a valid JSON object matching the ResumeData schema.
""")

        chain = prompt | self.structured_llm

        start_time = time.time()
        print("Starting LLM structured extraction...")  # For debugging in console

        try:
            result = chain.invoke( {"resume_text": resume_text})
            elapsed = time.time() - start_time
            print(f"Extraction completed in {elapsed:.1f} seconds")
            return result

        except Exception as e:
            print(f"Extraction failed: {e}")
            # Fallback: return empty structure
            return ResumeData(
                full_name="Extraction Failed",
                email=None,
                phone=None,
                location=None,
                linkedin=None,
                summary=None,
                skills=[],
                experience=[],
                education=[],
                projects=[],
                total_experience_years=None,
                experience_level="Unknown"
            )


# Quick test function
if __name__ == "__main__":
    from src.parser.document_parser import DocumentParser
    
    test_file = "data/sample_resume.pdf"   # Change to your test file
    text, meta = DocumentParser.parse_resume(test_file)
    
    extractor = ResumeExtractor()
    data = extractor.extract(text)
    
    print("\nExtracted Data:")
    print(data.model_dump_json(indent=2))