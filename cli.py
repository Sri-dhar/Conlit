import typer
import json
from app.data_manager import DataManager
from app import services
import pdb

app = typer.Typer()

@app.command()
def user_profile(username: str):
    """
    Get a user's LeetCode profile.
    """
    profile = services.get_user_profile(username)
    if profile:
        print(json.dumps(profile, indent=2))
    else:
        print(f"Could not find profile for user: {username}")

@app.command()
def analyze(username: str, coach: bool = typer.Option(False, "--coach", help="Get AI-powered coaching advice.")):
    """
    Run analysis for a user.
    """
    data_manager = DataManager()
    data_manager.load_and_index_data()
    
    result = services.get_full_analysis(username, coach, data_manager)
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    app()
