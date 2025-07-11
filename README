# MCP Chatbot: a PoC
## Repository
This repository contains a fully functionnal chatbot that uses the Model Context Protocol (MCP).
It contains the following elements:
- An API allowing one to interact with a to-do list application.

    In order to use it, set up a postgresql database from the backup in go-api/postgres-backup.sql. It should have an user "goapi" whose password is "tatatoto". 
    
    Then, in order to start the API, run the command:
    ```bash
    ./go-api/go-api
    ```
- Several MCP servers:

    - One interacting with the database: `mcp-postgres/postgres_server.py`

    - One interacting with the API: `mcp-postgres/server2.py`

- Several in-terminal clients:

    - `MCP/client_llama.py`: a client using the model llama3 that can interact with the database

    - `MCP/client.py`: a client using the model qwen2.5 that can interact with the database

    - `MCP/client\ copy.py`: a client using the model qwen2.5 that can interact with the API

- A Terminal User Interface (TUI):

    `TUI/chat.py` allows one to chat with the MCP agent through a clean and easy to use interface

    It can be used thanks to the following command:

    ```bash
    python -m TUI.chat
    ```