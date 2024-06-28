import openai
import logging
from memory import create_memory_folders, store_in_stm, DialogEntry
from agi import AGI
from api import APIManager
from chatter import GPT4o, GroqModel

class FundamentalAGI:
    def __init__(self):
        self.api_manager = APIManager()
        self.manage_api_keys()
        self.agi = self.initialize_agi()
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

    def initialize_agi(self):
        openai_key = self.api_manager.get_api_key('openai')
        groq_key = self.api_manager.get_api_key('groq')
        
        if openai_key:
            chatter = GPT4o(openai_key)
        elif groq_key:
            chatter = GroqModel(groq_key)
        else:
            print("No suitable API key found. Please add an API key.")
            self.manage_api_keys()
            return self.initialize_agi()
        
        return AGI(chatter)

    def main_loop(self):
        while True:
            environment_data = self.perceive_environment()
            if environment_data.lower() == 'exit':
                break

            self.agi.reasoning.add_premise(environment_data)
            conclusion = self.agi.reasoning.draw_conclusion()
            self.communicate_response(conclusion)

            entry = DialogEntry(environment_data, conclusion)
            store_in_stm(entry)

    def perceive_environment(self):
        agi_prompt = input("Enter the problem to solve (or type 'exit' to quit): ")
        return agi_prompt

    def communicate_response(self, conclusion):
        logging.info(f"Communicating response: {conclusion}")
        print(conclusion)

def main():
    fundamental_agi = FundamentalAGI()
    fundamental_agi.main_loop()

if __name__ == "__main__":
    main()
