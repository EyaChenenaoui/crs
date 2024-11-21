import sys
import os
from langchain_groq import ChatGroq
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain_community.vectorstores import FAISS
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from dotenv import load_dotenv
from typing import List, Dict
import asyncio

# Define project paths
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(PROJECT_ROOT)

from Utils.Tools import read_dialogue, read_json, user_info_details, get_item_name, filter_list

MOVIE_VECTOR_INDEX_PATH = os.path.join(PROJECT_ROOT, "RAG", "vectors", "movie_retriever")

final_data_path = os.path.join(PROJECT_ROOT, "Movie", "final_data.jsonl")
Conversation_path = os.path.join(PROJECT_ROOT, "Movie", "Conversation.txt")
item_map_path = os.path.join(PROJECT_ROOT, "Movie", "item_map.json")

chat_groq_model = None
faiss_vector_db = None

async def init_resources()->None:
    """
    Initialize and cache global resources
    """
    global chat_groq_model, faiss_vector_db

    if chat_groq_model is None:
        chat_groq_model = ChatGroq(temperature=0.3, model="llama3-70b-8192")
    
    if faiss_vector_db is None:
        embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
        faiss_vector_db = await asyncio.to_thread(
            lambda: FAISS.load_local(MOVIE_VECTOR_INDEX_PATH, embeddings, allow_dangerous_deserialization=True)
        )
async def filter_personalized_movies(recommended_ids: List[str], item_map: Dict[str, str]) -> FAISS:

    """
    Create a personalized FAISS database for movie recommendations.
    """

    personalized_movie_texts = [f"{movie_id}: {item_map[movie_id]}" for movie_id in recommended_ids]
    embeddings = faiss_vector_db.embeddings
    personalized_db = FAISS.from_texts(personalized_movie_texts, embeddings)
    return personalized_db


async def generate_response(query: str, user_id: str) -> str:
    """ 
    Generate a personalized response to the user's query.
     
    """
    try:
        await init_resources()
        load_dotenv()
        item_map, Conversation = await asyncio.gather(
            asyncio.to_thread(read_json, item_map_path),
            asyncio.to_thread(read_dialogue, Conversation_path)
        )

        _, user_likes_item, user_dislikes_item, user_might_likes, history_interaction = await asyncio.to_thread(
            user_info_details, user_id, final_data_path, Conversation
        )

        # Filter out disliked items from the interaction history
        history_interaction = filter_list(history_interaction, user_dislikes_item)
        movie_retriever= await filter_personalized_movies(user_might_likes + history_interaction, item_map)

        # Retrieve relevant movies and dialogues based on the user's query
        recommended_movies = await asyncio.to_thread(movie_retriever.similarity_search, query,3)
        hated_movies = get_item_name(user_dislikes_item, item_map)
        liked_movies = get_item_name(user_likes_item, item_map)
       # Create the prompt template
        prompt_template = PromptTemplate(
            input_variables=["hated_movies", "liked_movies", "recommended_movies", "query"],
            template="""
            You are a conversational agent specialized in recommending movies based on the following user preferences:
            - Hated Movies: {hated_movies}
            - Liked Movies: {liked_movies}
            - Recommended Movies: {recommended_movies}
            - Query: {query}
            Generate not long response in a conversational tone that includes personalized recommendations.
            """
        )

        # Create and execute the LLMChain
        chain = LLMChain(llm=chat_groq_model, prompt=prompt_template)
        response = await asyncio.to_thread(chain.run, {
            "hated_movies": hated_movies,
            "liked_movies": liked_movies,
            "recommended_movies": recommended_movies,
            "query": query
        })

        return response

    except Exception as e:
        raise ValueError(f"Error generating response: {e}")
