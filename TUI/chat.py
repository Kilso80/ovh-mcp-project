from textual.app import App
from textual.widgets import Footer, Header, Button, Static, TextArea, Markdown
from textual.containers import ScrollableContainer
from textual import on
from MCP.client_copy import ask_model

class ChatBotApp(App):
    BINDINGS = [
        ("d", "toggle_dark", "Toggle dark mode"),
    ]
    
    CSS_PATH = "style.tcss"
    
    def compose(self):
        yield Header(name="MCP ChatBot")
        yield Conversation()
        yield ChatInput()
        yield Footer()
        
    def action_send_msg(self):
        self.action_toggle_dark()

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
    def compose(self):
        # yield Input(placeholder="Enter your question here")
        yield TextArea(disabled=False, compact=True, id="input")
        yield Button('Send', "primary")
    
    @on(Button.Pressed)
    async def action_ask_agent(self):
        query = self.children[0].text
        self.children[0].text = ""
        msg = UserMessage('\n\n'.join(query.split('\n')))
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
        

if __name__ == "__main__":
    ChatBotApp().run()