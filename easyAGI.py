# easyAGI (c) Gregory L. Magnusson 2024 MIT license
import logging
import asyncio
import concurrent.futures
from nicegui import ui, app
from memory.memory import create_memory_folders, store_in_stm, DialogEntry
from api import APIManager
from chatter import GPT4o, GroqModel
from fastapi.staticfiles import StaticFiles
import os
import json
from datetime import datetime
from automind import FundamentalAGI

# Set up logging
logging.basicConfig(level=logging.DEBUG)

# Serve static files from the 'gfx' directory
app.mount('/gfx', StaticFiles(directory='gfx'), name='gfx')

# Serve the CSS file
app.mount('/static', StaticFiles(directory='static'), name='static')

class OpenMind:
    def __init__(self):
        self.api_manager = APIManager()
        self.agi_instance = None
        self.initialize_memory()
        self.initialize_agi()
        self.internal_queue = asyncio.Queue()
        self.prompt = ""  # Initialize an empty prompt field

    def initialize_memory(self):
        create_memory_folders()

    def add_api_key(self):
        service = self.service_input.value.strip()
        api_key = self.key_input.value.strip()
        logging.debug(f"Adding API key for {service}: {api_key[:4]}...{api_key[-4:]}")
        if service and api_key:
            self.api_manager.api_keys[service] = api_key
            self.api_manager.save_api_key(service, api_key)
            self.initialize_agi()
            ui.notify(f'API key for {service} added and loaded successfully')
            self.service_input.value = ''
            self.key_input.value = ''
            ui.run_javascript('setTimeout(() => { window.location.href = "/"; }, 1000);')
        else:
            ui.notify('Please provide both service name and API key')

    def delete_api_key(self, service):
        logging.debug(f"Deleting API key for {service}")
        if service in self.api_manager.api_keys:
            del self.api_manager.api_keys[service]
            self.api_manager.remove_api_key(service)
            self.initialize_agi()
            ui.notify(f'API key for {service} removed successfully')
            self.list_api_keys()  # Refresh the list after deletion
        else:
            ui.notify(f'No API key found for {service}')

    def list_api_keys(self):
        if self.api_manager.api_keys:
            keys_list = [(service, key) for service, key in self.api_manager.api_keys.items()]
            logging.debug(f"Stored API keys: {keys_list}")
            keys_container.clear()
            for service, key in keys_list:
                with keys_container:
                    ui.label(f"{service}: {key[:4]}...{key[-4:]}").classes('flex-1')
                    ui.button('Delete', on_click=lambda s=service: self.delete_api_key(s)).classes('ml-4')
            ui.notify('Stored API keys:\n' + "\n".join([f"{service}: {key[:4]}...{key[-4:]}" for service, key in keys_list]))
        else:
            ui.notify('No API keys in storage')
            keys_container.clear()
            with keys_container:
                ui.label('No API keys in storage')

    def initialize_agi(self):
        openai_key = self.api_manager.get_api_key('openai')
        groq_key = self.api_manager.get_api_key('groq')

        if openai_key:
            chatter = GPT4o(openai_key)
        elif groq_key:
            chatter = GroqModel(groq_key)
        else:
            self.agi_instance = None
            return

        self.agi_instance = FundamentalAGI(chatter)
        logging.debug("AGI initialized")

    async def get_conclusion_from_agi(self, prompt):
        """
        Get a conclusion from the AGI based on the provided prompt.
        This method is asynchronous to allow non-blocking operations.
        """
        if self.agi_instance is None:
            return "AGI not initialized. Please add an API key."
        conclusion = await asyncio.get_event_loop().run_in_executor(None, self.agi_instance.get_conclusion_from_agi, prompt)
        return conclusion

    def communicate_response(self, conclusion):
        """
        Log and print the conclusion from the AGI.
        """
        logging.info(f"Communicating response: {conclusion}")
        self.display_internal_conclusion(conclusion)
        return conclusion

    async def reasoning_loop(self):
        """
        Internal reasoning loop for continuous AGI reasoning without user interaction.
        This loop adds a prompt to the AGI and processes its conclusion periodically.
        The conclusions are displayed in the response window.
        """
        while True:
            if self.agi_instance is None:
                openai_key = self.api_manager.get_api_key('openai')
                groq_key = self.api_manager.get_api_key('groq')
                if openai_key or groq_key:
                    self.initialize_agi()
                else:
                    logging.debug("Waiting for API key...")
                    await asyncio.sleep(5)  # Wait before checking again
                    continue

            prompt = self.prompt  # Use the updated prompt from user input
            conclusion = await self.get_conclusion_from_agi(prompt)
            self.display_internal_conclusion(conclusion)
            await asyncio.sleep(10)  # Adjust the delay as necessary

    def display_internal_conclusion(self, conclusion):
        """
        Display the internal reasoning conclusion in the response window and log it to a JSON file.
        """
        if conclusion != "No premises available for logic as conclusion.":
            with message_container:
                response_message = ui.chat_message(name='funAGI', sent=False)
                response_message.clear()
                with response_message:
                    ui.html(f"Internal reasoning conclusion: {conclusion}")
            logging.info(f"Internal reasoning conclusion: {conclusion}")

        # Determine which log file to write to
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "conclusion": conclusion
        }
        
        if conclusion == "No premises available for logic as conclusion.":
            log_file_path = "./memory/logs/notpremise.json"
        else:
            log_file_path = "./memory/logs/thoughts.json"

        if not os.path.exists(log_file_path):
            with open(log_file_path, 'w') as file:
                json.dump([log_entry], file, indent=4)
        else:
            with open(log_file_path, 'r+') as file:
                data = json.load(file)
                data.append(log_entry)
                file.seek(0)
                json.dump(data, file, indent=4)

    async def main_loop(self):
        """
        Main loop to handle both internal reasoning and user input.
        """
        asyncio.create_task(self.reasoning_loop())

        while True:
            prompt = await self.internal_queue.get()
            if prompt == 'exit':
                break
            self.prompt = prompt  # Update the prompt with the new input
            conclusion = await self.get_conclusion_from_agi(prompt)
            self.communicate_response(conclusion)

    async def send_message(self, question):
        with message_container:
            ui.chat_message(text=question, name='query', sent=True)
            response_message = ui.chat_message(name='easyAGI', sent=False)
            spinner = ui.spinner(type='dots')

        try:
            conclusion = await self.get_conclusion_from_agi(question)
            response_message.clear()
            with response_message:
                ui.html(conclusion)

            await self.run_javascript_with_retry('window.scrollTo(0, document.body.scrollHeight)', retries=3, timeout=30.1)

            # Store the dialog entry
            entry = DialogEntry(question, conclusion)
            store_in_stm(entry)
        except Exception as e:
            logging.error(f"Error getting conclusion from easyAGI: {e}")
            log.push(f"Error getting conclusion from easyAGI: {e}")
        finally:
            message_container.remove(spinner)  # Correctly remove the spinner

    async def run_javascript_with_retry(self, script, retries=3, timeout=10.0):
        for attempt in range(retries):
            try:
                await ui.run_javascript(script, timeout=timeout)
                return
            except TimeoutError:
                logging.warning(f"JavaScript did not respond within {timeout} s on attempt {attempt + 1}")
        raise TimeoutError(f"JavaScript did not respond after {retries} attempts")

    def read_log_file(self, file_path):
        """
        Read the content of a log file and return it.
        """
        try:
            with open(file_path, 'r') as file:
                return file.read()
        except FileNotFoundError:
            logging.error(f"Log file not found: {file_path}")
            return f"Log file not found: {file_path}"
        except Exception as e:
            logging.error(f"Error reading log file {file_path}: {e}")
            return f"Error reading log file {file_path}: {e}"

    def handle_javascript_response(self, msg):
        request_id = msg.get('request_id')
        result = msg.get('result')
        
        if request_id is not None:
            if result is not None:
                JavaScriptRequest.resolve(request_id, result)
            else:
                # Handle the case where 'result' is missing
                JavaScriptRequest.reject(request_id, 'Missing result in JavaScript response')
        else:
            # Handle the case where 'request_id' is missing if needed
            pass

