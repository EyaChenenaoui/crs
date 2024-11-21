import json
import csv
from typing import List, Dict

def read_json(path):
    with open(path, 'r') as file:
        df = json.load(file)
    return df


def read_txt(txt_path):
    with open(txt_path, 'r') as file:
        text = file.read()
    return text


def read_dialogue(txt_path):
    with open(txt_path, 'r', encoding='utf-8') as file:
        content = file.read()
    return content


def split_dialogues(text):
    dialogues = []
    current_number = None
    current_dialogue = ''

    lines = text.split('\n')

    for line in lines:
        if line.isdigit():
            if current_number is not None:
                dialogues.append((current_number, current_dialogue.strip()))
                current_dialogue = ''
            current_number = line
        else:
            current_dialogue += line + '\n'

    if current_number is not None and current_dialogue.strip():
        dialogues.append((current_number, current_dialogue.strip()))

    return dialogues


def get_conversation_by_id(content, conversation_id):

    lines = content.strip().split('\n\n')
    current_id = None
    conversation = []

    for line in lines:
        if line.isdigit():

            if current_id is not None and conversation:
                if current_id == conversation_id:
                    return ''.join(conversation)
                conversation = []  
            current_id = int(line) 
        else:
            conversation.append(line + '\n\n')


    if current_id == conversation_id:
        return ''.join(conversation)

    return 'Can not find the Conversation:{}'.format(conversation_id)  


def read_jsonl(path):
    with open(path, "r") as fr:
        output_lines = fr.readlines()
    return output_lines


def read_string_by_line(line_number, path):
    with open(path, 'r') as file:
        lines = file.readlines()
        if line_number < len(lines):
            return lines[line_number].strip()
        else:
            return None


def read_csv(path):
    result = []
    with open(path, mode='r', encoding='utf-8') as file:
        reader = csv.reader(file)
        for row in reader:
            result.append(row[0]) 
    return result


def read_user_data(filename, user_id):
    with open(filename, 'r', encoding='utf-8') as file:
        data = [json.loads(line) for line in file]

    for entry in data:
        if user_id in entry:
            return entry[user_id] 

    return None 


def get_item_name(item_ids:list,item_map: Dict[str, str])->list:
    """
    returns the names of movie items
    """

    items_names=[]
    for k in range(len(item_ids)):
        items_names.append(item_map[item_ids[k]])
    return items_names

def filter_list(List_1:list,List_2:list)->list:
    """
    Filter List_1 from items that exists in List_2

    """
    for item in List_1:
        if item in List_2:
                  List_1.remove(item)
    return List_1


def user_info_details (user_id:str,final_data_path:str,Conversation:str)->List:
    """
    returns the user information details

    """

    user_information = read_user_data(final_data_path, user_id)
    # read user's history_interaction
    history_interaction = user_information['history_interaction']
    # read user_might_likes
    user_might_likes = user_information['user_might_like']
    # read Conversation_info
    Conversation_info = user_information['Conversation']
    # read Conversation Detail Information
    user_likes_ids=[]
    user_dislikes_ids=[]
    dialogues=[]
    for j in range(len(Conversation_info)):
        per_conversation_info = Conversation_info[j]['conversation_{}'.format(j + 1)]
        user_likes_id=per_conversation_info['user_likes']
        user_dislikes_id = per_conversation_info['user_dislikes']
        if user_likes_id!=[]:
         user_likes_ids = user_likes_id+ user_likes_ids 
        if user_dislikes_id!=[]:
             user_dislikes_ids= user_dislikes_ids+ user_dislikes_id
        # Conversation_id could locate the dialogue
        conversation_id = per_conversation_info['conversation_id']
        # Dialogue
        dialogues.append(get_conversation_by_id(Conversation, conversation_id))
    return dialogues , user_likes_ids, user_dislikes_ids, user_might_likes, history_interaction