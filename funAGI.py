from nicegui import ui
import openai
import logging
import asyncio
import concurrent.futures
from memory import create_memory_folders, store_in_stm, DialogEntry
from agi import AGI
from api import APIManager
from chatter import GPT4o, GroqModel

# Set up logging
logging.basicConfig(level=logging.DEBUG)

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
            ui.notify(f'Stored API keys:\n' + "\n".join([f"{service}: {key[:4]}...{key[-4:]}" for service, key in keys_list]))
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

    def get_solution_from_agi(self, prompt):
        if self.agi is None:
            ui.notify("Please initialize AGI with an API key first.")
            return "AGI not initialized."
        self.agi.reasoning.add_premise(prompt)
        solution = self.agi.reasoning.draw_conclusion()
        return solution

    def perceive_environment(self):
        agi_prompt = input("Enter the problem to solve (or type 'exit' to quit): ")
        return agi_prompt

    def communicate_response(self, conclusion):
        logging.info(f"Communicating response: {conclusion}")
        print(conclusion)

fundamental_agi = FundamentalAGI()

@ui.page('/')
def main():
    executor = concurrent.futures.ThreadPoolExecutor()

    async def send() -> None:
        question = text.value
        text.value = ''
        with message_container:
            ui.chat_message(text=question, name='query', sent=True)
            response_message = ui.chat_message(name='funAGI', sent=False)
            spinner = ui.spinner(type='dots')

        try:
            loop = asyncio.get_event_loop()
            solution = await loop.run_in_executor(executor, fundamental_agi.get_solution_from_agi, question)
            response_message.clear()
            with response_message:
                ui.html(solution)
            await ui.run_javascript('window.scrollTo(0, document.body.scrollHeight)', timeout=5.0)
        except Exception as e:
            logging.error(f"Error getting solution from funAGI: {e}")
            log.push(f"Error getting solution from funAGI: {e}")
        finally:
            message_container.remove(spinner)  # Correctly remove the spinner

    ui.add_css(r'a:link, a:visited {color: inherit !important; text-decoration: none; font-weight: 500}')
    ui.query('.q-page').classes('flex')
    ui.query('.nicegui-content').classes('w-full')

    with ui.tabs().classes('w-full') as tabs:
        chat_tab = ui.tab('chat')
        logs_tab = ui.tab('logs')
        api_tab = ui.tab('API Keys')
    with ui.tab_panels(tabs, value=chat_tab).classes('w-full max-w-2xl mx-auto flex-grow items-stretch'):
        message_container = ui.tab_panel(chat_tab).classes('items-stretch')
        with ui.tab_panel(logs_tab):
            log = ui.log().classes('w-full h-full')
        with ui.tab_panel(api_tab):
            ui.label('Manage API Keys').classes('text-lg font-bold')
            with ui.row().classes('items-center'):
                fundamental_agi.service_input = ui.input('Service (e.g., "openai", "groq")').classes('flex-1')
                fundamental_agi.key_input = ui.input('API Key').classes('flex-1')
            with ui.dropdown_button('Actions', auto_close=True):
                ui.menu_item('Add API Key', on_click=fundamental_agi.add_api_key)
                ui.menu_item('List API Keys', on_click=fundamental_agi.list_api_keys)

            # Container to list keys with delete buttons
            global keys_container
            keys_container = ui.column().classes('w-full')

    with ui.footer().classes('bg-white'), ui.column().classes('w-full max-w-3xl mx-auto my-6'):
        with ui.row().classes('w-full no-wrap items-center'):
            placeholder = 'Enter your prompt here'
            text = ui.input(placeholder=placeholder).props('rounded outlined input-class=mx-3') \
                .classes('w-full self-center').on('keydown.enter', send)
        ui.markdown('[funAGI](https://github.com/pythaiml/funAGI)').classes('text-xs self-end mr-8 m-[-1em] text-primary')

logging.debug("starting funAGI")
ui.run(title='funAGI')

if __name__ == '__main__':
    main()
