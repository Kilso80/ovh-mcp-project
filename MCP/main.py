{
    "servers": {
    "postgres": {
      "command": "/root/test-project/mcp-postgres/venv/bin/python",
      "args": [
        "/root/test-project/mcp-postgres/postgres_server.py"
      ],
      "env": {
        "POSTGRES_CONNECTION_STRING": "postgresql://goapi:tototata@localhost:5432/todolist?ssl=true"
      }
    }
  }
}