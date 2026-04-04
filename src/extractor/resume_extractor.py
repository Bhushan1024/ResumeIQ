from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate
from src.models.resume import ResumeData
from src.config import settings
from pathlib import Path

class ResumeExtractor:
    def __init__(self):
        self.llm = ChatOllama(
            model=settings.LLM_MODEL,
            temperature=settings.LLM_TEMPERATURE,
            num_ctx=8192,   # Larger context for full resume
        )
        # Use structured output (Ollama + Pydantic)
        self.structured_llm = self.llm.with_structured_output(ResumeData)

    def extract(self, resume_text: str) -> ResumeData:
        prompt = ChatPromptTemplate.from_template("""
You are an expert resume parser. Extract all information accurately from the resume text below.
Only use information that is explicitly present. Do not hallucinate or add extra details.

Resume Text:
{resume_text}

Return the data in the exact structured format.
""")

        chain = prompt | self.structured_llm
        
        result = chain.invoke({"resume_text": resume_text})
        return result

# Simple test
if __name__ == "__main__":
    from src.parser.document_parser import DocumentParser
    
    test_file = "data/sample_resume.pdf"
    text, _ = DocumentParser.parse_resume(test_file)
    
    extractor = ResumeExtractor()
    structured_data = extractor.extract(text)
    
    print(structured_data.model_dump_json(indent=2))