openmind = OpenMind()

@ui.page('/')
def main():
    global executor, message_container, log
    executor = concurrent.futures.ThreadPoolExecutor()

    async def send() -> None:
        question = text.value
        text.value = ''
        await openmind.send_message(question)
        await openmind.internal_queue.put(question)  # Add the prompt to the internal queue for processing

    # Link the external stylesheet
    ui.add_head_html('<link rel="stylesheet" href="/static/style.css">')

    # Initialize dark mode toggle
    dark_mode = ui.dark_mode()

    async def toggle_dark_mode():
        dark_mode.value = not dark_mode.value
        dark_mode_toggle.text = 'Light Mode' if dark_mode.value else 'Dark Mode'

    with ui.row().classes('justify-end w-full p-4'):
        dark_mode_toggle = ui.button('Dark Mode', on_click=toggle_dark_mode).props('style="color: #ADD8E6; background-color: #1C3D5A; font-weight: bold; font-size: 16px; width: 150px; padding: 10px; border: 2px solid #1C3D5A; border-radius: 5px; transition: background-color 200ms ease-in-out, box-shadow 200ms ease-in-out;"').classes('ml-2 py-2 px-4 shadow-md hover:bg-blue-900 active:bg-blue-700')
        # Adding log file buttons
        log_files = {
            "Premises Log": "./memory/logs/premises.json",
            "Not Premise Log": "./memory/logs/notpremise.json",
            "Truth Tables Log": "./memory/logs/truth_tables.json",
            "Thoughts Log": "./memory/logs/thoughts.json",
            "Conclusions Log": "./memory/logs/conclusions.txt",
            "Decisions Log": "./memory/logs/decisions.json"
        }

        for log_name, log_path in log_files.items():
            ui.button(log_name, on_click=lambda path=log_path: view_log(path)).props('style="color: #ADD8E6; font-weight: bold; background-color: #1C3D5A; font-size: 16px; width: 150px; padding: 10px; border: 2px solid #1C3D5A; border-radius: 5px;"').classes('justify-center')

    # Function to view log files
    def view_log(file_path):
        log_content = openmind.read_log_file(file_path)
        log_container.clear()  # Clear the existing log content
        with log_container:
            ui.markdown(log_content).classes('w-full')

    with ui.tabs().classes('w-full') as tabs:
        chat_tab = ui.tab('chat').props('style="color: #218838; font-weight: bold; background-color: #e2e6ea; font-size: 16px; padding: 10px; border: 3px groove #218838; border-radius: 5px; transition: background-color 300ms ease-in-out, box-shadow 300ms ease-in-out;"').classes('ml-2 py-2 px-4 shadow-md hover:shadow-lg active:shadow-sm')
        logs_tab = ui.tab('logs').props('style="color: #218838; font-weight: bold; background-color: #e2e6ea; font-size: 16px; padding: 10px; border: 3px groove #218838; border-radius: 5px; transition: background-color 200ms ease-in-out, box-shadow 200ms ease-in-out;"').classes('ml-2 py-2 px-4 shadow-md hover:shadow-lg active:shadow-sm')
        api_tab = ui.tab('APIk').props('style="color: #218838; font-weight: bold; background-color: #e2e6ea; font-size: 16px; padding: 10px; border: 3px groove #218838; border-radius: 5px; transition: background-color 100ms ease-in-out, box-shadow 100ms ease-in-out;"').classes('ml-2 py-2 px-4 shadow-md hover:shadow-lg active:shadow-sm')
    with ui.tab_panels(tabs, value=chat_tab).props('style="color: rgb(0, 50, 0); background-color: rgba(70, 130, 180, 0.777); padding: 10px; border-radius: 5px;"').classes('items-center justify-center w-full max-w-2xl mx-auto flex-grow items-stretch'):
        message_container = ui.tab_panel(chat_tab).classes('items-stretch')
        with ui.tab_panel(logs_tab):
            log = ui.log().classes('w-full h-full')
            log_container = ui.column().classes('w-full')
        with ui.tab_panel(api_tab):
            ui.label('Manage API Keys').classes('text-lg font-bold')
            with ui.row().classes('items-center'):
                openmind.service_input = ui.input('Service (e.g., "openai", "groq")').classes('flex-1')
                openmind.key_input = ui.input('API Key').classes('flex-1')
            with ui.dropdown_button('Actions', auto_close=True):
                ui.menu_item('Add API Key', on_click=openmind.add_api_key)
                ui.menu_item('List API Keys', on_click=openmind.list_api_keys)

            # Container to list keys with delete buttons
            global keys_container
            keys_container = ui.column().classes('w-full')

    with ui.footer().classes('bg-black'), ui.column().classes('w-full max-w-3xl mx-auto my-6 input-area'):
        with ui.row().classes('w-full no-wrap items-center'):
            placeholder = 'Enter your prompt here'
            text = ui.input(placeholder='Enter text here').props('rounded outlined input-class=mx-3 bg-green-100 input-style="color: green" input-class="font-mono"').props('style="border: 2px solid #4CAF50; width: 100%; outline: none;"').on('keydown.enter', send)
        ui.markdown('[easyAGI](https://rage.pythai.net)').classes('text-xs self-end mr-8 m-[-1em] text-primary')

    # Start the main loop
    asyncio.create_task(openmind.main_loop())

logging.debug("starting easyAGI")
ui.run(title='easyAGI')

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        logging.info("Shutting down...")
