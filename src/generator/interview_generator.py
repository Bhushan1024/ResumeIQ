from langchain_ollama import ChatOllama
from src.config import settings
from src.generator.prompts import get_interview_prompt
import time

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
        
        start_time = time.time()
        print("Generating tailored interview questions...")
        response = self.llm.invoke(prompt)
        elapsed = time.time() - start_time
        print(f"Interview questions generated in {elapsed:.1f} seconds")
        
        return response.content