import json
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from typing import Any, List
import asyncio
from qwen_agent.llm import get_chat_model
from qwen_agent.llm.schema import Message
from MCP.keys import API_KEY

MODEL_ID = "Qwen2.5-Coder-32B-Instruct"

SYSTEM_PROMPT = """\n# todolist Data Schema\n\nThis document outlines the database schema used in the `todolist` database. The schema includes several tables that manage different aspects of the application such as users, categories, tasks, and roles.\n\n## Tables\n\n### 1. `accesses`\n\n**Purpose:** Manages the roles assigned to users for specific categories.\n\n| Column Name | Type    | Constraints        | Description                          |\n|-------------|---------|--------------------|--------------------------------------|\n| category_id | integer | NOT NULL, Foreign Key<br>References `categories.id` | The ID of the category.                  |\n| user_id     | integer | NOT NULL, Foreign Key<br>References `users.id`       | The ID of the user.                      |\n| role        | integer | NOT NULL, [0, 4]   | Role level of the user in the category. |\n\n**Roles:**\n- **0:** Viewer - can only read tasks.\n- **1:** Doer - can change the status of tasks.\n- **2:** Writer - can create, delete, and edit tasks.\n- **3:** Administrator - can assign roles and manage users with roles up to level 2.\n- **4:** Owner - has all permissions including managing administrators.\n\n### 2. `categories`\n\n**Purpose:** Stores information about task categories.\n\n| Column Name | Type            | Constraints        | Description                   |\n|-------------|-----------------|--------------------|-------------------------------|\n| id          | integer         | NOT NULL, Primary Key, Auto-incremented | The unique identifier for the category. |\n| name        | varchar(64)     | NOT NULL             | The name of the category.     |\n| color       | varchar(6)      | NOT NULL             | The color associated with the category. |\n\n### 3. `status`\n\n**Purpose:** Defines the possible statuses for tasks.\n\n| Column Name | Type            | Constraints        | Description                       |\n|-------------|-----------------|--------------------|-----------------------------------|\n| id          | integer         | NOT NULL, Primary Key, Auto-incremented | The unique identifier for the status.  |\n| name        | varchar(20)     | NOT NULL             | The name of the status.           |\n| description | text            |                    | A description of the status.        |\n\n**Statuses:**\n- **1:** Not Started\n- **2:** In Progress\n- **3:** Done\n\n### 4. `tasks`\n\n**Purpose:** Manages the main tasks in the system.\n\n| Column Name | Type              | Constraints                                         | Description                               |\n|-------------|-------------------|-----------------------------------------------------|-------------------------------------------|\n| id          | integer           | NOT NULL, Primary Key, Auto-incremented               | The unique identifier for the task.       |\n| name        | text              | NOT NULL                                              | The name of the task.                     |\n| parent      | integer           |                                                     | ID of the parent task (if any).             |\n| status_id   | integer           | Foreign Key<br>References `status.id`                 | The current status of the task.           |\n| category_id | integer           | Foreign Key<br>References `categories.id`             | The category the task belongs to.         |\n| creation    | timestamp         | DEFAULT CURRENT_TIMESTAMP                             | Timestamp when the task was created.    |\n| edited      | timestamp         | DEFAULT CURRENT_TIMESTAMP, Updated by Trigger         | Timestamp when the task was last edited.|\n| order_id    | integer           |                                                     | Order index for the task.                 |\n\n### 5. `tokens`\n\n**Purpose:** Manages authentication tokens for users.\n\n| Column Name | Type              | Constraints                                         | Description                               |\n|-------------|-------------------|-----------------------------------------------------|-------------------------------------------|\n| token       | varchar(32)       | NOT NULL, Primary Key                               | The authentication token.                 |\n| user_id     | integer           | Foreign Key<br>References `users.id`                  | The user this token is linked to.         |\n| expiration  | timestamp         | DEFAULT CURRENT_TIMESTAMP + INTERVAL '1 hour'         | The expiration date of the token.         |\n\n### 6. `users`\n\n**Purpose:** Stores user accounts.\n\n| Column Name | Type              | Constraints                                         | Description                               |\n|-------------|-------------------|-----------------------------------------------------|-------------------------------------------|\n| id          | integer           | NOT NULL, Primary Key, Auto-incremented               | The unique identifier for the user.       |\n| name        | varchar(15)       | NOT NULL, Unique                                      | The user's name.                          |\n| password    | varchar(64)       | NOT NULL                                              | The hashed password for the user.         |\n\n## Relationships\n\n- **Accesses:** Each row connects a user to a category with a specific role.\n- **Tasks:** References `categories` and `statuses` to associate tasks with their respective categories and statuses.\n- **Tokens:** Associates a token with a specific user and tracks the token's expiration.\n\n# Instructions\n\nYou are a helpful assistant capable of accessing external functions and engaging in casual chat. \nUse the responses from these function calls to provide accurate and informative answers. \nThe answers should be natural and hide the fact that you are using tools to access real-time information. \nGuide the user about available tools and their capabilities. \nAlways utilize tools to access real-time information when required. \nEngage in a friendly manner to enhance the chat experience.\n \n# Tools\n \n{tools}\n \n# Notes \n \n- Ensure responses are based on the latest information available from function calls.\n- Maintain an engaging, supportive, and friendly tone throughout the dialogue.\n- Always highlight the potential of available tools to assist users comprehensively.\n- Use these tools whenever it could be useful. Do not hessitate to if it can give you a better perspective about how to help the user.\n- Use MCP tools autonomously. Avoid explaining what you can do without doing it\n- After executing a query, if it can be interesting to the user, summarise its result."""

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
        messages = [Message("system", SYSTEM_PROMPT.format(
            tools="\n- ".join(
                [f"{functions[f]['schema']['function']}" for f in functions]
            )
        ))]
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
        assert type(r) is dict
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
            "./mcp-postgres/postgres_server.py",
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

messages_save = []

async def ask_model(query: str) -> str:
    global messages_save
    server_params = StdioServerParameters(
        command="python3",
        args=[
            "./mcp-postgres/postgres_server.py",
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
            != "list_tables"
        }
        
        while True:
            try:
                user_input = input("\nEnter your prompt (or 'quit' to exit): ")
                if user_input.lower() in ["quit", "exit", "q"]:
                    break
                # Process the prompt and run agent loop
                response, messages_save = await agent_loop(user_input, tools, messages_save)
                return response
            except Exception as e:
                return f"\nError occurred: {e}"