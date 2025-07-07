import json
from openai import AsyncOpenAI
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from typing import Any, List
import asyncio
from keys import API_KEY

MODEL_ID = "Meta-Llama-3_3-70B-Instruct"
 
# System prompt that guides the LLM's behavior and capabilities
# This helps the model understand its role and available tools
SYSTEM_PROMPT = """
# todolist Data Schema

This document outlines the database schema used in the `todolist` database. The schema includes several tables that manage different aspects of the application such as users, categories, tasks, and roles.

## Tables

### 1. `accesses`

**Purpose:** Manages the roles assigned to users for specific categories.

| Column Name | Type    | Constraints        | Description                          |
|-------------|---------|--------------------|--------------------------------------|
| category_id | integer | NOT NULL, Foreign Key<br>References `categories.id` | The ID of the category.                  |
| user_id     | integer | NOT NULL, Foreign Key<br>References `users.id`       | The ID of the user.                      |
| role        | integer | NOT NULL, [0, 4]   | Role level of the user in the category. |

**Roles:**
- **0:** Viewer - can only read tasks.
- **1:** Doer - can change the status of tasks.
- **2:** Writer - can create, delete, and edit tasks.
- **3:** Administrator - can assign roles and manage users with roles up to level 2.
- **4:** Owner - has all permissions including managing administrators.

### 2. `categories`

**Purpose:** Stores information about task categories.

| Column Name | Type            | Constraints        | Description                   |
|-------------|-----------------|--------------------|-------------------------------|
| id          | integer         | NOT NULL, Primary Key, Auto-incremented | The unique identifier for the category. |
| name        | varchar(64)     | NOT NULL             | The name of the category.     |
| color       | varchar(6)      | NOT NULL             | The color associated with the category. |

### 3. `status`

**Purpose:** Defines the possible statuses for tasks.

| Column Name | Type            | Constraints        | Description                       |
|-------------|-----------------|--------------------|-----------------------------------|
| id          | integer         | NOT NULL, Primary Key, Auto-incremented | The unique identifier for the status.  |
| name        | varchar(20)     | NOT NULL             | The name of the status.           |
| description | text            |                    | A description of the status.        |

**Statuses:**
- **1:** Not Started
- **2:** In Progress
- **3:** Done

### 4. `tasks`

**Purpose:** Manages the main tasks in the system.

| Column Name | Type              | Constraints                                         | Description                               |
|-------------|-------------------|-----------------------------------------------------|-------------------------------------------|
| id          | integer           | NOT NULL, Primary Key, Auto-incremented               | The unique identifier for the task.       |
| name        | text              | NOT NULL                                              | The name of the task.                     |
| parent      | integer           |                                                     | ID of the parent task (if any).             |
| status_id   | integer           | Foreign Key<br>References `status.id`                 | The current status of the task.           |
| category_id | integer           | Foreign Key<br>References `categories.id`             | The category the task belongs to.         |
| creation    | timestamp         | DEFAULT CURRENT_TIMESTAMP                             | Timestamp when the task was created.    |
| edited      | timestamp         | DEFAULT CURRENT_TIMESTAMP, Updated by Trigger         | Timestamp when the task was last edited.|
| order_id    | integer           |                                                     | Order index for the task.                 |

### 5. `tokens`

**Purpose:** Manages authentication tokens for users.

| Column Name | Type              | Constraints                                         | Description                               |
|-------------|-------------------|-----------------------------------------------------|-------------------------------------------|
| token       | varchar(32)       | NOT NULL, Primary Key                               | The authentication token.                 |
| user_id     | integer           | Foreign Key<br>References `users.id`                  | The user this token is linked to.         |
| expiration  | timestamp         | DEFAULT CURRENT_TIMESTAMP + INTERVAL '1 hour'         | The expiration date of the token.         |

### 6. `users`

**Purpose:** Stores user accounts.

| Column Name | Type              | Constraints                                         | Description                               |
|-------------|-------------------|-----------------------------------------------------|-------------------------------------------|
| id          | integer           | NOT NULL, Primary Key, Auto-incremented               | The unique identifier for the user.       |
| name        | varchar(15)       | NOT NULL, Unique                                      | The user's name.                          |
| password    | varchar(64)       | NOT NULL                                              | The hashed password for the user.         |

## Relationships

- **Accesses:** Each row connects a user to a category with a specific role.
- **Tasks:** References `categories` and `statuses` to associate tasks with their respective categories and statuses.
- **Tokens:** Associates a token with a specific user and tracks the token's expiration.

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
"""
 
 
# Initialize OpenAI client with HuggingFace inference API
# This allows us to use Llama models through HuggingFace's API
client = AsyncOpenAI(
    base_url="https://llama-3-3-70b-instruct.endpoints.kepler.ai.cloud.ovh.net/api/openai_compat/v1",
    api_key=API_KEY
)
 
 
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
 
 
async def agent_loop(query: str, tools: dict, messages: List[dict] = None):
    """
    Main interaction loop that processes user queries using the LLM and available tools.
 
    This function:
    1. Sends the user query to the LLM with context about available tools
    2. Processes the LLM's response, including any tool calls
    3. Returns the final response to the user
 
    Args:
        query: User's input question or command
        tools: Dictionary of available database tools and their schemas
        messages: List of messages to pass to the LLM, defaults to None
    """
    messages = (
        [
            {
                "role": "system",
                "content": SYSTEM_PROMPT.format(
                    tools="\n- ".join(
                        [
                            f"{t['name']}: {t['schema']['function']['description']}"
                            for t in tools.values()
                        ]
                    )
                ),  # Creates System prompt based on available MCP server tools
            },
        ]
        if messages is None
        else messages  # reuse existing messages if provided
    )
    # add user query to the messages list
    messages.append({"role": "user", "content": query})
 
    # Query LLM with the system prompt, user query, and available tools
    first_response = await client.chat.completions.create(
        model=MODEL_ID,
        messages=messages,
        tools=([t["schema"] for t in tools.values()] if len(tools) > 0 else None),
        max_tokens=4096,
        temperature=0,
    )
    # detect how the LLM call was completed:
    # tool_calls: if the LLM used a tool
    # stop: If the LLM generated a general response, e.g. "Hello, how can I help you today?"
    stop_reason = (
        "tool_calls"
        if first_response.choices[0].message.tool_calls is not None
        else first_response.choices[0].finish_reason
    )
 
    if stop_reason == "tool_calls":
        # Extract tool use details from response
        for tool_call in first_response.choices[0].message.tool_calls:
            arguments = (
                json.loads(tool_call.function.arguments)
                if isinstance(tool_call.function.arguments, str)
                else tool_call.function.arguments
            )
            # Call the tool with the arguments using our callable initialized in the tools dict
            tool_result = await tools[tool_call.function.name]["callable"](**arguments)
            # Add the tool result to the messages list
            messages.append(
                {
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "name": tool_call.function.name,
                    "content": json.dumps(tool_result),
                }
            )
 
        # Query LLM with the user query and the tool results
        new_response = await client.chat.completions.create(
            model=MODEL_ID,
            messages=messages,
        )
 
    elif stop_reason == "stop":
        # If the LLM stopped on its own, use the first response
        new_response = first_response
 
    else:
        raise ValueError(f"Unknown stop reason: {stop_reason}")
 
    # Add the LLM response to the messages list
    messages.append(
        {"role": "assistant", "content": new_response.choices[0].message.content}
    )
 
    # Return the LLM response and messages
    return new_response.choices[0].message.content, messages
 
 
async def main():
    """
    Main function that sets up the MCP server, initializes tools, and runs the interactive loop.
    The server is run in a Docker container to ensure isolation and consistency.
    """
    # Configure Docker-based MCP server for SQLite
    server_params = StdioServerParameters(
        command="python3",
        args=[
            "../mcp-postgres/postgres_server.py",
        ],
        env=None,
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
 
        # Start interactive prompt loop for user queries
        messages = None
        while True:
            try:
                # Get user input and check for exit commands
                user_input = input("\nEnter your prompt (or 'quit' to exit): ")
                if user_input.lower() in ["quit", "exit", "q"]:
                    break
 
                # Process the prompt and run agent loop
                response, messages = await agent_loop(user_input, tools, messages)
                print("\nResponse:", response)
                # print("\nMessages:", messages)
            except KeyboardInterrupt:
                print("\nExiting...")
                break
            except Exception as e:
                print(f"\nError occurred: {e}")
 
 
if __name__ == "__main__":
    asyncio.run(main())