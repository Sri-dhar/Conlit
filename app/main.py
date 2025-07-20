from fastapi import FastAPI, Depends, Header, Cookie, Response
from typing import Optional
from app.data_manager import DataManager
from app import services

app = FastAPI(
    title="Conlit API",
    description="An API for analyzing LeetCode contest performance.",
    version="1.0.0",
)
data_manager = DataManager()

@app.on_event("startup")
def startup_event():
    data_manager.load_and_index_data()

def get_data_manager():
    return data_manager

@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    return Response(status_code=204)

@app.get("/")
def read_root():
    return {
        "message": "Welcome to the Conlit API!",
        "docs": "/docs",
        "redoc": "/redoc",
        "paths": [route.path for route in app.routes]
    }

@app.get("/v1/user/{username}/profile")
def get_user_profile(username: str):
    return services.get_user_profile(username)

@app.get("/v1/user/{username}/analysis")
def get_user_analysis(
    username: str,
    coach: bool = False,
    leetcode_session_query: Optional[str] = None,
    leetcode_session_cookie: Optional[str] = Cookie(None),
    leetcode_session_header: Optional[str] = Header(None),
    dm: DataManager = Depends(get_data_manager)
):
    leetcode_session = leetcode_session_query or leetcode_session_cookie or leetcode_session_header
    return services.get_full_analysis(username, coach, dm, leetcode_session)

@app.get("/v1/user/{username}/analysis/topic-gaps")
def get_topic_gaps(
    username: str,
    coach: bool = False,
    leetcode_session_query: Optional[str] = None,
    leetcode_session_cookie: Optional[str] = Cookie(None),
    leetcode_session_header: Optional[str] = Header(None),
    dm: DataManager = Depends(get_data_manager)
):
    leetcode_session = leetcode_session_query or leetcode_session_cookie or leetcode_session_header
    return services.get_topic_gaps_analysis(username, coach, dm, leetcode_session)

@app.get("/v1/user/{username}/analysis/nemesis-problems")
def get_nemesis_problems(
    username: str,
    coach: bool = False,
    leetcode_session_query: Optional[str] = None,
    leetcode_session_cookie: Optional[str] = Cookie(None),
    leetcode_session_header: Optional[str] = Header(None),
    dm: DataManager = Depends(get_data_manager)
):
    leetcode_session = leetcode_session_query or leetcode_session_cookie or leetcode_session_header
    return services.get_nemesis_problems_analysis(username, coach, dm, leetcode_session)
