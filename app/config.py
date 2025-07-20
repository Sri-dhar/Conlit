from pydantic_settings import BaseSettings
import os

class Settings(BaseSettings):
    gemini_api_key: str
    leetcode_session: str
    
    data_dir: str = "data"
    
    if os.getenv("VERCEL_ENV"):
        data_dir = "/var/task/data"

    question_data_path: str = os.path.join(data_dir, "all_contests_questions.json")

    class Config:
        env_file = ".env"

settings = Settings()
