from langchain_ollama import ChatOllama
from src.config import settings

print("Testing setup on Windows...")
print(f"Model: {settings.LLM_MODEL}")

llm = ChatOllama(
    model=settings.LLM_MODEL,
    temperature=settings.LLM_TEMPERATURE,
)

response = llm.invoke("Confirm: Ollama + LangChain setup is successful for ResumeAI Prep on Windows. Reply with 'Yes, ready!'")
print("\nResponse:", response.content)