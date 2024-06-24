import os
import pathlib
import time
import ujson
import logging

# Define the constants for memory folders
MEMORY_FOLDER = "./memory/"
STM_FOLDER = MEMORY_FOLDER + "stm/"
LTM_FOLDER = MEMORY_FOLDER + "ltm/"
EPISODIC_FOLDER = MEMORY_FOLDER + "episodic/"
TRUTH_FOLDER = MEMORY_FOLDER + "truth/"
MINDX_FOLDER = "./mindx/"
AGENCY_FOLDER = MINDX_FOLDER + "agency/"

class DialogEntry:
    def __init__(self, instruction, response):
        self.instruction = instruction
        self.response = response

def create_memory_folders():
    try:
        if not pathlib.Path(MEMORY_FOLDER).exists():
            pathlib.Path(MEMORY_FOLDER).mkdir(parents=True)
        if not pathlib.Path(STM_FOLDER).exists():
            pathlib.Path(STM_FOLDER).mkdir(parents=True)
        if not pathlib.Path(LTM_FOLDER).exists():
            pathlib.Path(LTM_FOLDER).mkdir(parents=True)
        if not pathlib.Path(EPISODIC_FOLDER).exists():
            pathlib.Path(EPISODIC_FOLDER).mkdir(parents=True)
        if not pathlib.Path(TRUTH_FOLDER).exists():
            pathlib.Path(TRUTH_FOLDER).mkdir(parents=True)
        if not pathlib.Path(MINDX_FOLDER).exists():
            pathlib.Path(MINDX_FOLDER).mkdir(parents=True)
        if not pathlib.Path(AGENCY_FOLDER).exists():
            pathlib.Path(AGENCY_FOLDER).mkdir(parents=True)
    except Exception as e:
        logging.error(f"Error creating memory folders: {e}")

def store_in_stm(dialog_entry):
    filename = f"{int(time.time())}.json"
    filepath = os.path.join(STM_FOLDER, filename)
    with open(filepath, "w") as file:
        ujson.dump(dialog_entry.__dict__, file)

def store_in_ltm(dialog_entry):
    filename = f"{int(time.time())}.json"
    filepath = os.path.join(LTM_FOLDER, filename)
    with open(filepath, "w") as file:
        ujson.dump(dialog_entry.__dict__, file)

def store_episodic_memory(episode):
    filename = f"{int(time.time())}.json"
    filepath = os.path.join(EPISODIC_FOLDER, filename)
    with open(filepath, "w") as file:
        ujson.dump(episode, file)

def save_valid_truth(valid_truth):
    filename = f"{int(time.time())}.json"
    filepath = os.path.join(TRUTH_FOLDER, filename)
    with open(filepath, "w") as file:
        ujson.dump(valid_truth, file)

def save_conversation_memory(memory):
    create_memory_folders()

    # Generate unique filenames based on the timestamp
    timestamp = str(int(time.time()))

    # Save to Short-Term Memory (STM) if the conversation is less than 30 seconds old
    if time.time() - memory.timestamp < 30:
        stm_filename = f"{STM_FOLDER}{timestamp}.json"
        with open(stm_filename, 'w') as f:
            ujson.dump(memory.dialog, f)

    # Save to Long-Term Memory (LTM) after 30 seconds
    elif time.time() - memory.timestamp >= 30:
        ltm_filename = f"{LTM_FOLDER}{timestamp}.json"
        with open(ltm_filename, 'w') as f:
            ujson.dump(memory.dialog, f)

    # Save to Episodic Memory
    episodic_filename = f"{EPISODIC_FOLDER}{timestamp}.json"
    with open(episodic_filename, 'w') as f:
        ujson.dump(memory.to_episodic(), f)

    return timestamp

def load_conversation_memory():
    create_memory_folders()
    memory_files = list(pathlib.Path(MEMORY_FOLDER).glob("*.json"))

    all_memory = []
    for file_path in memory_files:
        with open(file_path, "r", encoding="utf-8") as file:
            memory = ujson.load(file)
            all_memory.extend(memory)

    return all_memory

def delete_conversation_memory():
    create_memory_folders()
    memory_files = list(pathlib.Path(MEMORY_FOLDER).glob("*.json"))

    for file_path in memory_files:
        file_path.unlink()

def get_latest_memory():
    create_memory_folders()
    memory_files = sorted(pathlib.Path(MEMORY_FOLDER).glob("*.json"), key=lambda p: p.stat().st_mtime, reverse=True)

    if not memory_files:
        return []

    latest_file = memory_files[0]
    with open(latest_file, "r", encoding="utf-8") as file:
        memory = ujson.load(file)

    return memory
