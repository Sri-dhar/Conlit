import requests
import json

# This script tests the deployed Conlit API.
# To run this script, you need to install the 'requests' library:
# pip install requests

BASE_URL = "https://conlit.vercel.app/"
USERNAME = "sridhartuli"

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


if __name__ == "__main__":
    test_api()
