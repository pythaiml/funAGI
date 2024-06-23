# memory.py
import os
import json
import datetime
import pathlib

def create_memory_folders():
    paths = ['./memory/conversations', './memory/truth']
    for path in paths:
        pathlib.Path(path).mkdir(parents=True, exist_ok=True)

def save_conversation_memory(conversation_id, conversation_data):
    path = f'./memory/conversations/{conversation_id}.json'
    with open(path, 'w') as file:
        json.dump(conversation_data, file, indent=4)

def load_conversation_memory(conversation_id):
    path = f'./memory/conversations/{conversation_id}.json'
    if os.path.exists(path):
        with open(path, 'r') as file:
            return json.load(file)
    return None

def delete_conversation_memory(conversation_id):
    path = f'./memory/conversations/{conversation_id}.json'
    if os.path.exists(path):
        os.remove(path)

def store_in_stm(dialog_entry):
    timestamp = datetime.datetime.now().isoformat()
    entry = {
        "timestamp": timestamp,
        "data": dialog_entry
    }
    stm_path = './memory/short_term_memory.json'
    if os.path.exists(stm_path):
        with open(stm_path, 'r') as file:
            stm = json.load(file)
    else:
        stm = []

    stm.append(entry)
    with open(stm_path, 'w') as file:
        json.dump(stm, file, indent=4)

def save_valid_truth(valid_truth):
    truth_path = './memory/truth/valid_truths.json'
    if os.path.exists(truth_path):
        with open(truth_path, 'r') as file:
            truths = json.load(file)
    else:
        truths = []

    truths.append(valid_truth)
    with open(truth_path, 'w') as file:
        json.dump(truths, file, indent=4)

class DialogEntry:
    def __init__(self, input_data, output_data):
        self.input_data = input_data
        self.output_data = output_data
