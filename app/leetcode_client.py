import httpx
import os

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
            'Content-Type': 'application/json'
        }

        response = httpx.post(leetcode_url, json=payload, headers=headers)
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
            'Content-Type': 'application/json'
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
            'Content-Type': 'application/json'
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

def get_solved_questions(username: str, cookie: str, is_cn: bool = False):
    """
    Fetches all solved questions for a given LeetCode username and session cookie.

    Args:
        username: The LeetCode username.
        cookie: The LEETCODE_SESSION cookie.
        is_cn: Whether to use the Chinese LeetCode site.

    Returns:
        A list of solved question titles.
    """
    base_url = BASE_URL
    graphql_url = f"{base_url}/graphql"
    
    headers = {
        "Content-Type": "application/json",
        "Cookie": f"LEETCODE_SESSION={cookie}",
        "Referer": base_url,
    }

    # Get total number of solved questions
    profile_payload = {
        "query": USER_PROFILE_QUERY,
        "variables": {"username": username},
    }
    response = httpx.post(graphql_url, json=profile_payload, headers=headers)
    profile_data = response.json()
    
    if "errors" in profile_data:
        raise Exception(f"GraphQL error: {profile_data['errors']}")

    if not profile_data.get("data", {}).get("matchedUser"):
        raise Exception(f"User '{username}' not found.")

    ac_submission_num = profile_data["data"]["matchedUser"]["submitStats"]["acSubmissionNum"]
    total_solved = sum(item['count'] for item in ac_submission_num)
    
    print(f"Found {total_solved} solved questions for user {username}. Fetching titles...")

    solved_questions = set()
    offset = 0
    limit = 20

    page_num = 0
    while len(solved_questions) < total_solved:
        page_num += 1
        # Safeguard against infinite loops
        if page_num > (total_solved // limit) + 2:
            print("Warning: Exceeded expected number of pages. Terminating.")
            break

        variables = {
            "offset": offset,
            "limit": limit,
            "questionSlug": "",
        }
        
        payload = {
            "query": SUBMISSIONS_QUERY,
            "variables": variables,
        }
        
        response = httpx.post(graphql_url, json=payload, headers=headers)
        data = response.json()

        print(f"Fetched page {offset // limit + 1}...")

        if "errors" in data:
            # Check for authentication errors
            if "user" in str(data["errors"]).lower():
                raise Exception("Authentication failed. Please check your LEETCODE_SESSION cookie.")
            raise Exception(f"GraphQL error: {data['errors']}")

        submission_list = data.get("data", {}).get("submissionList")
        if not submission_list:
            raise Exception("Failed to fetch submissions. The API response might have changed.")

        submissions = submission_list.get("submissions") or []
        for submission in submissions:
            if submission["statusDisplay"] == "Accepted":
                solved_questions.add(submission["title"])

        # Check for authentication issues after the first page
        if page_num == 1 and total_solved > 0 and len(solved_questions) == 0:
            print("Warning: No accepted submissions found on the first page.")
            print("Please ensure your LEETCODE_SESSION cookie is valid.")

        offset += limit

    return list(solved_questions)
