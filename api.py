# api.py
import json
import os
from dotenv import load_dotenv

class APIManager:
    def __init__(self):
        self.api_keys_file = 'api_keys.json'
        self.api_keys = self.load_api_keys()
        load_dotenv()  # Load environment variables from .env file
        self.load_env_api_keys()

    def load_api_keys(self):
        if os.path.exists(self.api_keys_file):
            with open(self.api_keys_file, 'r') as file:
                return json.load(file)
        return {}

    def save_api_keys(self):
        with open(self.api_keys_file, 'w') as file:
            json.dump(self.api_keys, file, indent=2)

    def load_env_api_keys(self):
        # Load API keys from environment variables if available
        openai_key = os.getenv('OPENAI_API_KEY')
        if openai_key:
            self.api_keys['openai'] = openai_key

        groq_key = os.getenv('GROQ_API_KEY')
        if groq_key:
            self.api_keys['groq'] = groq_key

        ollama_key = os.getenv('OLLAMA_API_KEY')
        if ollama_key:
            self.api_keys['ollama'] = ollama_key

        self.save_api_keys()

    def get_api_key(self, service):
        return self.api_keys.get(service)

    def add_api_key_interactive(self):
        service = input("Enter the name of the service (e.g., 'openai', 'groq'): ").strip()
        api_key = input(f"Enter the API key for {service}: ").strip()
        self.api_keys[service] = api_key
        self.save_api_keys()
        print(f"API key for {service} added successfully.")

    def remove_api_key(self, service):
        if service in self.api_keys:
            del self.api_keys[service]
            self.save_api_keys()
            print(f"API key for {service} removed successfully.")
        else:
            print(f"No API key found for {service}.")

    def list_api_keys(self):
        if self.api_keys:
            print("Stored API keys:")
            for service, key in self.api_keys.items():
                print(f"{service}: {key[:4]}...{key[-4:]}")  # Show only partial keys for security
        else:
            print("No API keys stored.")
