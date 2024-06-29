# funAGI
fundamental AGI point of departure agi.py logic.py and SocraticReasoning.py using api.py with memory.py for folder and key management<br />
debug environment now includes logging for deeper understanding of the reasoning process and troubleshooting<br />
original implmentation of funAGI has been archived at <a href="https://github.com/autoGLM/funAGI">github.com/autoGLM/funAGI</a><br />
This version of funAGI.py is going deeper into the "workings" of the SocraticReasoning technique to include logic.py tables and bdi.py with an even more "verbose" logging method to follow premise to conclusion workflow. api.py has been updated to use .env for key storage.<br />

Work has begun to create funAGIcli.py as the terminal interaction and funAGI.py as the UIUX<br />
expect breaking changed use at own risk<br />

still need to have the response be towards the participant instead of the context of the internal reasoning<br />

# first output from "create a framework for AGI from mixtral using groq includes<br />


1. knowledge representation and reasoning: the ability to represent and reason about complex knowledge, including objects, relationships, and events in the world. 2. natural language understanding and generation: the ability to understand and generate natural language in order to communicate effectively with humans. 3. perception and action: the ability to perceive and interact with the physical world through sensors and actuators. 4. learning and adaptation: the ability to learn and adapt to new situations and environments. 5. ethics and values: the incorporation of ethical principles and values to guide decision-making and behavior. 6. safety and security: the incorporation of safety and security measures to prevent unintended behavior and protect against malicious attacks. 7. scalability and efficiency: the ability to handle large amounts of data and complex tasks without requiring excessive computational resources. 8. verifiability and explainability: the ability to prove the correctness and trustworthiness of the agi system, as well as the ability to provide clear explanations of its reasoning and decision-making processes. these components are all crucial for the development of a safe, ethical, and beneficial agi system. however, it is important to note that this framework is not exhaustive, and that the development of agi will likely involve many additional considerations and challenges. for example, agi systems will need to be able to handle uncertainty and ambiguity in a way that is consistent with human reasoning and decision-making. they will also need to be able to deal with missing or incomplete information, and to be able to learn from and make decisions based on limited data. additionally, agi systems will need to be able to interact and cooperate with humans in a way that is safe and beneficial for both parties. this will require the development of effective human-machine interfaces and the ability for agi systems to understand and respond to human emotions, intentions, and social cues. another important consideration is the potential impact of agi on society and the economy. as agi systems become more capable, they may have the potential to disrupt traditional industries and occupations, and to create new ones.


UIUX has been split into two versions<br />
<b>funAGIcli.py</b> will maintain the terminal based interaction<br />
<b>funAGI.py</b> is the UIUX graphical expression<br />


# FundamentalAGI Project Setup

codebase to create a simplified and fun AGI for fundamentalAGI basic reasoning. funAGI.py uses SocraticReasoning.py with logic.py
verbose logging to reason to truth as export of belief into ./memory/truth. This simplified version will omits reasoning.py and SimpleMind.py to directly leverage the core logic and memory management of the basic reasoning AGI. For a deep dive into SocraticReasoning.py visit<br />
<a href="https://rage.pythai.net/understanding-socraticreasoning-py/">https://rage.pythai.net/understanding-socraticreasoning-py/</a><br />

# project structure

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
#########################################################################
# Process Flow from User Input to Response
Step 1: User Input

    Action: The user provides an input via the command line.
    Input Example: "Explain the workflow to building AGI"

Step 2: Perceive Environment

    Method: EasyAGI.perceive_environment
    Action: The system captures the user's input.
    Output: The user's input string is returned for processing.

