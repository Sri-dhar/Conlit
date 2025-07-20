import json
import re
import os
from app.config import settings

class DataManager:
    def __init__(self):
        self.questions_by_slug = {}
        self.questions_by_topic = {}

    def load_and_index_data(self):
        try:
            # Ensure the path is constructed correctly for the environment
            path = settings.question_data_path
            with open(path, 'r') as f:
                data = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            print(f"Warning: Could not load data from {settings.question_data_path}")
            return

        for contest_slug, contest_data in data.items():
            questions = contest_data.get("questions", [])
            if not questions:
                # Log or handle contests that do not contain any questions.
                # print(f"Info: No questions found for contest: {contest_slug}")
                pass
            for question in questions:
                if question and "title" in question:
                    # Create a URL-friendly slug by converting the title to lowercase, replacing non-word characters with hyphens, and removing leading/trailing hyphens
                    title = question["title"]
                    slug = re.sub(r'\W+', '-', title.lower()).strip('-')
                    self.questions_by_slug[slug] = question
                    
                    for tag in question.get("topicTags", []):
                        topic_name = tag.get("name")
                        if topic_name:
                            if topic_name not in self.questions_by_topic:
                                self.questions_by_topic[topic_name] = []
                            self.questions_by_topic[topic_name].append(question)
        

    def get_question_by_slug(self, slug: str):
        return self.questions_by_slug.get(slug)

    def get_questions_by_topic(self, topic: str):
        return self.questions_by_topic.get(topic, [])
