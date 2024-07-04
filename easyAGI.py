# easyAGI recursive internal reasoning of thought version 1 for display purposes
from nicegui import ui, app
import openai
import logging
import asyncio
import concurrent.futures
from memory import create_memory_folders, store_in_stm, DialogEntry
from agi import AGI
from api import APIManager
from chatter import GPT4o, GroqModel
from fastapi.staticfiles import StaticFiles
import os

# Set up logging
logging.basicConfig(level=logging.DEBUG)

# Serve static files from the 'gfx' directory
app.mount('/gfx', StaticFiles(directory='gfx'), name='gfx')

# Serve the CSS file
app.mount('/static', StaticFiles(directory='static'), name='static')

class FundamentalAGI:
    def __init__(self):
        self.api_manager = APIManager()
        self.agi = None
        self.initialize_memory()
        self.initialize_agi()

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
            self.agi = None
            ui.notify("Please add an OpenAI or Groq API key.")
            return
        
        self.agi = AGI(chatter)
        logging.debug("AGI initialized")

    def get_conclusion_from_agi(self, prompt):
        if self.agi is None:
            ui.notify("Please initialize AGI with an API key first.")
            return "AGI not initialized."
        self.agi.reasoning.add_premise(prompt)
        conclusion = self.agi.reasoning.draw_conclusion()
        return conclusion

    def perceive_environment(self, agi_prompt):
        return agi_prompt

    def communicate_response(self, conclusion):
        logging.info(f"Communicating response: {conclusion}")
        return conclusion

    def read_log_file(self, file_path):
        if os.path.exists(file_path):
            with open(file_path, 'r') as file:
                return file.read()
        else:
            return f"Log file {file_path} does not exist."

fundamental_agi = FundamentalAGI()

@ui.page('/')
def main():
    executor = concurrent.futures.ThreadPoolExecutor()

    async def send() -> None:
        question = text.value
        text.value = ''
        with message_container:
            ui.chat_message(text=question, name='query', sent=True)
            response_message = ui.chat_message(name='easyAGI', sent=False)
            spinner = ui.spinner(type='dots')

        try:
            loop = asyncio.get_event_loop()
            conclusion = await loop.run_in_executor(executor, fundamental_agi.get_conclusion_from_agi, question)
            response_message.clear()
            with response_message:
                ui.html(conclusion)
            await ui.run_javascript('window.scrollTo(0, document.body.scrollHeight)', timeout=5.0)

            # Store the dialog entry
            entry = DialogEntry(question, conclusion)
            store_in_stm(entry)
        except Exception as e:
            logging.error(f"Error getting conclusion from funAGI: {e}")
            log.push(f"Error getting conclusion from funAGI: {e}")
        finally:
            message_container.remove(spinner)  # Correctly remove the spinner

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
            "Truth Tables Log": "./memory/logs/truth_tables.json",
            "Not Premise Log": "./memory/logs/notpremise.json",
            "Conclusions Log": "./memory/logs/conclusions.txt"
            #"Decisions Log": "./memory/logs/decisions.json"
        }

        for log_name, log_path in log_files.items():
            ui.button(log_name, on_click=lambda path=log_path: view_log(path)).props('style="color: #ADD8E6; font-weight: bold; background-color: #1C3D5A; font-size: 16px; width: 150px; padding: 10px; border: 2px solid #1C3D5A; border-radius: 5px;"').classes('ml-2')

    # Function to view log files
    def view_log(file_path):
        log_content = fundamental_agi.read_log_file(file_path)
        log_container.clear()  # Clear the existing log content
        with log_container:
            ui.markdown(log_content).classes('w-full')

    with ui.tabs().classes('w-full') as tabs:
        chat_tab = ui.tab('chat').props('style="color: #218838; font-weight: bold; background-color: #e2e6ea; font-size: 16px; padding: 10px; border: 3px groove #218838; border-radius: 5px; transition: background-color 300ms ease-in-out, box-shadow 300ms ease-in-out;"').classes('ml-2 py-2 px-4 shadow-md hover:shadow-lg active:shadow-sm')
        logs_tab = ui.tab('Logs').props('style="color: #218838; font-weight: bold; background-color: #e2e6ea; font-size: 16px; padding: 10px; border: 3px groove #218838; border-radius: 5px; transition: background-color 200ms ease-in-out, box-shadow 200ms ease-in-out;"').classes('ml-2 py-2 px-4 shadow-md hover:shadow-lg active:shadow-sm')
        api_tab = ui.tab('keys').props('style="color: #218838; font-weight: bold; background-color: #e2e6ea; font-size: 16px; padding: 10px; border: 3px groove #218838; border-radius: 5px; transition: background-color 100ms ease-in-out, box-shadow 100ms ease-in-out;"').classes('ml-2 py-2 px-4 shadow-md hover:shadow-lg active:shadow-sm')
    with ui.tab_panels(tabs, value=chat_tab).props('style="background-color: transparent; padding: 10px; border-radius: 5px;"').classes('items-center justify-center').classes('w-full max-w-2xl mx-auto flex-grow items-stretch'):
        message_container = ui.tab_panel(chat_tab).classes('items-stretch')
        with ui.tab_panel(logs_tab):
            log = ui.log().classes('w-full h-full')
            log_container = ui.column().classes('w-full')
        with ui.tab_panel(api_tab):
            ui.label('Manage API Keys').classes('text-lg font-bold')
            with ui.row().props('style="background-color: #d1d5db; padding: 10px; border-radius: 5px;"').classes('items-center justify-center'):
                fundamental_agi.service_input = ui.input('Service (e.g., "openai", "groq")').classes('flex-1')
                fundamental_agi.key_input = ui.input('API Key').classes('flex-1')
            with ui.dropdown_button('Actions', auto_close=True).props('style="background-color: transparent; padding: 10px; border-radius: 5px;"').classes('items-center justify-center').classes('w-full max-w-2xl mx-auto flex-grow items-stretch'):
                ui.menu_item('Add API Key', on_click=fundamental_agi.add_api_key).props('style="color: #218838; font-weight: bold; background-color: #e2e6ea; font-size: 16px; padding: 10px; border: 3px groove #218838; border-radius: 5px; transition: background-color 100ms ease-in-out, box-shadow 100ms ease-in-out;"').classes('ml-2 py-2 px-4 shadow-md hover:shadow-lg active:shadow-sm')
                ui.menu_item('List API Keys', on_click=fundamental_agi.list_api_keys).props('style="color: green; font-weight: bold; background-color: #e2e6ea; font-size: 16px; padding: 10px; border: 3px groove #218838; border-radius: 5px; transition: background-color 100ms ease-in-out, box-shadow 100ms ease-in-out;"').classes('ml-2 py-2 px-4 shadow-md hover:shadow-lg active:shadow-sm')

            # Container to list keys with delete buttons
            global keys_container
            keys_container = ui.column().classes('w-full')

    with ui.footer().classes('bg-black'), ui.column().classes('w-full max-w-3xl mx-auto my-6 input-area'):
        with ui.row().classes('w-full no-wrap items-center'):
            placeholder = 'Enter your prompt here'
            text = ui.input(placeholder='Enter text here').props('rounded outlined input-class=mx-3 bg-green-100 input-style="color: green" input-class="font-mono"').props('style="border: 2px solid #4CAF50; width: 100%; outline: none; background-color: transparent;"').on('keydown.enter', send)
        ui.markdown('[funAGI](https://rage.pythai.net)').classes('text-xs self-end mr-8 m-[-1em] text-primary')

logging.debug("starting easyAGI")
ui.run(title='easyAGI')

if __name__ == '__main__':
    main()
