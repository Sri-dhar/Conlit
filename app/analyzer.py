import re
import random
import os
import json
from . import leetcode_client
from .data_manager import DataManager

CACHE_DIR = "cache"
if not os.path.exists(CACHE_DIR):
    os.makedirs(CACHE_DIR)

def _get_cache_path(username: str) -> str:
    return os.path.join(CACHE_DIR, f"{username}_data.json")

def _read_cache(username: str) -> dict | None:
    cache_path = _get_cache_path(username)
    if os.path.exists(cache_path):
        with open(cache_path, 'r') as f:
            return json.load(f)
    return None

def _write_cache(username: str, data: dict):
    cache_path = _get_cache_path(username)
    with open(cache_path, 'w') as f:
        json.dump(data, f)

def _create_slug(title: str) -> str:
    return re.sub(r'\W+', '-', title.lower()).strip('-')

def analyze_topic_gaps(username: str, data_manager: DataManager, leetcode_session: str = None) -> dict:
    if leetcode_session:
        cached_data = _read_cache(username)
        current_submission_count = leetcode_client.get_user_submission_count(username)

        if cached_data and cached_data.get("submission_count") == current_submission_count:
            print(f"Using cached data for {username}")
            solved_slugs = set(cached_data["solved_slugs"])
        else:
            print(f"Fetching fresh data for {username}")
            try:
                solved_titles = leetcode_client.get_solved_questions(username, leetcode_session)
                solved_slugs = {_create_slug(title) for title in solved_titles}
                _write_cache(username, {"submission_count": current_submission_count, "solved_slugs": list(solved_slugs)})
            except Exception as e:
                return {"error": f"Could not fetch solved questions: {e}"}
    else:
        user_submissions = leetcode_client.get_user_submissions(username, limit=1000)
        if not user_submissions:
            return {"error": "Could not fetch user submissions."}
        solved_slugs = {_create_slug(sub['title']) for sub in user_submissions if sub['statusDisplay'] == 'Accepted'}

    user_submissions = leetcode_client.get_user_submissions(username, limit=1000)
    if not user_submissions:
        return {"error": "Could not fetch user submissions."}
    
    submission_counts = {}
    for sub in user_submissions:
        slug = _create_slug(sub['title'])
        if slug not in submission_counts:
            submission_counts[slug] = {'accepted': False, 'attempts': 0}
        submission_counts[slug]['attempts'] += 1
        if sub['statusDisplay'] == 'Accepted':
            submission_counts[slug]['accepted'] = True
    nemesis_slugs = {slug for slug, data in submission_counts.items() if data['attempts'] > 1}

    solved_topics = set()
    for slug in solved_slugs:
        question = data_manager.get_question_by_slug(slug)
        if question:
            for tag in question.get("topicTags", []):
                solved_topics.add(tag['name'])

    all_topics = set(data_manager.questions_by_topic.keys())
    unsolved_topics = all_topics - solved_topics

    topic_gaps = {}
    for topic in unsolved_topics:
        questions = data_manager.get_questions_by_topic(topic)
        # Suggesting 5 easy or medium problems for each topic gap 
        suggestions = []
        for q in questions:
            if q and 'difficulty' in q and q['difficulty'] in ['Easy', 'Medium'] and 'title' in q:
                slug = _create_slug(q['title'])
                if slug not in solved_slugs and slug not in nemesis_slugs:
                    suggestions.append(slug)
        
        random.shuffle(suggestions)
        if suggestions:
            topic_gaps[topic] = suggestions[:5]

    return dict(list(topic_gaps.items())[:5])

def analyze_unsolved_contest_problems(username: str, data_manager: DataManager) -> dict:
    contest_history = leetcode_client.get_user_contest_history(username)
    if not contest_history or 'userContestRankingHistory' not in contest_history:
        return {"error": "Could not fetch contest history."}

    unsolved_problems = []
    for contest in contest_history['userContestRankingHistory']:
        if contest['attended'] and contest['problemsSolved'] < contest['totalProblems']:
            # Can't get contest problems directly; just flag contest as unsolved.
            unsolved_problems.append(contest['contest']['title'])
    
    return {"unsolved_contests": unsolved_problems[:5]} # Return top 5

def find_nemesis_problems(username: str, data_manager: DataManager, leetcode_session: str = None) -> dict:
    if leetcode_session:
        cached_data = _read_cache(username)
        current_submission_count = leetcode_client.get_user_submission_count(username)

        if cached_data and cached_data.get("submission_count") == current_submission_count:
            print(f"Using cached data for {username}")
            solved_slugs = set(cached_data["solved_slugs"])
        else:
            print(f"Fetching fresh data for {username}")
            try:
                solved_titles = leetcode_client.get_solved_questions(username, leetcode_session)
                solved_slugs = {_create_slug(title) for title in solved_titles}
                _write_cache(username, {"submission_count": current_submission_count, "solved_slugs": list(solved_slugs)})
            except Exception as e:
                return {"error": f"Could not fetch solved questions: {e}"}
    else:
        user_submissions = leetcode_client.get_user_submissions(username, limit=1000)
        if not user_submissions:
            return {"error": "Could not fetch user submissions."}
        solved_slugs = {_create_slug(sub['title']) for sub in user_submissions if sub['statusDisplay'] == 'Accepted'}

    submissions = leetcode_client.get_user_submissions(username, limit=1000)
    if not submissions:
        return {"error": "Could not fetch submissions."}

    submission_counts = {}
    for sub in submissions:
        slug = _create_slug(sub['title'])
        if slug not in submission_counts:
            submission_counts[slug] = {'accepted': False, 'attempts': 0}
        submission_counts[slug]['attempts'] += 1
        if sub['statusDisplay'] == 'Accepted':
            submission_counts[slug]['accepted'] = True

    # A nemesis problem is one that took more than 1 attempt OR is unsolved.
    nemesis_problems = {
        slug: data['attempts'] for slug, data in submission_counts.items()
        if data['attempts'] > 1 or not data['accepted']
    }
    
    # Sort by number of attempts, shuffle, and return the top 10
    sorted_nemesis = sorted(nemesis_problems.items(), key=lambda item: item[1], reverse=True)
    random.shuffle(sorted_nemesis)
    return dict(sorted_nemesis[:10])


def find_related_problems(nemesis_problems: dict, data_manager: DataManager) -> dict:
    related_problems = {}
    for slug, attempts in nemesis_problems.items():
        question = data_manager.get_question_by_slug(slug)
        if not question:
            continue

        topics = [tag['name'] for tag in question.get("topicTags", [])]
        if len(topics) < 3:
            continue

        import itertools
        topic_combinations = list(itertools.combinations(topics, 3))

        for combo in topic_combinations:
            combo_key = ", ".join(sorted(combo))
            if combo_key not in related_problems:
                related_problems[combo_key] = []

            # Find other questions with the same three topics
            potential_problems = []
            for q_slug, q_data in data_manager.questions_by_slug.items():
                if q_slug == slug:
                    continue

                q_topics = {tag['name'] for tag in q_data.get("topicTags", [])}
                if set(combo).issubset(q_topics):
                    potential_problems.append(q_slug)
            
            random.shuffle(potential_problems)
            related_problems[combo_key].extend(potential_problems[:4])
    
    return related_problems


def generate_performance_summary(username: str, data_manager: DataManager) -> dict:
    profile = leetcode_client.get_user_profile(username)
    if not profile:
        return {"error": "Could not fetch user profile."}
        
    return {
        "ranking": profile.get('profile', {}).get('ranking'),
        "submission_stats": profile.get('submitStats')
    }
