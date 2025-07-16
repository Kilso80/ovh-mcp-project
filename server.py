from textual_serve.server import Server

s = Server("source .venv/bin/activate;python -m TUI.chat", port=5173)
s.serve()