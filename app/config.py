from pydantic_settings import BaseSettings
import os
from typing import Optional

class Settings(BaseSettings):
    gemini_api_key: str
    leetcode_session: Optional[str] = None
    
    data_dir: str = "data"

    question_data_path: str = os.path.join(data_dir, "all_contests_questions.json")

    class Config:
        env_file = ".env"

settings = Settings()
