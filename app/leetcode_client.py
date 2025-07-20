import httpx
import os
import asyncio
from typing import List, Set, Tuple

LEETCODE_GRAPHQL_URL = "https://leetcode.com/graphql"
BASE_URL = "https://leetcode.com"

# GraphQL queries
USER_PROFILE_QUERY = """
query getUserProfile($username: String!) {
    matchedUser(username: $username) {
        submitStats: submitStatsGlobal {
            acSubmissionNum {
                difficulty
                count
            }
        }
    }
}
"""

SUBMISSIONS_QUERY = """
query submissionList($offset: Int!, $limit: Int!, $questionSlug: String) {
    submissionList(offset: $offset, limit: $limit, questionSlug: $questionSlug) {
        hasNext
        submissions {
            id
            title
            statusDisplay
            timestamp
        }
    }
}
"""

def get_user_profile(username: str):
    try:
        leetcode_url = LEETCODE_GRAPHQL_URL
        query = """query userPublicProfile($username: String!) {
            matchedUser(username: $username) {
                username
                profile {
                    realName
                    websites
                    countryName
                    company
                    school
                    aboutMe
                    reputation
                    ranking
                }
                submitStats {
                    acSubmissionNum {
                        difficulty
                        count
                        submissions
                    }
                    totalSubmissionNum {
                        difficulty
                        count
                        submissions
                    }
                }
            }
        }"""
        
        payload = {
            "query": query,
            "variables": {"username": username},
            "operationName": "userPublicProfile"
        }
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Content-Type': 'application/json',
            'Referer': BASE_URL
        }

        response = httpx.post(leetcode_url, json=payload, headers=headers, timeout=30)
        response.raise_for_status()
        
        data = response.json()
        
        if not data.get("data", {}).get("matchedUser"):
            print(f"User not found: {username}")
            return None
        return data["data"]["matchedUser"]

    except httpx.HTTPStatusError as e:
        print(f"HTTP Error fetching user profile for {username}: {e.response.status_code} - {e.response.text}")
        return None
    except Exception as e:
        print(f"An error occurred fetching user profile for {username}: {e}")
        return None

def get_user_contest_history(username: str):
    try:
        leetcode_url = LEETCODE_GRAPHQL_URL
        query = """query userContestRankingInfo($username: String!) {
            userContestRanking(username: $username) {
                attendedContestsCount
                rating
                globalRanking
                totalParticipants
                topPercentage
            }
            userContestRankingHistory(username: $username) {
                attended
                trendDirection
                problemsSolved
                totalProblems
                finishTimeInSeconds
                rating
                ranking
                contest {
                    title
                    startTime
                }
            }
        }"""
        
        payload = {
            "query": query,
            "variables": {"username": username},
            "operationName": "userContestRankingInfo"
        }
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Content-Type': 'application/json',
            'Referer': BASE_URL
        }

        response = httpx.post(leetcode_url, json=payload, headers=headers)
        response.raise_for_status()
        
        data = response.json()
        
        if not data.get("data"):
            print(f"Contest history not found for user: {username}")
            return None
        return data["data"]

    except httpx.HTTPStatusError as e:
        print(f"HTTP Error fetching contest history for {username}: {e.response.status_code} - {e.response.text}")
        return None
    except Exception as e:
        print(f"An error occurred fetching contest history for {username}: {e}")
        return None

def get_user_submissions(username: str, limit: int = 20):
    try:
        leetcode_url = LEETCODE_GRAPHQL_URL
        query = """query recentSubmissions($username: String!, $limit: Int!) {
            recentSubmissionList(username: $username, limit: $limit) {
                title
                titleSlug
                timestamp
                statusDisplay
                lang
                url
            }
        }"""
        
        payload = {
            "query": query,
            "variables": {"username": username, "limit": limit}
        }
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Content-Type': 'application/json',
            'Referer': BASE_URL
        }

        response = httpx.post(leetcode_url, json=payload, headers=headers)
        response.raise_for_status()
        
        data = response.json()
        
        if "errors" in data:
            print(f"Submissions not found for user {username}: {data['errors']}")
            return []
        return data.get("data", {}).get("recentSubmissionList", [])

    except httpx.HTTPStatusError as e:
        print(f"HTTP Error fetching submissions for {username}: {e.response.status_code} - {e.response.text}")
        return []
    except Exception as e:
        print(f"An error occurred fetching submissions for {username}: {e}")
        return []

