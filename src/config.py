from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")
    
    LLM_MODEL: str = "llama3.2:3b"      # Change if you pulled a different model or we can use llama3.2:3b or "qwen3:8b"
    LLM_TEMPERATURE: float = 0.0        # Low for consistent extraction
    LLM_MAX_TOKENS: int = 2048
    
    BASE_DIR: Path = Path(__file__).parent.parent.parent
    DATA_DIR: Path = BASE_DIR / "data"
    TEMP_DIR: Path = BASE_DIR / "temp"

settings = Settings()

# Create folders
settings.DATA_DIR.mkdir(exist_ok=True)
settings.TEMP_DIR.mkdir(exist_ok=True)

print(f"Config loaded - Using model: {settings.LLM_MODEL}")