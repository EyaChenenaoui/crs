import sys
import os
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(PROJECT_ROOT)
from langchain_community.vectorstores import FAISS
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from Utils.Tools import read_json
from dotenv import load_dotenv
from typing import  Dict

MOVIE_VECTOR_INDEX_PATH ='./vectors/movie_retriever' 
item_map_path = os.path.join(PROJECT_ROOT, "Movie", "item_map.json")


def create_full_movie_vector_db(item_map: Dict[str, str], save_path: str) -> None:
    """
    Create a centralized vector database for all movie items.
    """
    movie_texts = [f"{movie_id}: {name}" for movie_id, name in item_map.items()]
    metadata_list = [{"name": name} for name in item_map.values()]

    embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
    vector_db = FAISS.from_texts(movie_texts, embeddings, metadatas=metadata_list)

    vector_db.save_local(save_path)
if __name__=='__main__':
    load_dotenv()
    item_map = read_json(item_map_path)
    create_full_movie_vector_db(item_map,MOVIE_VECTOR_INDEX_PATH )