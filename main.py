import os
import sys
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from RAG.crs import generate_response as rag_generate_response
from few_shot.crs import generate_response as few_shot_generate_response
from Utils.Tools import read_json

PROJECT_ROOT: str = os.path.abspath(os.path.join(os.path.dirname(__file__), '.'))
USER_MAP_PATH: str = os.path.join(PROJECT_ROOT, "Movie", "user_ids.json")

sys.path.append(PROJECT_ROOT)


class UserRequest(BaseModel):
    user_id: str = ""
    query: str = ""
    method: str = "few shot"


def validate_request(user_request: UserRequest) -> None:
    """
    Validate the incoming user request.
    """
    user_map = read_json(USER_MAP_PATH)
    user_id = user_request.user_id
    query = user_request.query
    method = user_request.method.lower()

    if user_id not in user_map:
        raise ValueError(f"User ID '{user_id}' is not registered.")
    if method not in ["few shot", "rag"]:
        raise ValueError(f"Invalid method '{method}'. Supported methods are 'rag' and 'few shot'.")
    if query == "":
        raise ValueError("Query cannot be empty.")


app = FastAPI()

@app.post("/recommend/")
async def recommend_movies(user_request: UserRequest) -> dict:
    """
    Recommends movies using the specified method.
    """
    try:
        # Validate user request
        validate_request(user_request)
        user_id = user_request.user_id
        query = user_request.query
        method = user_request.method.lower()

        if method == "rag":
            response = await rag_generate_response(query, user_id)
        else:
            response = await few_shot_generate_response(query, user_id)

        return {"response": response}

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")
