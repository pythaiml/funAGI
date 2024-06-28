from nicegui import ui
import logging
import asyncio
import concurrent.futures
from memory import create_memory_folders, store_in_stm, DialogEntry
from agi import AGI
from api import APIManager
from chatter import GPT4o, GroqModel

# Set up logging
logging.basicConfig(level=logging.DEBUG)

class NiceAGI:
    def __init__(self):
        self.api_manager = APIManager()
        self.initialize_memory()
        self.manage_api_keys()
        self.agi = self.initialize_agi()

    def initialize_memory(self):
        create_memory_folders()

    def manage_api_keys(self):
        while True:
            self.api_manager.list_api_keys()
            action = input("Choose an action: (a) Add API key, (d) Delete API key, (l) List API keys, (Press Enter to continue): ").strip().lower()
            if not action:
                break
            elif action == 'a':
                self.api_manager.add_api_key_interactive()
            elif action == 'd':
                api_name = input("Enter the API name to delete: ").strip()
                if api_name:
                    self.api_manager.remove_api_key(api_name)
            elif action == 'l':
                self.api_manager.list_api_keys()

    def initialize_agi(self):
        openai_key = self.api_manager.get_api_key('openai')
        groq_key = self.api_manager.get_api_key('groq')
        
        if openai_key:
            chatter = GPT4o(openai_key)
        elif groq_key:
            chatter = GroqModel(groq_key)
        else:
            print("No suitable API key found. Please add an API key.")
            self.manage_api_keys()
            return self.initialize_agi()
        
        return AGI(chatter)

    def get_solution_from_agi(self, question):
        proposition_p, proposition_q = self.agi.learn_from_data(question)
        decision = self.agi.make_decisions(proposition_p, proposition_q)
        entry = DialogEntry(question, decision)
        store_in_stm(entry)
        return decision

    def add_api_key(self):
        service = self.service_input.value
        api_key = self.key_input.value
        if service and api_key:
            self.api_manager.save_api_key(service, api_key)
            ui.notify(f"API key for {service} added successfully.")
            self.list_api_keys()
        else:
            ui.notify("Service and API key must not be empty.")

    def list_api_keys(self):
        keys_container.clear()
        api_keys = self.api_manager.api_keys
        if api_keys:
            for service, key in api_keys.items():
                with keys_container:
                    ui.label(f"{service}: {key[:4]}...{key[-4:]}")
                    ui.button('Delete', on_click=lambda s=service: self.delete_api_key(s))
        else:
            ui.label("No API keys stored.")

    def delete_api_key(self, service):
        self.api_manager.remove_api_key(service)
        ui.notify(f"API key for {service} removed successfully.")
        self.list_api_keys()

# Initialize NiceAGI
fundamental_agi = NiceAGI()

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
        ui.markdown('[funAGI](https://github.com/autoGLM/funAGI)').classes('text-xs self-end mr-8 m-[-1em] text-primary')

logging.debug("starting funAGI")
ui.run(title='funAGI')

if __name__ == '__main__':
    main()
