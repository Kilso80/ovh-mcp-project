from keys import API_KEY
import json
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from typing import Any, List
import asyncio
from qwen_agent.llm import get_chat_model
from qwen_agent.llm.schema import Message

MODEL_ID = "Qwen2.5-Coder-32B-Instruct"

SWAGGER = """{\n  "openapi": "3.0.2",\n  "info": {\n    "title": "Go-API",\n    "version": "1.0.0",\n    "description": "A simple API for managing tasks, categories, and users."\n,    "baseUrl": "http://127.0.0.1:8080"},\n  "paths": {\n    "/tasks": {\n      "get": {\n        "summary": "Retrieve all tasks",\n        "operationId": "getTasks",\n        "responses": {\n          "200": {\n            "description": "A list of tasks",\n            "content": {\n              "application/json": {\n                "schema": {\n                  "type": "array",\n                  "items": {\n                    "$ref": "#/components/schemas/Task"\n                  }\n                }\n              }\n            }\n          }\n        }\n      },\n      "post": {\n        "summary": "Create a new task",\n        "operationId": "createTask",\n        "requestBody": {\n          "required": true,\n          "content": {\n            "application/json": {\n              "schema": {\n                "type": "object",\n                "properties": {\n                  "name": {\n                    "type": "string"\n                  },\n                  "parent": {\n                    "type": "integer"\n                  },\n                  "category": {\n                    "type": "integer"\n                  },\n                  "priority_order": {\n                    "type": "integer"\n                  }\n                }\n              }\n            }\n          },\n          "responses": {\n            "201": {\n              "description": "Task created successfully",\n              "content": {\n                "application/json": {\n                  "schema": {\n                    "type": "object",\n                    "properties": {\n                      "id": {\n                        "type": "integer"\n                      }\n                    }\n                  }\n                }\n              }\n            }\n          }\n        }\n      }\n    },\n    "/tasks/{id}": {\n      "put": {\n        "summary": "Update a task",\n        "operationId": "updateTask",\n        "parameters": [\n          {\n            "name": "id",\n            "in": "path",\n            "required": true,\n            "schema": {\n              "type": "integer"\n            }\n          }\n        ],\n        "requestBody": {\n          "required": true,\n          "content": {\n            "application/json": {\n              "schema": {\n                "type": "object",\n                "properties": {\n                  "name": {\n                    "type": "string"\n                  },\n                  "parent": {\n                    "type": "integer"\n                  },\n                  "status": {\n                    "type": "integer"\n                  },\n                  "category": {\n                    "type": "integer"\n                  },\n                  "priority_order": {\n                    "type": "integer"\n                  }\n                }\n              }\n            }\n          },\n          "responses": {\n            "200": {\n              "description": "Task updated successfully",\n              "content": {\n                "application/json": {\n                  "schema": {\n                    "type": "object",\n                    "properties": {\n                      "message": {\n                        "type": "string"\n                      }\n                    }\n                  }\n                }\n              }\n            }\n          }\n        }\n      },\n      "delete": {\n        "summary": "Delete a task",\n        "operationId": "deleteTask",\n        "parameters": [\n          {\n            "name": "id",\n            "in": "path",\n            "required": true,\n            "schema": {\n              "type": "integer"\n            }\n          }\n        ],\n        "responses": {\n          "200": {\n            "description": "Task deleted successfully",\n            "content": {\n              "application/json": {\n                "schema": {\n                  "type": "object",\n                  "properties": {\n                    "message": {\n                      "type": "string"\n                    }\n                  }\n                }\n              }\n            }\n          }\n        }\n      }\n    },\n    "/users": {\n      "post": {\n        "summary": "Create a new user",\n        "operationId": "createUser",\n        "requestBody": {\n          "required": true,\n          "content": {\n            "application/json": {\n              "schema": {\n                "type": "object",\n                "properties": {\n                  "name": {\n                    "type": "string"\n                  },\n                  "password": {\n                    "type": "string"\n                  }\n                }\n              }\n            }\n          },\n          "responses": {\n            "201": {\n              "description": "User created successfully",\n              "content": {\n                "application/json": {\n                  "schema": {\n                    "type": "object",\n                    "properties": {\n                      "id": {\n                        "type": "integer"\n                      }\n                    }\n                  }\n                }\n              }\n            }\n          }\n        }\n      },\n      "put": {\n        "summary": "Update the authenticated user",\n        "operationId": "updateUser",\n        "requestBody": {\n          "required": true,\n          "content": {\n            "application/json": {\n              "schema": {\n                "type": "object",\n                "properties": {\n                  "name": {\n                    "type": "string"\n                  },\n                  "password": {\n                    "type": "string"\n                  }\n                }\n              }\n            }\n          },\n          "responses": {\n            "200": {\n              "description": "User updated successfully",\n              "content": {\n                "application/json": {\n                  "schema": {\n                    "type": "object",\n                    "properties": {\n                      "message": {\n                        "type": "string"\n                      }\n                    }\n                  }\n                }\n              }\n            }\n          }\n        }\n      },\n      "auth": {\n        "post": {\n          "summary": "Authenticate a user",\n          "operationId": "authenticateUser",\n          "requestBody": {\n            "required": true,\n            "content": {\n              "application/json": {\n                "schema": {\n                  "type": "object",\n                  "properties": {\n                    "name": {\n                      "type": "string"\n                    },\n                    "password": {\n                      "type": "string"\n                    }\n                  }\n                }\n              }\n            },\n            "responses": {\n              "200": {\n                "description": "Authentication successful",\n                "content": {\n                  "application/json": {\n                    "schema": {\n                      "type": "object",\n                      "properties": {\n                        "message": {\n                          "type": "string"\n                        },\n                        "token": {\n                          "type": "string"\n                        }\n                      }\n                    }\n                  }\n                }\n              }\n            }\n          }\n        }\n      },\n      "delete": {\n        "summary": "Delete the authenticated user",\n        "operationId": "deleteUser",\n        "responses": {\n          "200": {\n            "description": "User deleted successfully",\n            "content": {\n              "application/json": {\n                "schema": {\n                  "type": "object",\n                  "properties": {\n                    "message": {\n                      "type": "string"\n                    }\n                  }\n                }\n              }\n            }\n          }\n        }\n      },\n      "get": {\n        "summary": "Search for users by name",\n        "operationId": "searchUsers",\n        "parameters": [\n          {\n            "name": "search",\n            "in": "query",\n            "required": true,\n            "schema": {\n              "type": "string"\n            }\n          }\n        ],\n        "responses": {\n          "200": {\n            "description": "A list of users",\n            "content": {\n              "application/json": {\n                "schema": {\n                  "type": "array",\n                  "items": {\n                    "$ref": "#/components/schemas/User"\n                  }\n                }\n              }\n            }\n          }\n        }\n      }\n    },\n    "/categories": {\n      "post": {\n        "summary": "Create a new category",\n        "operationId": "createCategory",\n        "requestBody": {\n          "required": true,\n          "content": {\n            "application/json": {\n              "schema": {\n                "type": "object",\n                "properties": {\n                  "name": {\n                    "type": "string"\n                  },\n                  "color": {\n                    "type": "string"\n                  }\n                }\n              }\n            }\n          },\n          "responses": {\n            "201": {\n              "description": "Category created successfully",\n              "content": {\n                "application/json": {\n                  "schema": {\n                    "type": "object",\n                    "properties": {\n                      "message": {\n                        "type": "string"\n                      },\n                      "category_id": {\n                        "type": "integer"\n                      }\n                    }\n                  }\n                }\n              }\n            }\n          }\n        }\n      },\n      "get": {\n        "summary": "Retrieve all categories",\n        "operationId": "getCategories",\n        "responses": {\n          "200": {\n            "description": "A list of categories",\n            "content": {\n              "application/json": {\n                "schema": {\n                  "type": "array",\n                  "items": {\n                    "$ref": "#/components/schemas/Category"\n                  }\n                }\n              }\n            }\n          }\n        }\n      }\n    },\n    "/categories/{id}": {\n      "delete": {\n        "summary": "Delete a category",\n        "operationId": "deleteCategory",\n        "parameters": [\n          {\n            "name": "id",\n            "in": "path",\n            "required": true,\n            "schema": {\n              "type": "integer"\n            }\n          }\n        ],\n        "responses": {\n          "200": {\n            "description": "Category deleted successfully",\n            "content": {\n              "application/json": {\n                "schema": {\n                  "type": "object",\n                  "properties": {\n                    "message": {\n                      "type": "string"\n                    }\n                  }\n                }\n              }\n            }\n          }\n        }\n      },\n      "put": {\n        "summary": "Update a category",\n        "operationId": "updateCategory",\n        "parameters": [\n          {\n            "name": "id",\n            "in": "path",\n            "required": true,\n            "schema": {\n              "type": "integer"\n            }\n          }\n        ],\n        "requestBody": {\n          "required": true,\n          "content": {\n            "application/json": {\n              "schema": {\n                "type": "object",\n                "properties": {\n                  "name": {\n                    "type": "string"\n                  },\n                  "color": {\n                    "type": "string"\n                  }\n                }\n              }\n            }\n          },\n          "responses": {\n            "200": {\n              "description": "Category updated successfully",\n              "content": {\n                "application/json": {\n                  "schema": {\n                    "type": "object",\n                    "properties": {\n                      "message": {\n                        "type": "string"\n                      }\n                    }\n                  }\n                }\n              }\n            }\n          }\n        }\n      },\n      "get": {\n        "summary": "Retrieve a category by ID",\n        "operationId": "getCategoryById",\n        "parameters": [\n          {\n            "name": "id",\n            "in": "path",\n            "required": true,\n            "schema": {\n              "type": "integer"\n            }\n          }\n        ],\n        "responses": {\n          "200": {\n            "description": "A category",\n            "content": {\n              "application/json": {\n                "schema": {\n                  "$ref": "#/components/schemas/Category"\n                }\n              }\n            }\n          }\n        }\n      }\n    },\n    "/categories/{id}/grant": {\n      "put": {\n        "summary": "Grant access to a category",\n        "operationId": "grantAccess",\n        "parameters": [\n          {\n            "name": "id",\n            "in": "path",\n            "required": true,\n            "schema": {\n              "type": "integer"\n            }\n          },\n          {\n            "name": "level",\n            "in": "query",\n            "required": true,\n            "schema": {\n              "type": "integer"\n            }\n          },\n          {\n            "name": "user",\n            "in": "query",\n            "required": true,\n            "schema": {\n              "type": "integer"\n            }\n          }\n        ],\n        "responses": {\n          "200": {\n            "description": "Permissions granted successfully",\n            "content": {\n              "application/json": {\n                "schema": {\n                  "type": "object",\n                  "properties": {\n                    "message": {\n                      "type": "string"\n                    }\n                  }\n                }\n              }\n            }\n          }\n        }\n      }\n    }\n  },\n  "components": {\n    "schemas": {\n      "Task": {\n        "type": "object",\n        "properties": {\n          "id": {\n            "type": "integer"\n          },\n          "name": {\n            "type": "string"\n          },\n          "parent": {\n            "type": "integer"\n          },\n          "status_id": {\n            "type": "integer"\n          },\n          "category_id": {\n            "type": "integer"\n          },\n          "creation": {\n            "type": "string",\n            "format": "date-time"\n          },\n          "edited": {\n            "type": "string",\n            "format": "date-time"\n          },\n          "order_id": {\n            "type": "integer"\n          }\n        }\n      },\n      "Status": {\n        "type": "object",\n        "properties": {\n          "id": {\n            "type": "integer"\n          },\n          "name": {\n            "type": "string"\n          },\n          "description": {\n            "type": "string"\n          }\n        }\n      },\n      "Category": {\n        "type": "object",\n        "properties": {\n          "id": {\n            "type": "integer"\n          },\n          "name": {\n            "type": "string"\n          },\n          "color": {\n            "type": "string"\n          }\n        }\n      },\n      "User": {\n        "type": "object",\n        "properties": {\n          "id": {\n            "type": "integer"\n          },\n          "username": {\n            "type": "string"\n          },\n          "password": {\n            "type": "string",\n            "format": "password"\n          }\n        }\n      },\n      "Token": {\n        "type": "object",\n        "properties": {\n          "id": {\n            "type": "integer"\n          },\n          "user_id": {\n            "type": "integer"\n          },\n          "token": {\n            "type": "string"\n          },\n          "expiration": {\n            "type": "string",\n            "format": "date-time"\n          }\n        }\n      }\n    }\n  }\n}"""

