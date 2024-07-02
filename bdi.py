import logging
from logic import LogicTables
from SocraticReasoning import SocraticReasoning
from memory.memory import store_in_stm, DialogEntry
from chatter import GPT4o
from api import APIManager

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('BDI')

# BDI Classes Start

# Belief Class
class Belief:
    def __init__(self, belief):
        self.belief = belief
        self.logic = LogicTables()  # Initialize LogicTables class for logical operations
        self.api_manager = APIManager()  # Initialize APIManager for managing API keys
        api_key = self.api_manager.get_api_key('gpt4o')  # Retrieve the API key for the chatter service
        if not api_key:
            raise ValueError("API key for GPT4o is missing. Please add it using APIManager.")
        self.socratic = SocraticReasoning(GPT4o(api_key))  # Initialize SocraticReasoning class with a chatter instance

    def __str__(self):
        return self.belief

    def evaluate_belief(self):
        try:
            # Use logic to evaluate the belief
            valid = self.logic.validate_truth(self.belief)
            if valid:
                return f"Belief '{self.belief}' is valid."
            else:
                return f"Belief '{self.belief}' is invalid."
        except Exception as e:
            logger.error(f"Error evaluating belief '{self.belief}': {e}")
            return f"Error evaluating belief '{self.belief}': {e}"

    def reason_belief(self):
        try:
            # Use SocraticReasoning to reason about the belief
            self.socratic.add_premise(self.belief)
            self.socratic.draw_conclusion()
            return self.socratic.logical_conclusion
        except Exception as e:
            logger.error(f"Error reasoning belief '{self.belief}': {e}")
            return f"Error reasoning belief '{self.belief}': {e}"

# Desire Class
class Desire:
    def __init__(self, goal):
        self.goal = goal

    def __str__(self):
        return f"Goal: {self.goal}"

# Intention Class
class Intention:
    def __init__(self, plan):
        self.plan = plan

    def execute(self):
        try:
            logger.info(f"Executing plan: {self.plan}")
            print(f"Executing plan: {self.plan}")
        except Exception as e:
            logger.error(f"Error executing plan '{self.plan}': {e}")

# Goal Class
class Goal:
    def __init__(self, name, conditions, priority=0):
        self.name = name
        self.conditions = conditions
        self.priority = priority

    def is_fulfilled(self, belief_system, desire_system, intentions_system):
        try:
            # Evaluate conditions based on beliefs, desires, and intentions
            # Return True if the goal is fulfilled, otherwise False
            return all(belief_system.evaluate_belief(cond) == f"Belief '{cond}' is valid." for cond in self.conditions)
        except Exception as e:
            logger.error(f"Error evaluating if goal '{self.name}' is fulfilled: {e}")
            return False

    def __str__(self):
        return f"Goal: {self.name}, Priority: {self.priority}"

# Reward Class
class Reward:
    def __init__(self):
        self.total_reward = 0

    def update_reward(self, goal):
        try:
            if goal.is_fulfilled():
                # Update the total reward based on the priority or other criteria
                self.total_reward += goal.priority
        except Exception as e:
            logger.error(f"Error updating reward for goal '{goal.name}': {e}")

    def get_reward(self):
        return self.total_reward

# BDI Classes End

# Example usage
if __name__ == "__main__":
    belief = Belief("A and B")
    print(belief.evaluate_belief())
    print(belief.reason_belief())

    desire = Desire("Achieve C")
    print(desire)

    intention = Intention("Plan to achieve C")
    intention.execute()

    goal = Goal("Goal1", ["A and B"], priority=5)
    beliefs = [belief]
    desires = [desire]
    intentions = [intention]
    print(goal.is_fulfilled(beliefs, desires, intentions))
    print(goal)

    reward = Reward()
    reward.update_reward(goal)
    print(reward.get_reward())

