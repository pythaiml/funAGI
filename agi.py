# agi.py
import logging
import json
import os
from SocraticReasoning import SocraticReasoning
from memory import save_conversation_memory, load_conversation_memory, delete_conversation_memory, create_memory_folders, store_in_stm, DialogEntry
from api import APIManager
from chatter import GPT4o

class AGI:
    def __init__(self, api_manager):
        self.api_manager = api_manager
        self.chatter = GPT4o(api_manager.get_api_key('openai'))
        self.reasoning = SocraticReasoning(self.chatter)

    def learn_from_data(self, data):
        # For simplicity, let's assume the input data is split into two propositions
        propositions = data.split(';')
        if len(propositions) >= 2:
            proposition_p = propositions[0].strip()
            proposition_q = propositions[1].strip()
        else:
            proposition_p = data.strip()
            proposition_q = ""

        self.reasoning.add_premise(proposition_p)
        self.reasoning.add_premise(proposition_q)

        return proposition_p, proposition_q

    def make_decisions(self, proposition_p, proposition_q):
        self.reasoning.draw_conclusion()
        decision = self.reasoning.logical_conclusion
        return decision

class EasyAGI:
    def __init__(self):
        self.api_manager = APIManager()
        self.manage_api_keys()
        self.agi = AGI(self.api_manager)
        self.initialize_memory()

    def initialize_memory(self):
        create_memory_folders()

    def manage_api_keys(self):
        while True:
            self.api_manager.list_api_keys()
            action = input("Choose an action: (a) Add API key, (d) Delete API key, (l) List API keys, (Press Enter to continue): ").strip().lower()
            if not action:
                break
            elif action == 'a':
                self.api_manager.add_api_key_interactive()
            elif action == 'd':
                api_name = input("Enter the API name to delete: ").strip()
                if api_name:
                    self.api_manager.remove_api_key(api_name)
            elif action == 'l':
                self.api_manager.list_api_keys()

    def main_loop(self):
        while True:
            environment_data = self.perceive_environment()
            if environment_data.lower() == 'exit':
                break

            proposition_p, proposition_q = self.agi.learn_from_data(environment_data)
            decision = self.agi.make_decisions(proposition_p, proposition_q)
            self.communicate_response(decision)

            entry = DialogEntry(environment_data, decision)
            store_in_stm(entry)

    def perceive_environment(self):
        agi_prompt = input("") # environment is empty prompt
        return agi_prompt

    def communicate_response(self, decision):
        logging.info(f"Communicating response: {decision}")
        print(decision)

def main():
    easy_agi = EasyAGI()
    easy_agi.main_loop()

if __name__ == "__main__":
    main()
