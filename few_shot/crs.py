import sys
import os
from langchain_groq import ChatGroq
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from dotenv import load_dotenv
import random
import asyncio
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(PROJECT_ROOT)

from Utils.Tools import read_dialogue,user_info_details
final_data_path = os.path.join(PROJECT_ROOT, "Movie", "final_data.jsonl")
Conversation_path = os.path.join(PROJECT_ROOT, "Movie", "Conversation.txt")
chat_groq_model = None
async def init_resources():
    """
    Initialize and cache global resources
    """
    global chat_groq_model

    if chat_groq_model is None:
        chat_groq_model = ChatGroq(temperature=0.7, model="llama3-70b-8192")

def few_shot_examples_formatting(dialogues:list)->str:
    """ 
    return few shot examples in a good format

    """
    current_example = 1
    few_shot = []
    for dialogue in dialogues:
        prompt = f"### Example {current_example} :\n"
        prompt += f"### Conversation History:\n{dialogue}\n"
        few_shot.append(prompt)
        current_example += 1
    
    few_shot_examples = "\n".join(few_shot)
    return few_shot_examples


async def generate_response(query: str, user_id:str) -> str:
    """
    Generate a response to the user's query based on their previous dialogues.
    """
    try:
        await init_resources()
        load_dotenv()
    
        #few shot data 
        Conversation = await asyncio.to_thread(read_dialogue, Conversation_path)
        dialogues, _, _, _, _   = await asyncio.to_thread(user_info_details, user_id, final_data_path, Conversation)
        if len(dialogues)>1:
            random_dialogues = random.sample(dialogues, 2)
            examples=few_shot_examples_formatting(random_dialogues)
        else:
            examples=few_shot_examples_formatting(dialogues)
        # prompt template
        prompt_template = PromptTemplate(
                input_variables=["examples", "query"],
                template="""You are a conversational agent specialized in recommending movies. 
            Here are examples of past recommendations in the conversation you had with him:
            {examples}

            Based on the above, answer the query:
            Query: {query}
            The Answer shouldn't be long .
            Answer:
                                    """
            )
      
        chain = LLMChain(llm=chat_groq_model, prompt=prompt_template)

        response = await asyncio.to_thread(chain.run, {
            "examples": examples,
            "query": query
        })
        return response
    except Exception as e:
            raise ValueError(f"Error generating response: {e}")

