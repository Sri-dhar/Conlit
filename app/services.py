from app.data_manager import DataManager
from app import analyzer
from app import llm_coach
from app import leetcode_client

def get_user_profile(username: str):
    """
    Get a user's LeetCode profile.
    """
    return leetcode_client.get_user_profile(username)

def get_full_analysis(username: str, coach: bool, data_manager: DataManager, leetcode_session: str = None):
    """
    Get a full analysis for a user, with an option for AI coaching.
    """
    if coach:
        return llm_coach.generate_coaching_plan(username, data_manager)
    
    return {
        "performance_summary": analyzer.generate_performance_summary(username, data_manager),
        "topic_gaps": analyzer.analyze_topic_gaps(username, data_manager, leetcode_session),
        "nemesis_problems": analyzer.find_nemesis_problems(username, data_manager, leetcode_session)
    }

def get_topic_gaps_analysis(username: str, coach: bool, data_manager: DataManager, leetcode_session: str = None):
    """
    Get topic gaps analysis, with an option for AI coaching.
    """
    if coach:
        return llm_coach.generate_topic_gap_report(username, data_manager)
    return analyzer.analyze_topic_gaps(username, data_manager, leetcode_session)

def get_nemesis_problems_analysis(username: str, coach: bool, data_manager: DataManager, leetcode_session: str = None):
    """
    Get nemesis problems analysis, with an option for AI coaching.
    """
    if coach:
        return llm_coach.generate_nemesis_problem_advice(username, data_manager)
    return analyzer.find_nemesis_problems(username, data_manager, leetcode_session)