SYSTEM_PROMPT = """
# Instructions

You are a helpful assistant capable of accessing external functions and engaging in casual chat. 
Use the responses from these function calls to provide accurate and informative answers. 
The answers should be natural and hide the fact that you are using tools to access real-time information. 
Guide the user about available tools and their capabilities. 
Always utilize tools to access real-time information when required. 
Engage in a friendly manner to enhance the chat experience.
 
# Tools
 
{tools}
 
# Notes 
 
- Ensure responses are based on the latest information available from function calls.
- Maintain an engaging, supportive, and friendly tone throughout the dialogue.
- Always highlight the potential of available tools to assist users comprehensively.
- Use these tools whenever it could be useful. Do not hessitate to if it can give you a better perspective about how to help the user.
- Use MCP tools autonomously. Avoid explaining what you can do without doing it
- Use APIs whenever needed. Do not hesitate to enquire about their structure by using your tools.
- After executing a query, if it can be interesting to the user, summarise its result.
"""

client = get_chat_model({
    "model": MODEL_ID,
    "model_server": "https://qwen-2-5-coder-32b-instruct.endpoints.kepler.ai.cloud.ovh.net/api/openai_compat/v1",
    "api_key": API_KEY
})


class MCPClient:
    """
    A client class for interacting with the MCP (Model Control Protocol) server.
    This class manages the connection and communication with the SQLite database through MCP.
    """

    def __init__(self, server_params: StdioServerParameters):
        """Initialize the MCP client with server parameters"""
        self.server_params = server_params
        self.session = None
        self._client = None
 
    async def __aenter__(self):
        """Async context manager entry"""
        await self.connect()
        return self
 
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session:
            await self.session.__aexit__(exc_type, exc_val, exc_tb)
        if self._client:
            await self._client.__aexit__(exc_type, exc_val, exc_tb)
            
    async def connect(self):
        """Establishes connection to MCP server"""
        self._client = stdio_client(self.server_params)
        self.read, self.write = await self._client.__aenter__()
        session = ClientSession(self.read, self.write)
        self.session = await session.__aenter__()
        await self.session.initialize()
        
    async def get_available_tools(self) -> List[Any]:
        """
        Retrieve a list of available tools from the MCP server.
        """
        if not self.session:
            raise RuntimeError("Not connected to MCP server")
        
        tools = await self.session.list_tools()
        
        _, _, tools_list = tools
        _, tools_list = tools_list
        return tools_list
 
    def call_tool(self, tool_name: str) -> Any:
        """
        Create a callable function for a specific tool.
        This allows us to execute database operations through the MCP server.

        Args:
            tool_name: The name of the tool to create a callable for

        Returns:
            A callable async function that executes the specified tool
        """
        if not self.session:
            raise RuntimeError("Not connected to MCP server")
        
        async def callable(*args, **kwargs):
            response = await self.session.call_tool(tool_name, arguments=kwargs)
            return response.content[0].text
        
        return callable


