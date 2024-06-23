import logging
import pathlib
from chatter import GPT4o
from logic import LogicTables

class SocraticReasoning:
    def __init__(self, chatter):
        self.premises = []
        self.logger = logging.getLogger('SocraticReasoning')
        self.logger.setLevel(logging.DEBUG)  # Set to DEBUG to capture all logs
        
        # Ensure the directory exists
        socratic_log_dir = './mindx'
        pathlib.Path(socratic_log_dir).mkdir(parents=True, exist_ok=True)

        file_handler = logging.FileHandler(f'{socratic_log_dir}/socraticlog.txt')  # Save logs to file
        file_handler.setLevel(logging.DEBUG)
        file_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(file_formatter)
        
        # Stream handler to suppress lower-level logs in the terminal
        stream_handler = logging.StreamHandler()
        stream_handler.setLevel(logging.CRITICAL)  # Only show critical logs in the terminal
        stream_formatter = logging.Formatter('%(message)s')
        stream_handler.setFormatter(stream_formatter)

        self.logger.addHandler(file_handler)
        self.logger.addHandler(stream_handler)

        self.max_tokens = 100
        self.chatter = chatter
        self.logic_tables = LogicTables()
        self.dialogue_history = []
        self.logical_conclusion = ""

    def log(self, message, level='info'):
        if level == 'info':
            self.logger.info(message)
        elif level == 'error':
            self.logger.error(message)
        self.store_log_in_mindx(message, level)

    def store_log_in_mindx(self, message, level):
        mindx_path = './mindx/errors/log.txt'
        pathlib.Path(mindx_path).parent.mkdir(parents=True, exist_ok=True)
        with open(mindx_path, 'a') as file:
            file.write(f"{level.upper()}: {message}\n")

    def add_premise(self, premise):
        if self.parse_statement(premise):
            self.premises.append(premise)
            self.log(f'Added premise: {premise}')
        else:
            self.log(f'Invalid premise: {premise}', level='error')

    def parse_statement(self, statement):
        # Simple parser to validate statements
        return isinstance(statement, str) and len(statement) > 0

    def challenge_premise(self, premise):
        if premise in self.premises:
            self.premises.remove(premise)
            self.log(f'Challenged and removed premise: {premise}')
            self.remove_equivalent_premises(premise)
        else:
            self.log(f'Premise not found: {premise}', level='error')

    def remove_equivalent_premises(self, premise):
        equivalent_premises = [p for p in self.premises if self.logic_tables.unify_variables(premise, p)]
        for p in equivalent_premises:
            self.premises.remove(p)
            self.log(f'Removed equivalent premise: {p}')

    def draw_conclusion(self):
        if not self.premises:
            self.log('No premises available for logic as conclusion.', level='error')
            return "No premises available for logic as conclusion."

        premise_text = "\n".join(f"- {premise}" for premise in self.premises)
        prompt = f"Based on the premises:\n{premise_text}\nProvide a logical conclusion."

        self.logical_conclusion = self.chatter.generate_response(prompt)
        self.log(f"Conclusion:\n{self.logical_conclusion}")

        if not self.validate_conclusion():
            self.log('Invalid conclusion. Please revise.', level='error')
            return "Invalid conclusion. Please revise."

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
                print(self.draw_conclusion())
            elif cmd == 'set_tokens':
                tokens = input("Enter the maximum number of tokens for the conclusion: ").strip()
                if tokens.isdigit():
                    self.set_max_tokens(int(tokens))
                else:
                    self.log("Invalid number of tokens.", level='error')
            else:
                self.log('Invalid command.', level='error')

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    chatter = GPT4o('your_api_key_here')  # Update with appropriate API key management
    socratic_reasoning = SocraticReasoning(chatter)

    # Example usage
    statements = [
        "Premise 1: A and B",
        "Premise 2: If A and B, then C",
        "Premise 3: Not C",
    ]

    for statement in statements:
        socratic_reasoning.add_premise(statement)

    socratic_reasoning.draw_conclusion()
    print(socratic_reasoning.logical_conclusion)
    socratic_reasoning.interact()
