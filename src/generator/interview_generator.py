from langchain_ollama import ChatOllama
from src.config import settings
from src.generator.prompts import get_interview_prompt

class InterviewGenerator:
    def __init__(self):
        self.llm = ChatOllama(
            model=settings.LLM_MODEL,
            temperature=0.7,      # Higher temperature for creative answers
            num_ctx=4096,
        )

    def generate_questions(self, resume_data, num_questions=8):
        """Generate tailored interview questions and expected answers."""
        prompt = get_interview_prompt(resume_data, num_questions)
        
        print("Generating tailored interview questions...")
        response = self.llm.invoke(prompt)
        
        return response.content