def get_user_submission_count(username: str):
    """
    Fetches the total number of submissions for a given LeetCode username.
    """
    try:
        leetcode_url = LEETCODE_GRAPHQL_URL
        query = """query userPublicProfile($username: String!) {
            matchedUser(username: $username) {
                submitStats {
                    totalSubmissionNum {
                        count
                    }
                }
            }
        }"""
        
        payload = {
            "query": query,
            "variables": {"username": username},
            "operationName": "userPublicProfile"
        }
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Content-Type': 'application/json',
            'Referer': BASE_URL
        }

        response = httpx.post(leetcode_url, json=payload, headers=headers)
        response.raise_for_status()
        
        data = response.json()
        
        if not data.get("data", {}).get("matchedUser"):
            print(f"User not found: {username}")
            return None
        
        total_submission_num = data["data"]["matchedUser"]["submitStats"]["totalSubmissionNum"]
        return sum(item['count'] for item in total_submission_num)

    except httpx.HTTPStatusError as e:
        print(f"HTTP Error fetching submission count for {username}: {e.response.status_code} - {e.response.text}")
        return None
    except Exception as e:
        print(f"An error occurred fetching submission count for {username}: {e}")
        return None

async def _fetch_submissions_page(client: httpx.AsyncClient, offset: int, limit: int, headers: dict) -> Tuple[List[dict], bool]:
    variables = {"offset": offset, "limit": limit, "questionSlug": ""}
    payload = {"query": SUBMISSIONS_QUERY, "variables": variables}
    
    try:
        response = await client.post(LEETCODE_GRAPHQL_URL, json=payload, headers=headers, timeout=30)
        response.raise_for_status()
        data = response.json()

        if "errors" in data:
            if any("session" in error.get("message", "").lower() for error in data.get("errors", [])):
                print("Warning: Authentication failed during submission fetch.")
            else:
                print(f"Warning: GraphQL error on page fetch: {data['errors']}")
            return [], False

        submission_list = data.get("data", {}).get("submissionList", {})
        submissions = submission_list.get("submissions", [])
        has_next = submission_list.get("hasNext", False)
        return submissions, has_next
    except httpx.HTTPStatusError as e:
        print(f"Warning: HTTP error on page fetch: {e.response.status_code}")
        return [], False
    except Exception as e:
        print(f"An unexpected error occurred during page fetch: {e}")
        return [], False

def get_solved_questions(username: str, cookie: str, is_cn: bool = False) -> List[str]:
    """
    Fetches all solved questions for a given LeetCode username and session cookie.
    Uses asyncio for concurrent fetching of initial pages.
    """
    if not cookie:
        raise ValueError("LEETCODE_SESSION cookie is required for this operation.")

    headers = {
        "Content-Type": "application/json",
        "Cookie": f"LEETCODE_SESSION={cookie}",
        "Referer": BASE_URL,
    }

    with httpx.Client() as client:
        profile_payload = {"query": USER_PROFILE_QUERY, "variables": {"username": username}}
        try:
            response = client.post(LEETCODE_GRAPHQL_URL, json=profile_payload, headers=headers, timeout=30)
            response.raise_for_status()
            profile_data = response.json()
        except httpx.HTTPStatusError as e:
            raise Exception(f"Failed to fetch user profile: {e.response.status_code}")

    if "errors" in profile_data:
        raise Exception(f"GraphQL error on profile fetch: {profile_data['errors']}")
    
    matched_user = profile_data.get("data", {}).get("matchedUser")
    if not matched_user:
        raise Exception(f"User '{username}' not found.")

    ac_submission_num = matched_user["submitStats"]["acSubmissionNum"]
    total_solved = sum(item['count'] for item in ac_submission_num)
    
    if total_solved == 0:
        return []

    print(f"Found {total_solved} solved questions for user {username}. Fetching titles...")

    return asyncio.run(_fetch_all_solved(total_solved, headers))

async def _fetch_all_solved(total_solved: int, headers: dict) -> List[str]:
    solved_questions: Set[str] = set()
    limit = 100
    offset = 0
    has_next = True
    
    async with httpx.AsyncClient() as client:
        while has_next:
            submissions, has_next = await _fetch_submissions_page(client, offset, limit, headers)
            
            if not submissions:
                print(f"Warning: No submissions returned at offset {offset}.")
            
            for sub in submissions:
                if sub["statusDisplay"] == "Accepted":
                    solved_questions.add(sub["title"])

            offset += limit

            if offset > total_solved + (limit * 10): 
                print("Warning: Exceeded expected number of pages by a large margin. Stopping.")
                break
            
            await asyncio.sleep(0.5)

    if len(solved_questions) < total_solved:
        print(f"Warning: Fetched {len(solved_questions)} unique solved questions, but expected a total of {total_solved}.")

    if not solved_questions:
        print("Warning: Could not retrieve any solved questions despite finding a total count.")

    return list(solved_questions)
