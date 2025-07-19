import httpx

LEETCODE_GRAPHQL_URL = "https://leetcode.com/graphql"

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
