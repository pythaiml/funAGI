# funAGI
fundamental AGI point of departure logic.py and SocraticReasoning.py
debug environment with logging
to do: include SimpleMind.py neural network and coach.py training

FundamentalAGI Project Setup

codebase to create a simplified version called fundamentalAGI.py. This new script will use SocraticReasoning.py and logic.py with verbose logging to understand the export of the belief into ./memory/truth. This simplified version will omit reasoning.py and directly leverage the core logic and memory management. Here's how we will structure the project:

    fundamentalAGI.py: Main script to run the AGI.
    agi.py: Core AGI logic.
    api.py: API key management.
    bdi.py: BDI (Belief-Desire-Intention) model.
    chatter.py: Interface for different chat models.
    logic.py: Logic table management and evaluation.
    memory.py: Memory management for storing dialogues and truth values.
    SocraticReasoning.py: Socratic reasoning engine for the AGI.

# agi.py AGI workflow

    API Key Management (api.py):

    Loads API keys from api_keys.json or environment variables.
    Manages adding, removing, and listing API keys.

Core AGI Logic (agi.py):

    Initializes the AGI with API manager and chatter models.
    Learns from data by creating propositions.
    Makes decisions by leveraging SocraticReasoning.

Memory Management (memory.py):

    Handles creating necessary directories.
    Stores and loads conversation memories.
    Stores valid truths and dialogue entries.

Socratic Reasoning (SocraticReasoning.py):

    Manages premises and draws logical conclusions.
    Logs actions and results.
    Validates conclusions using LogicTables.

Logic Table Management (logic.py):

    Manages logic variables, expressions, and truth tables.
    Evaluates expressions and validates truths.
    Logs all actions and saves beliefs.

Chat Models (chatter.py):

    Interfaces for different chat models like GPT4o, GroqModel, and OllamaModel.

# Key Components and Flow

    API Key Management:
        APIManager class handles loading, saving, and managing API keys.
        In EasyAGI.__init__, the user is prompted to manage API keys if necessary.

    Learning from Data:
        AGI.learn_from_data method processes input data into two propositions.
        These propositions are added as premises to the SocraticReasoning engine.

    Making Decisions:
        AGI.make_decisions method invokes the Socratic reasoning process to draw a conclusion.
        The conclusion (decision) is returned.

    Main Loop:
        EasyAGI.main_loop handles user input and processes it using the AGI system.
        Decisions are communicated back to the user and stored in short-term memory.


Belief-Desire-Intention Model (bdi.py):

    Manages beliefs, desires, and intentions.
    Processes BDI components for decision making.


    funAGI.py is the UI. fundatmentalAGI funAGI has been published to showcase, audit and debug the easyAGI SocraticReasoning.py and logic.py

install (builds an openai API and groq API ready terminal interaction from openai or groq API key with response from SocraticReasoning.py and logic.py with logging to local folders from memory.py)

```bash
git clone https://github.com/autoGLM/funAGI/
cd funAGI
python3 -m venv fun
source fun/bin/activate
pip install -r requirements.txt
python3 funAGI.py
```


