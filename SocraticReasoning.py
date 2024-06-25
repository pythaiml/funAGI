import logging
import pathlib
import ujson
from chatter import GPT4o, GroqModel, OllamaModel
from logic import LogicTables
from memory import create_memory_folders, store_in_stm, DialogEntry

class SocraticReasoning:
    def __init__(self, chatter):
        self.premises = []
        self.logger = logging.getLogger('SocraticReasoning')
        self.logger.setLevel(logging.DEBUG)                            # set to DEBUG to capture all SocraticReasoing logs
        file_handler = logging.FileHandler('./mindx/socraticlog.txt')  # save socraticreasoning to ./mindx/socraticlog.txt
        self.premises_file = './mindx/premises.json'                   # save premises to ./mindx/premises.json
        self.not_premises_file = './mindx/notpremise.json'             # save not premise to ./mindx/notpremise.json
        file_handler.setLevel(logging.DEBUG)
        file_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(file_formatter)
        
        # Stream handler to suppress lower-level logs in the terminal
        stream_handler = logging.StreamHandler()
        stream_handler.setLevel(logging.CRITICAL)                      # show only critical logs in the terminal
        stream_formatter = logging.Formatter('%(message)s')
        stream_handler.setFormatter(stream_formatter)

        self.logger.addHandler(file_handler)
        self.logger.addHandler(stream_handler)

        self.max_tokens = 100                                         # default max tokens for socratic premise from add_premise(statement)
        self.chatter = chatter
        self.logic_tables = LogicTables()
        self.dialogue_history = []
        self.logical_conclusion = ""                                  # conclusion is solution

        create_memory_folders()                                       # ensure folders are created

    def log(self, message, level='info'):
        if level == 'info':
            self.logger.info(message)
        elif level == 'error':
            self.logger.error(message)
        self.store_log_in_mindx(message, level)                       # save socraticreasoning to ./mindx/socraticlog.txt

    def store_log_in_mindx(self, message, level):
        mindx_path = './mindx/errors/log.txt'
        pathlib.Path(mindx_path).parent.mkdir(parents=True, exist_ok=True)
        with open(mindx_path, 'a') as file:
            file.write(f"{level.upper()}: {message}\n")

    def log_not_premise(self, message, level='info'):
        not_premises_path = self.not_premises_file
        pathlib.Path(not_premises_path).parent.mkdir(parents=True, exist_ok=True)
        entry = {"level": level.upper(), "message": message}
        try:
            with open(not_premises_path, 'r') as file:
                logs = ujson.load(file)
        except (FileNotFoundError, ValueError):
            logs = []

        logs.append(entry)
        with open(not_premises_path, 'w') as file:
            ujson.dump(logs, file, indent=2)

    def save_premises(self):
        pathlib.Path(self.premises_file).parent.mkdir(parents=True, exist_ok=True)
        with open(self.premises_file, 'w') as file:
            ujson.dump(self.premises, file, indent=2)

    def add_premise(self, premise):
        if self.parse_statement(premise):
            self.premises.append(premise)
            #self.log(f'Added premise: {premise}')
            self.save_premises()
        else:
            #self.log(f'Invalid premise: {premise}', level='error')                 # uncomment to log not premise to terminal
            self.log_not_premise(f'Invalid premise: {premise}', level='error')      # save not premise to ./mindx/notpremise.json

    def parse_statement(self, statement):
        # Simple parser to validate statements
        return isinstance(statement, str) and len(statement) > 0

    def challenge_premise(self, premise):
        if premise in self.premises:
            self.premises.remove(premise)
            self.log(f'Challenged and removed premise: {premise}')
            self.remove_equivalent_premises(premise)
            self.save_premises()                                                    # save is premise to ./mindx/premises.json
        else:
            self.log_not_premise(f'Premise not found: {premise}', level='error')    # save not premise to ./mindx/notpremise.json

    def remove_equivalent_premises(self, premise):
        equivalent_premises = [p for p in self.premises if self.logic_tables.unify_variables(premise, p)]
        for p in equivalent_premises:
            self.premises.remove(p)
            self.log_not_premise(f'Removed equivalent premise: {p}')
        self.save_premises()

