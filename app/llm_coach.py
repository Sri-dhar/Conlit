import google.generativeai as genai
import json
import re
from .config import settings
from . import analyzer
from . import leetcode_client

genai.configure(api_key=settings.gemini_api_key)
model = genai.GenerativeModel('gemini-1.5-flash')

def _create_slug(title: str) -> str:
    return re.sub(r'\W+', '-', title.lower()).strip('-')

def generate_coaching_plan(username: str, data_manager) -> dict:
    user_submissions = leetcode_client.get_user_submissions(username, limit=1000)
    solved_slugs = set()
    if user_submissions:
        solved_slugs = {_create_slug(sub['title']) for sub in user_submissions if sub['statusDisplay'] == 'Accepted'}
    
    print("===================SOLVEDSLUGS========================")
    print(solved_slugs)
    print("===================SOLVEDSLUGS========================")

    topic_gaps = analyzer.analyze_topic_gaps(username, data_manager)
    nemesis_problems = analyzer.find_nemesis_problems(username, data_manager)
    related_problems = analyzer.find_related_problems(nemesis_problems, data_manager)

    unsolved_nemesis_problems = {slug: attempts for slug, attempts in nemesis_problems.items() if slug not in solved_slugs}
    unsolved_related_problems = {}
    for combo, problems in related_problems.items():
        unsolved_problems = [slug for slug in problems if slug not in solved_slugs]
        if unsolved_problems:
            unsolved_related_problems[combo] = unsolved_problems
    
    prompt = (
        f"You are an expert LeetCode coach. Your task is to create a personalized coaching plan for the user '{username}'.\n\n"
        f"**Analysis Data:**\n"
        f"1. **Topic Gaps:** Here are topics the user has not yet mastered, with suggested practice problems:\n"
        f"{json.dumps(topic_gaps, indent=2)}\n\n"
        f"2. **Nemesis Problems:** Here are problems the user has attempted multiple times without success:\n"
        f"{json.dumps(unsolved_nemesis_problems, indent=2)}\n\n"
        f"3. **Related Problems:** Here are problems related to the user's nemesis problems, grouped by topic combinations:\n"
        f"{json.dumps(unsolved_related_problems, indent=2)}\n\n"
        f"**Your Task:**\n"
        f"Based on the analysis, create a structured coaching plan in JSON format. The plan should include:\n"
        f"1. A brief, encouraging introduction.\n"
        f"2. A 'focus_areas' array, with each element being an object containing a 'topic' and a 'reason'.\n"
        f"3. A 'suggested_problems' array, with each element being an object containing a 'slug', 'reason', and 'difficulty'.\n"
        f"Select a maximum of 3 focus areas and 5 suggested problems in total. Prioritize problems from the nemesis list and the related problems list."
    )
    
    try:
        response = model.generate_content(prompt)
        text = response.text.strip()
        if text.startswith("```json"):
            text = text[7:]
        if text.endswith("```"):
            text = text[:-3]
        
        # TODO: validate the JSON response here
        return json.loads(text)
    except Exception as e:
        return {"error": f"Error generating coaching plan: {e}"}

def generate_topic_gap_report(username: str, data_manager) -> str:
    return json.dumps(generate_coaching_plan(username, data_manager), indent=2)

def generate_nemesis_problem_advice(username: str, data_manager) -> str:
    return json.dumps(generate_coaching_plan(username, data_manager), indent=2)
