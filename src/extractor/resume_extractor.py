from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate
from src.models.resume import ResumeData
from src.config import settings
from pathlib import Path
import time


def _all_fields_required_schema() -> dict:
    """JSON schema for ResumeData with every property marked required.

    Ollama turns the schema into a decoding grammar, and a property that is not
    in `required` may simply be skipped. Pydantic marks every defaulted field as
    optional, so small models were omitting the expensive ones (`experience`,
    `projects`, `summary`) and returning a resume with no jobs at all.
    Optional fields stay nullable, so the model can still answer "not present"
    with null / [] — it just can no longer stay silent.

    The same applies to the nested models in `$defs` (Experience, Education):
    without it the grammar lets the model drop start_date/end_date, which the
    analyzer needs to compute total years.
    """
    schema = ResumeData.model_json_schema()
    for obj in [schema, *schema.get("$defs", {}).values()]:
        if "properties" in obj:
            obj["required"] = list(obj["properties"].keys())
    return schema


class ResumeExtractor:
    def __init__(self):
        self.llm = ChatOllama(
            model=settings.LLM_MODEL,
            temperature=settings.LLM_TEMPERATURE,           # Critical for speed + consistency
            num_ctx=8192,              # how much input the model can remember
            num_predict=2048,          # Limit output length # how much output the model can generate
        )

        self.structured_llm = self.llm.with_structured_output(_all_fields_required_schema())

    def extract(self, resume_text: str) -> ResumeData:
        """Stable extraction with strict optimized prompt and fallback parsing."""
        
        # Optimized prompt - concise, strict, and effective
        prompt= ChatPromptTemplate.from_template("""
You are an expert resume parser.

Your ONLY task is to extract information strictly and accurately from the resume text
and return ONLY valid JSON matching the ResumeData schema.

## STRICT RULES (Follow exactly)
- Every key in the schema MUST appear in your JSON. Use null (or []) only when the
  resume genuinely does not contain that information — never to skip work.
- Do NOT add any explanation, reasoning, or extra text outside the JSON.
- Pay special attention to contact information (email, phone, LinkedIn).
- For experience_level, choose only: "Junior", "Mid-level", or "Senior", judged from the
  job titles and responsibilities (e.g. "Lead", "Architect", "Senior" titles -> "Senior";
  intern / trainee / fresher -> "Junior"). Do NOT add any description.
- For skills, list them as short, clean strings (e.g. "Java", "Python", "SQL").

## EXTRACTION RULES
- full_name: Extract candidate full name if clearly present.
- email: Extract only the main personal email if present.
- phone: Extract only the main contact number if present.
- linkedin: Extract LinkedIn URL if explicitly present.
- location: Extract city/state/country only if explicitly written.
- summary: Extract professional summary/objective if present.
- skills: Extract technical and professional skills as short clean strings.
  Example: ["Java", "Spring Boot", "SQL", "React"]
- education: Extract each education entry separately.
- projects: One short string per project (title, plus technologies if written).
- experience: MOST IMPORTANT FIELD. Read the work history / professional experience
  section and create ONE entry per job, internship or freelance role, in the order
  they appear. For every entry fill:
  - company
  - role
  - location
  - start_date  (the month/year the role started, exactly as written)
  - end_date    ("Present" or "Current" for an ongoing role, otherwise as written)
  - responsibilities (short bullet-like strings)
  Never return an empty experience list when the resume shows any job.
- total_experience_years:
  - Extract ONLY if explicitly mentioned in the resume (e.g. "5+ years of experience").
  - Otherwise return null. Do NOT try to add up the dates yourself.

## IMPORTANT
- Preserve date formats as written in the resume where possible.
- Put the start and the end of a role in their own fields; do not place a whole
  range like "Jan 2020 - Present" into start_date.
- Do not merge multiple jobs into one.
- Do not invent missing skills, projects, education, dates, or links.

<resume_text>
{resume_text}
</resume_text>

Return ONLY a valid JSON object matching the ResumeData schema.
""")

        chain = prompt | self.structured_llm

        start_time = time.time()
        print("Starting LLM structured extraction...")  # For debugging in console

        try:
            raw = chain.invoke({"resume_text": resume_text})
            result = ResumeData.model_validate(raw)
            elapsed = time.time() - start_time
            print(f"Extraction completed in {elapsed:.1f} seconds "
                  f"({len(result.experience)} experience entries)")
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