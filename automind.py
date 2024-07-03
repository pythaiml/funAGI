import logging
from memory.memory import create_memory_folders, store_in_stm, DialogEntry
from agi import AGI
from chatter import GPT4o, GroqModel

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('FundamentalAGI')

class FundamentalAGI:
    def __init__(self, chatter):
        self.agi = self.initialize_agi(chatter)
        self.initialize_memory()

    def initialize_memory(self):
        create_memory_folders()
        logger.info("Memory folders initialized.")
    
    def initialize_agi(self, chatter):
        return AGI(chatter)

    def main_loop(self):
        """
        Main loop for interacting with the environment and making decisions.
        """
        while True:
            environment_data = self.perceive_environment()
            if environment_data.lower() == 'exit':
                break

            self.agi.reasoning.add_premise(environment_data)
            conclusion = self.agi.reasoning.draw_conclusion()
            self.communicate_response(conclusion)

            entry = DialogEntry(environment_data, conclusion)
            store_in_stm(entry)
            logger.info(f"Stored dialog entry: {entry}")

    def perceive_environment(self):
        """
        Get input from the user.
        """
        agi_prompt = input("Enter the problem to solve (or type 'exit' to quit): ")
        return agi_prompt

    def communicate_response(self, conclusion):
        """
        Log and print the conclusion.
        """
        logging.info(f"Communicating response: {conclusion}")
        print(conclusion)

    def get_conclusion_from_agi(self, prompt):
        self.agi.reasoning.add_premise(prompt)
        conclusion = self.agi.reasoning.draw_conclusion()
        return conclusion

def main():
    openai_key = input("Enter OpenAI API Key: ").strip()
    groq_key = input("Enter Groq API Key: ").strip()
    
    if openai_key:
        chatter = GPT4o(openai_key)
    elif groq_key:
        chatter = GroqModel(groq_key)
    else:
        print("No suitable API key found. Exiting.")
        return
    
    fundamental_agi = FundamentalAGI(chatter)
    fundamental_agi.main_loop()

if __name__ == "__main__":
    main()