async def agent_loop(query: str, functions: List[dict], messages: List[Message] = None):
    """
    Main interaction loop that processes user queries using the LLM and available functions.

    This function:
    1. Sends the user query to the LLM with context about available functions
    2. Processes the LLM's response, including any function calls
    3. Returns the final response to the user

    Args:
        query: User's input question or command
        functions: List of available database functions and their schemas
        messages: List of messages to pass to the LLM, defaults to None
    """
    if messages == []:
        messages = [Message("system", SWAGGER + "\n" + SYSTEM_PROMPT.format(
            tools="\n- ".join(
                [f"{functions[f]['schema']['function']}" for f in functions]
            )
        ) + '\n- In order to use a tool, simply end your answer by something of this form: {"name": "tool", "arguments": {"param_1": 35, "param_2": "test", "headers": {"Authorization": "Bearer abcdefGHIJKlmnOPQrstUvwXYZ"}}}')]
    messages.append(Message("user", query))
    
    ok = True
    last = None
    
    while ok:
        ok = False
        responses = client.chat(
            messages=messages,
            functions=[functions[f]['schema']['function'] for f in functions],
            extra_generate_cfg=dict(parallel_function_calls=True)
        )
        
        message = None
        for r in responses:
            for m in r:
                message = m
        ok, fn_call = str_to_tool_call(message.get("content"))
        if ok: print(fn_call)
        if ok and fn_call != last:
            last = fn_call
            fn_name: str = fn_call.get('name', '')
            fn_args: dict = fn_call.get("arguments", dict())
            if not fn_name:
                print("Function call received without a valid function name.")
            callable_fn = None
            for fn in functions.values():
                if fn["schema"]['function']['name'] == fn_name:
                    callable_fn = fn['callable']
                    break
            if callable_fn is None:
                print(f"No callable found for function name: {fn_name}")
            try:
                fn_res: str = await callable_fn(**fn_args)
                messages.append({
                    "role": "function",
                    "name": fn_name,
                    "content": json.dumps(fn_res),
                })
                print(fn_res)
            except Exception as e:
                print(f"Error executing function {fn_name}: {e}")
                messages.append({
                    "role": "function",
                    "name": fn_name,
                    "content": json.dumps(f"Error executing function: {e}"),
                })
            messages.append({
                "role": "assistant",
                "content": "The tool call terminated. Users can't read anything said between their question and here. Now, answer them. Do not talk about requests or technical details unless needed to answer them. You also may do so to use tools another time.",
            })
        messages.append(message)
    return messages[-1].get("content", ""), messages


