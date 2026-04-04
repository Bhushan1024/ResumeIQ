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
            num_ctx=4096,              # Reduced from 8192 → much faster on most laptops
            num_predict=2048,          # Limit output length
        )
        # Use structured output (most reliable way)
        self.structured_llm = self.llm.with_structured_output(ResumeData)

    def extract(self, resume_text: str) -> ResumeData:
        """Extract structured data from resume text with optimized prompt."""
        
        # Optimized prompt - concise, strict, and effective
        prompt= ChatPromptTemplate.from_template("""
You are an expert resume parser. Extract information **strictly and accurately** from the resume text.

Strict Rules:
- ONLY use information explicitly written in the resume. Never guess, assume, or hallucinate.
- Do NOT add any explanation, reasoning, or extra text outside the JSON.
- If a field is not present, use null or empty list [].
- For experience_level, choose only: "Junior", "Mid-level", or "Senior" based on total years and role seniority. Do NOT add any description.
- For skills, list them as short, clean strings (e.g. "Java", "Python", "SQL").
- For experience, create one entry per job with responsibilities as short bullet points.

Resume Text:
{resume_text}

Return ONLY a valid JSON object that exactly matches the ResumeData schema. No markdown, no ```json, no extra text.
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
                experience_level="Unknown",
                skills=[],
                experience=[],
                education=[]
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