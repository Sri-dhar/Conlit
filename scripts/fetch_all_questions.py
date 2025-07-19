#!/usr/bin/python
import httpx
import json
import os
import time

STORAGE_FILE = 'data/all_contests_questions.json'

def get_all_contests():
    try:
        leetcode_url = "https://leetcode.com/graphql"
        query = """
        query {
            allContests {
                title
                titleSlug
                startTime
            }
        }
        """
        
        payload = {
            "query": query
        }
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Content-Type': 'application/json'
        }

        response = httpx.post(leetcode_url, json=payload, headers=headers)
        response.raise_for_status()
        
        data = response.json()
        
        if "errors" in data:
            print(f"GraphQL Errors for contests: {data['errors']}")
            return []
            
        all_contests = data.get("data", {}).get("allContests", [])
        return all_contests

    except httpx.HTTPStatusError as e:
        print(f"HTTP Error fetching contests: {e.response.status_code} - {e.response.text}")
        return []
    except Exception as e:
        print(f"An error occurred fetching contests: {e}")
        return []

def get_question_details(title_slug):
    try:
        leetcode_url = "https://leetcode.com/graphql"
        query = """query questionData($titleSlug: String!) {
            question(titleSlug: $titleSlug) {
                questionId
                questionFrontendId
                title
                content
                likes
                dislikes
                stats
                similarQuestions
                categoryTitle
                hints
                topicTags { name }
                companyTags { name }
                difficulty
                isPaidOnly
                solution { canSeeDetail content }
                hasSolution
                hasVideoSolution
            }
        }"""
        
        payload = {
            "query": query,
            "variables": {"titleSlug": title_slug}
        }
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Content-Type': 'application/json'
        }

        response = httpx.post(leetcode_url, json=payload, headers=headers)
        response.raise_for_status()
        
        data = response.json()
        
        if "errors" in data:
            print(f"GraphQL Errors for {title_slug}: {data['errors']}")
            return None
            
        question_data = data.get("data", {}).get("question")
        return question_data

    except httpx.HTTPStatusError as e:
        print(f"HTTP Error for {title_slug}: {e.response.status_code} - {e.response.text}")
        return None
    except Exception as e:
        print(f"An error occurred for {title_slug}: {e}")
        return None

def get_contest_questions(contest_slug):
    try:
        leetcode_url = "https://leetcode.com/graphql"
        query = """query contestInfo($titleSlug: String!) {
            contest(titleSlug: $titleSlug) {
                title
                questions {
                    title
                    titleSlug
                }
            }
        }"""
        
        variables = {
            "titleSlug": contest_slug
        }
        
        payload = {
            "query": query,
            "variables": variables
        }
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Content-Type': 'application/json'
        }

        response = httpx.post(leetcode_url, json=payload, headers=headers)
        response.raise_for_status()
        
        data = response.json()
        
        if "errors" in data:
            print(f"GraphQL Errors: {data['errors']}")
            return None
            
        contest_data = data.get("data", {}).get("contest")
        if not contest_data:
            print("Contest not found.")
            return None
            
        questions = contest_data.get("questions")
        
        return questions

    except httpx.HTTPStatusError as e:
        print(f"HTTP Error: {e.response.status_code} - {e.response.text}")
        return None
    except Exception as e:
        print(f"An error occurred: {e}")
        return None

def load_stored_data():
    if os.path.exists(STORAGE_FILE):
        with open(STORAGE_FILE, 'r') as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return {}
    return {}

def save_data(data):
    os.makedirs(os.path.dirname(STORAGE_FILE), exist_ok=True)
    with open(STORAGE_FILE, 'w') as f:
        json.dump(data, f, indent=2)

if __name__ == '__main__':
    stored_data = load_stored_data()
    all_contests = get_all_contests()

    if not all_contests:
        print("Could not retrieve contest list. Exiting.")
    else:
        print(f"Found {len(all_contests)} contests.")
        for contest in all_contests:
            contest_slug = contest['titleSlug']
            if contest_slug in stored_data:
                print(f"Skipping '{contest_slug}', already fetched.")
                continue

            print(f"\nFetching questions for contest: '{contest_slug}'")
            questions = get_contest_questions(contest_slug)
            
            if questions:
                print(f"Found {len(questions)} questions for contest '{contest_slug}'.")
                contest_with_questions = {
                    "title": contest['title'],
                    "titleSlug": contest['titleSlug'],
                    "startTime": contest['startTime'],
                    "questions": []
                }

                for q in questions:
                    print(f"--- Fetching details for: {q['title']} ---")
                    details = get_question_details(q['titleSlug'])
                    if details:
                        contest_with_questions["questions"].append(details)
                    time.sleep(1)  # delay for rate-limiting
                
                if contest_with_questions["questions"]:
                    stored_data[contest_slug] = contest_with_questions
                    save_data(stored_data)
                    print(f"Successfully fetched and stored data for '{contest_slug}'.")
                else:
                    print(f"No question details found for '{contest_slug}', skipping.")

        print("\nAll contests processed.")