Step 3: Learning from Data

    Method: AGI.learn_from_data
    Action: The user's input string is processed to extract propositions.
    Process:
        The input string is split into two propositions based on a delimiter (e.g., ";").
        If the input contains only one proposition, the second proposition is set as an empty string.
        The propositions are added as premises in the Socratic reasoning engine.
    Output: Two propositions are returned for further processing.

    Adding Premises to Socratic Reasoning:
        Validates and adds each proposition as a premise.
        Logs each addition.

    skipped ::::: Processing THOT:
        Iterates through reasoning methods.
        Generates intermediate conclusions.
        Aggregates combined results.

    skipped ::::: Logging THOT Data:
        Logs premises, combined results, and final decision.
        Appends to THOT log file (thots.json).

    Drawing a Conclusion:
        Generates logical conclusion using language model.
        Validates conclusion.
        Logs conclusion.

    Communicating Response:
        Prints final decision to console.
        Logs communicated response.

    Storing Conversation Memory:
        Creates DialogEntry with input and decision.
        Saves entry to STM.

This workflow provides a comprehensive view of how user input is processed, reasoned with, and responded to in fundamentalAGI funAGI.py system. Each component plays a critical role in ensuring the AGI provides accurate and logical responses based on the input provided. funAGI is the simplified agi --> SocraticReasoning --> logic --> response dialogue
################################################################

```csharp
+-------------------+       +-------------------+       +---------------------+
|    User Input     | ----> | Perceive          | ----> | Learning from Data  |
| (Command Line)    |       | Environment       |       | (Extract Propositions)|
+-------------------+       +-------------------+       +---------------------+
                                      |
                                      v
                             +-------------------+
                             | Add Premises to   |
                             | Socratic Reasoning|
                             +-------------------+
                                      |
                                      v
                             +-------------------+
                             |  Process THOT     |
                             |  (Various Reasoning|
                             |   Techniques)      |
                             +-------------------+
                                      |
                                      v
                             +-------------------+
                             |  Log THOT Data    |
                             +-------------------+
                                      |
                                      v
                             +-------------------+
                             |  Draw Conclusion  |
                             |  (GPT-4 Model)    |
                             +-------------------+
                                      |
                                      v
                             +-------------------+
                             |Communicate Response|
                             |  to User           |
                             +-------------------+
                                      |
                                      v
                             +-------------------+
                             | Store Conversation |
                             | Memory (STM)       |
                             +-------------------+
```

# install
(builds an openai API and groq API ready terminal interaction from openai or groq API key<br />
with response from SocraticReasoning.py and logic.py with logging to local folders from memory.py)<br />
<b>logs SocraticReasoning</b><br />
./mindx/socraticlogs.txt<br />
<b>logs errors</b><br />
./mindx/errors/logs.txt<br />
<b>logs logic.py truth tables errors to</b><br />
./mindx/truth/logs.txt<br />
<b>shows truthtable creation in</b><br /> 
./mindx/truth/2024-06-23T22:44:49.670605_belief.txt<br /> 

to do: include statement of belief in belief log; fix SocraticReasoning from ./mindx/socraticlogs.txt<br />

<b>memory of each input / response is stored in</b><br />
./memory/stm/1719207889.json<br />
as timestamped instruction / response<br />

```json
{"instruction":"agi","response":"a logical conclusion based on the premise of autonomous general intelligence (agi) is that it has the ability to independently perform a wide range of tasks at a level equal to or beyond that of a human being. agi would be capable of understanding, learning, and applying knowledge across a wide range of domains and tasks, and would be able to adapt to new situations and environments. it would be able to understand and respond to natural language, recognize and interpret visual and auditory information, and make decisions and solve problems based on its understanding. additionally, agi would be capable of self-improvement and continue to learn and get better at tasks over time. however, it is important to note that the development of agi also raises ethical and societal concerns that need to be addressed."}
```
this is the bare bones working version of funAGI with error logging and first errors to fix from first working deployment. fundamental funAGI.py point of departure version 1

```bash
git clone https://github.com/autoGLM/funAGI/
cd funAGI
python3 -m venv fun
source fun/bin/activate
pip install -r requirements.txt
python3 funAGI.py
```


