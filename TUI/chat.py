from textual.app import App
from textual.widgets import Footer, Header, Button, Static, TextArea, Markdown, Input
from textual.containers import ScrollableContainer
from textual import on
from MCP.client_copy import ask_model, reset_chat
from textual.binding import Binding

class ChatBotApp(App):
    BINDINGS = [
        ("d", "toggle_dark", "Toggle dark mode"),
        ("ctrl+n", "create_new_chat", "Create new chat"),
    ]
    
    CSS_PATH = "style.tcss"
    
    def compose(self):
        yield Header(name="MCP ChatBot")
        yield Conversation()
        yield ChatInput()
        yield Footer()
        
    def action_create_new_chat(self):
        reset_chat()
        self.query_exactly_one("Conversation ScrollableContainer").remove_children()
        

class Conversation(Static):
    def compose(self):
        yield ScrollableContainer()

class Message(Static):
    def __init__(self, message: str, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.content = Markdown(markdown=message)
        self.content.styles.width = max(15, *[len(l) for l in message.split('\n')]) + 5
    
    async def set_text(self, text):
        self.content.styles.width = max(15, *[len(l) for l in text.split('\n')]) + 5
        await self.content.update(text)
    
    def compose(self):
        yield self.content

class BotMessage(Message):
    def __init__(self, message, *args, **kwargs):
        super().__init__(message, *args, **kwargs)

class UserMessage(Message):
    def __init__(self, message, *args, **kwargs):
        super().__init__(message, *args, **kwargs)

class ChatInput(Static):
    BINDINGS = [
        Binding("shift+enter", "use_multiline", "Switch to a multi-line text editor")
    ]
    def compose(self):
        i = Input(placeholder="Enter your question here")
        yield i
        yield TextArea(compact=True, id="input")
        yield Button('Send', "primary")
        
    def action_use_multiline(self):
        self.change_input_type(False)
        
    def change_input_type(self, oneline: bool):
        if self.children[1].display not in [None, False] and oneline:
            self.children[0].value = self.children[1].text
        if self.children[0].display not in [None, False] and not oneline:
            self.children[1].text = self.children[0].value
        self.children[0].display = [False, "block"][oneline]
        self.children[1].display = ["block", False][oneline]
    
    @on(Button.Pressed)
    async def action_ask_agent(self):
        query = ""
        if self.children[0].display not in [None, False]:
            query = self.children[0].value
            self.children[0].value = ""
        else:
            query = self.children[1].text
            self.children[1].text = ""
        msg = UserMessage("\n\n".join(query.split('\n')))
        self.query_exactly_one("Button").disabled = True
        msg_list = self.parent.query_exactly_one("Conversation ScrollableContainer")
        msg_list.mount(msg)
        msg_list.scroll_end()
        answer = BotMessage("")
        answer.set_loading(True)
        msg_list.mount(answer)
        msg_list.scroll_end()
        ans_text = await ask_model(query)
        if ans_text == "": ans_text = "An error has been encountered"
        await answer.set_text(ans_text)
        answer.refresh()
        answer.set_loading(False)
        msg_list.scroll_end()
        self.query_exactly_one("Button").disabled = False
        self.change_input_type(True)

if __name__ == "__main__":
    ChatBotApp().run()