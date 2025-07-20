import requests
import json
import os
from dotenv import load_dotenv

load_dotenv()

# This script tests the Conlit API.
# To run this script, you need to install the 'requests' library:
# pip install requests

# The base URL for the local API
BASE_URL = "http://127.0.0.1:8000"
USERNAME = "sridhartuli"
LEETCODE_SESSION = os.getenv("leetcode_session")

def print_response(response):
    """Prints the status code and formatted JSON response."""
    print(f"Status Code: {response.status_code}")
    try:
        print(json.dumps(response.json(), indent=2))
    except json.JSONDecodeError:
        print("Response body is not valid JSON.")
    print("-" * 40)

def test_api():
    """Tests all available API endpoints."""
    print(f"Testing API for user: {USERNAME}\n")

    # Test /profile endpoint
    print("Testing /v1/user/{username}/profile")
    profile_url = f"{BASE_URL}/v1/user/{USERNAME}/profile"
    response = requests.get(profile_url)
    print_response(response)

    # Test /analysis endpoint (no coach)
    print("Testing /v1/user/{username}/analysis")
    analysis_url = f"{BASE_URL}/v1/user/{USERNAME}/analysis"
    response = requests.get(analysis_url)
    print_response(response)

    # Test /analysis endpoint (with coach)
    print("Testing /v1/user/{username}/analysis?coach=true")
    analysis_coach_url = f"{analysis_url}?coach=true"
    response = requests.get(analysis_coach_url)
    print_response(response)

    # Test /topic-gaps endpoint (no coach)
    print("Testing /v1/user/{username}/analysis/topic-gaps")
    topic_gaps_url = f"{BASE_URL}/v1/user/{USERNAME}/analysis/topic-gaps"
    response = requests.get(topic_gaps_url)
    print_response(response)

    # Test /topic-gaps endpoint (with coach)
    print("Testing /v1/user/{username}/analysis/topic-gaps?coach=true")
    topic_gaps_coach_url = f"{topic_gaps_url}?coach=true"
    response = requests.get(topic_gaps_coach_url)
    print_response(response)

    # Test /nemesis-problems endpoint (no coach)
    print("Testing /v1/user/{username}/analysis/nemesis-problems")
    nemesis_url = f"{BASE_URL}/v1/user/{USERNAME}/analysis/nemesis-problems"
    response = requests.get(nemesis_url)
    print_response(response)

    # Test /nemesis-problems endpoint (with coach)
    print("Testing /v1/user/{username}/analysis/nemesis-problems?coach=true")
    nemesis_coach_url = f"{nemesis_url}?coach=true"
    response = requests.get(nemesis_coach_url)
    print_response(response)

    # --- Tests with leetcode_session cookie ---
    if LEETCODE_SESSION:
        print("\n--- Testing with leetcode_session and caching ---")

        # Test /topic-gaps endpoint with session as query parameter
        print("Testing /v1/user/{username}/analysis/topic-gaps with session as query (first call)")
        topic_gaps_query_url = f"{topic_gaps_url}?leetcode_session_query={LEETCODE_SESSION}"
        response = requests.get(topic_gaps_query_url)
        print_response(response)

        print("Testing /v1/user/{username}/analysis/topic-gaps with session as query (second call - should be cached)")
        response = requests.get(topic_gaps_query_url)
        print_response(response)

        # Test /topic-gaps endpoint with session as header
        print("Testing /v1/user/{username}/analysis/topic-gaps with session as header (should be cached)")
        headers = {"leetcode_session_header": LEETCODE_SESSION}
        response = requests.get(topic_gaps_url, headers=headers)
        print_response(response)
        
        # Test /topic-gaps endpoint with session as cookie
        print("Testing /v1/user/{username}/analysis/topic-gaps with session as cookie (should be cached)")
        cookies = {"leetcode_session_cookie": LEETCODE_SESSION}
        response = requests.get(topic_gaps_url, cookies=cookies)
        print_response(response)

    else:
        print("\nSkipping session-based tests: leetcode_session not found in .env file.")


if __name__ == "__main__":
    # Clear cache before running tests
    cache_file = f"/tmp/cache/{USERNAME}_data.json"
    if os.path.exists(cache_file):
        os.remove(cache_file)
        print(f"Cleared cache file: {cache_file}")
        
    test_api()