#    def draw_conclusion(self):
#        if not self.premises:
#            self.log('No premises available for logic as conclusion.', level='error')
#            return "No premises available for logic as conclusion."
#
#        premise_text = " ".join(f"{premise}" for premise in self.premises)
#        prompt = f"{premise_text} Conclusion?"
#
#        self.logical_conclusion = self.chatter.generate_response(prompt)
#        # Commented out to avoid duplication in the response
#        #self.log(f"{self.logical_conclusion}")  # log the conclusion directly in the terminal response
#
#        if not self.validate_conclusion():
#            #self.log('Invalid conclusion. Revise.', level='error')
#            self.log_not_premise('Invalid conclusion. Revise.', level='error')
#
#        conclusion_entry = {"premises": self.premises, "conclusion": self.logical_conclusion}
#        pathlib.Path(self.premises_file).parent.mkdir(parents=True, exist_ok=True)
#        with open(self.premises_file, 'w') as file:
#            ujson.dump(conclusion_entry, file, indent=2)
#
#        return premise_text + " " + self.logical_conclusion

    def draw_conclusion(self):
        if not self.premises:
            self.log('No premises available for logic as conclusion.', level='error')
            return "No premises available for logic as conclusion."

        # Create a single string from the premises
        premise_text = " ".join(f"{premise}" for premise in self.premises)

        # Use the premise_text as the input (knowledge) for generating a response
        raw_response = self.chatter.generate_response(premise_text)

        # Process the response to get the conclusion
        conclusion = raw_response.strip()

        self.logical_conclusion = conclusion

        if not self.validate_conclusion():
            self.log_not_premise('Invalid conclusion. Revise.', level='error')
  
        conclusion_entry = {"premises": self.premises, "conclusion": self.logical_conclusion}
        pathlib.Path(self.premises_file).parent.mkdir(parents=True, exist_ok=True)
        with open(self.premises_file, 'w') as file:
            ujson.dump(conclusion_entry, file, indent=2)

        # Return only the conclusion without the premise text
        return self.logical_conclusion


    def validate_conclusion(self):
        return self.logic_tables.tautology(self.logical_conclusion)

    def update_logic_tables(self, variables, expressions, valid_truths):
        self.logic_tables.variables = variables
        self.logic_tables.expressions = expressions
        self.logic_tables.valid_truths = valid_truths

    def set_max_tokens(self, max_tokens):
        self.max_tokens = max_tokens
        self.log(f"Max tokens set to: {max_tokens}")

    def interact(self):
        while True:
            self.log("\nCommands: add, challenge, conclude, set_tokens, exit")
            cmd = input("> ").strip().lower()
            
            if cmd == 'exit':
                self.log('Exiting Socratic Reasoning.')
                break
            elif cmd == 'add':
                premise = input("Enter the premise: ").strip()
                self.add_premise(premise)
            elif cmd == 'challenge':
                premise = input("Enter the premise to challenge: ").strip()
                self.challenge_premise(premise)
            elif cmd == 'conclude':
                conclusion = self.draw_conclusion()
                print(conclusion)
            elif cmd == 'set_tokens':
                tokens = input("Enter the maximum number of tokens for the conclusion: ").strip()
                if tokens.isdigit():
                    self.set_max_tokens(int(tokens))
                else:
                    self.log("Invalid number of tokens.", level='error')
                    self.log_not_premise("Invalid number of tokens.", level='error')
            else:
                #self.log('Invalid command.', level='error')
                self.log_not_premise('Invalid command.', level='error')

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    chatter = GPT4o('your_api_key_here')  # Update with appropriate API key management
    socratic_reasoning = SocraticReasoning(chatter)

    # Example usage
    statements = [
        "All humans are mortal.",
        "Socrates is a human."
    ]

    for statement in statements:
        socratic_reasoning.add_premise(statement)

    conclusion = socratic_reasoning.draw_conclusion()
    print(conclusion)
    socratic_reasoning.interact()