def str_to_tool_call(string):
    if '}' not in string:
        return False, None
    l = string.split('}')
    string = '}'.join(l[:-1]) + '}'
    i = len(string) - 1
    c = 1
    while i > 0 and c > 0:
        i -= 1
        c += (string[i] == '}') - (string[i] == '{')
    if string[i] != '{':
        return False, None
    try:
        r = eval(string[i:].replace(": null", ": None"))
    except:
        return False, None
    return r.get("name") is not None and r.get("arguments") is not None, r


async def main():
    """
    Main function that sets up the MCP server, initializes tools, and runs the interactive loop.
    The server is run in a Docker container to ensure isolation and consistency.
    """
    server_params = StdioServerParameters(
        command="python3",
        args=[
            "../mcp-postgres/server2.py",
        ],
        env=None
    )
    
    # Start MCP client and create interactive session
    async with MCPClient(server_params) as mcp_client:
        # Get available database tools and prepare them for the LLM
        mcp_tools = await mcp_client.get_available_tools()
        # Convert MCP tools into a format the LLM can understand and use
        tools = {
            tool.name: {
                "name": tool.name,
                "callable": mcp_client.call_tool(
                    tool.name
                ),  # returns a callable function for the rpc call
                "schema": {
                    "type": "function",
                    "function": {
                        "name": tool.name,
                        "description": tool.description,
                        "parameters": tool.inputSchema,
                    },
                },
            }
            for tool in mcp_tools
            if tool.name
            != "list_tables"  # Excludes list_tables tool as it has an incorrect schema
        }
        
        messages = []
        while True:
            try:
                user_input = input("\nEnter your prompt (or 'quit' to exit): ")
                if user_input.lower() in ["quit", "exit", "q"]:
                    break
                # Process the prompt and run agent loop
                response, messages = await agent_loop(user_input, tools, messages)
                print("\nResponse:", response)
            except KeyboardInterrupt:
                print("\nExiting...")
                break
            except Exception as e:
                print(f"\nError occurred: {e}")


if __name__ == "__main__":
    asyncio.run(main())