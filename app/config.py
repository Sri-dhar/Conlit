from pydantic_settings import BaseSettings
import os

class Settings(BaseSettings):
    gemini_api_key: str
    question_data_path: str = "data/all_contests_questions.json"

    class Config:
        env_file = ".env"

settings = Settings()
