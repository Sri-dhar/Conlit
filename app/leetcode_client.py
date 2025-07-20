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
            'Content-Type': 'application/json'
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

def get_solved_questions(username: str, cookie: str, is_cn: bool = False):
    """
    Fetches all solved questions for a given LeetCode username and session cookie.
    """
    if not cookie:
        raise ValueError("LEETCODE_SESSION cookie is required for this operation.")

    base_url = BASE_URL
    graphql_url = f"{base_url}/graphql"
    
    headers = {
        "Content-Type": "application/json",
        "Cookie": f"LEETCODE_SESSION={cookie}",
        "Referer": base_url,
    }

    profile_payload = {
        "query": USER_PROFILE_QUERY,
        "variables": {"username": username},
    }
    
    try:
        response = httpx.post(graphql_url, json=profile_payload, headers=headers, timeout=30)
        response.raise_for_status()
        profile_data = response.json()
    except httpx.HTTPStatusError as e:
        raise Exception(f"Failed to fetch user profile: {e.response.status_code}")
    
    if "errors" in profile_data:
        # Check for auth-related errors
        if any("session" in error.get("message", "").lower() for error in profile_data["errors"]):
            raise Exception("Authentication failed. Your LEETCODE_SESSION cookie may be invalid or expired.")
        raise Exception(f"GraphQL error on profile fetch: {profile_data['errors']}")

    matched_user = profile_data.get("data", {}).get("matchedUser")
    if not matched_user:
        raise Exception(f"User '{username}' not found.")

    ac_submission_num = matched_user["submitStats"]["acSubmissionNum"]
    total_solved = sum(item['count'] for item in ac_submission_num)
    
    if total_solved == 0:
        return []

    print(f"Found {total_solved} solved questions for user {username}. Fetching titles...")

    solved_questions = set()
    offset = 0
    limit = 20
    page_num = 0

    while len(solved_questions) < total_solved:
        page_num += 1
        if page_num > (total_solved // limit) + 5: # Increased safeguard
            print("Warning: Exceeded expected number of pages. Terminating.")
            break

        variables = {"offset": offset, "limit": limit, "questionSlug": ""}
        payload = {"query": SUBMISSIONS_QUERY, "variables": variables}
        
        try:
            response = httpx.post(graphql_url, json=payload, headers=headers, timeout=30)
            response.raise_for_status()
            data = response.json()
        except httpx.HTTPStatusError as e:
            print(f"Warning: HTTP error on page {page_num}: {e.response.status_code}")
            break # Stop fetching on error

        if "errors" in data:
            if any("session" in error.get("message", "").lower() for error in data["errors"]):
                print("Warning: Authentication failed while fetching submissions. Returning partial list.")
                break
            print(f"Warning: GraphQL error on page {page_num}: {data['errors']}")
            break

        submission_list = data.get("data", {}).get("submissionList")
        if not submission_list or not submission_list.get("submissions"):
            print(f"Warning: No submissions found on page {page_num}. Ending fetch.")
            break

        submissions = submission_list["submissions"]
        found_new = False
        for sub in submissions:
            if sub["statusDisplay"] == "Accepted":
                if sub["title"] not in solved_questions:
                    solved_questions.add(sub["title"])
                    found_new = True
        
        if not found_new and page_num > 1:
            print("Warning: No new solved questions found. The API might be returning duplicates.")
            break

        offset += limit

    if not solved_questions:
        print("Warning: Could not retrieve any solved questions. Check your LEETCODE_SESSION cookie.")

    return list(solved_questions)
