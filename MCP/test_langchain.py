from langchain_openai.llms.base import OpenAI
from MCP.keys import API_KEY
from mcp import ClientSession, StdioServerParameters
from typing import Any, List
from langchain_core.messages import (
    AIMessage,
    BaseMessage,
    HumanMessage,
)
import json
from mcp.client.stdio import stdio_client

SWAGGER = """{
  "openapi": "3.0.2",
  "info": {
    "title": "tasks manager",
    "version": "1.0.0",
    "description": "A simple API for managing tasks, categories, and users."
,    "baseUrl": "http://127.0.0.1:8080"},
  "paths": {
    "/tasks": {
      "get": {
        "summary": "Retrieve all tasks",
        "operationId": "getTasks",
        "responses": {
          "200": {
            "description": "A list of tasks",
            "content": {
              "application/json": {
                "schema": {
                  "type": "array",
                  "items": {
                    "$ref": "#/components/schemas/Task"
                  }
                }
              }
            }
          }
        }
      },
      "post": {
        "summary": "Create a new task",
        "operationId": "createTask",
        "requestBody": {
          "required": true,
          "content": {
            "application/json": {
              "schema": {
                "type": "object",
                "properties": {
                  "name": {
                    "type": "string"
                  },
                  "parent": {
                    "type": "integer"
                  },
                  "category": {
                    "type": "integer"
                  },
                }
              }
            }
          },
          "responses": {
            "201": {
              "description": "Task created successfully",
              "content": {
                "application/json": {
                  "schema": {
                    "type": "object",
                    "properties": {
                      "id": {
                        "type": "integer"
                      }
                    }
                  }
                }
              }
            }
          }
        }
      }
    },
    "/tasks/{id}": {
      "put": {
        "summary": "Update a task",
        "operationId": "updateTask",
        "parameters": [
          {
            "name": "id",
            "in": "path",
            "required": true,
            "schema": {
              "type": "integer"
            }
          }
        ],
        "requestBody": {
          "required": true,
          "content": {
            "application/json": {
              "schema": {
                "type": "object",
                "properties": {
                  "name": {
                    "type": "string"
                  },
                  "parent": {
                    "type": "integer"
                  },
                  "status": {
                    "type": "integer"
                  },
                  "category": {
                    "type": "integer"
                  },
                  }
              }
            }
          },
          "responses": {
            "200": {
              "description": "Task updated successfully",
              "content": {
                "application/json": {
                  "schema": {
                    "type": "object",
                    "properties": {
                      "message": {
                        "type": "string"
                      }
                    }
                  }
                }
              }
            }
          }
        }
      },
      "delete": {
        "summary": "Delete a task",
        "operationId": "deleteTask",
        "parameters": [
          {
            "name": "id",
            "in": "path",
            "required": true,
            "schema": {
              "type": "integer"
            }
          }
        ],
        "responses": {
          "200": {
            "description": "Task deleted successfully",
            "content": {
              "application/json": {
                "schema": {
                  "type": "object",
                  "properties": {
                    "message": {
                      "type": "string"
                    }
                  }
                }
              }
            }
          }
        }
      }
    },
        "/users": {
          "post": {
            "summary": "Create a new user",
            "operationId": "createUser",
            "requestBody": {
              "required": true,
              "content": {
                "application/json": {
                  "schema": {
                    "type": "object",
                    "properties": {
                      "name": {
                        "type": "string"
                      },
                      "password": {
                        "type": "string"
                      }
                    }
                  }
                }
              },
              "responses": {
                "201": {
                  "description": "User created successfully",
                  "content": {
                    "application/json": {
                      "schema": {
                        "type": "object",
                        "properties": {
                          "id": {
                            "type": "integer"
                          }
                        }
                      }
                    }
                  }
                }
              }
            }
          },
          "put": {
            "summary": "Update the authenticated user",
            "operationId": "updateUser",
            "requestBody": {
              "required": true,
              "content": {
                "application/json": {
                  "schema": {
                    "type": "object",
                    "properties": {
                      "name": {
                        "type": "string"
                      },
                      "password": {
                        "type": "string"
                      }
                    }
                  }
                }
              },
              "responses": {
                "200": {
                  "description": "User updated successfully",
                  "content": {
                    "application/json": {
                      "schema": {
                        "type": "object",
                        "properties": {
                          "message": {
                            "type": "string"
                          }
                        }
                      }
                    }
                  }
                }
              }
            }
          },
          "auth": {
            "post": {
              "summary": "Authenticate a user",
              "operationId": "authenticateUser",
              "requestBody": {
                "required": true,
                "content": {
                  "application/json": {
                    "schema": {
                      "type": "object",
                      "properties": {
                        "name": {
                          "type": "string"
                        },
                        "password": {
                          "type": "string"
                        }
                      }
                    }
                  }
                },
                "responses": {
                  "200": {
                    "description": "Authentication successful",
                    "content": {
                      "application/json": {
                        "schema": {
                          "type": "object",
                          "properties": {
                            "message": {
                              "type": "string"
                            },
                            "token": {
                              "type": "string"
                            }
                          }
                        }
                      }
                    }
                  }
                }
              }
            }
          },
          "delete": {
            "summary": "Delete the authenticated user",
            "operationId": "deleteUser",
            "responses": {
              "200": {
                "description": "User deleted successfully",
                "content": {
                  "application/json": {
                    "schema": {
                      "type": "object",
                      "properties": {
                        "message": {
                          "type": "string"
                        }
                      }
                    }
                  }
                }
              }
            }
          },
          "get": {
            "summary": "Search for users by name",
            "operationId": "searchUsers",
            "parameters": [
              {
                "name": "search",
                "in": "query",
                "required": true,
                "schema": {
                  "type": "string"
                }
              }
            ],
            "responses": {
              "200": {
                "description": "A list of users",
                "content": {
                  "application/json": {
                    "schema": {
                      "type": "array",
                      "items": {
                        "$ref": "#/components/schemas/User"
                      }
                    }
                  }
                }
              }
            }
          }
        },
        "/categories": {
          "post": {
            "summary": "Create a new category",
            "operationId": "createCategory",
            "requestBody": {
              "required": true,
              "content": {
                "application/json": {
                  "schema": {
                    "type": "object",
                    "properties": {
                      "name": {
                        "type": "string"
                      },
                      "color": {
                        "type": "string"
                      }
                    }
                  }
                }
              },
              "responses": {
                "201": {
                  "description": "Category created successfully",
                  "content": {
                    "application/json": {
                      "schema": {
                        "type": "object",
                        "properties": {
                          "message": {
                            "type": "string"
                          },
                          "category_id": {
                            "type": "integer"
                          }
                        }
                      }
                    }
                  }
                }
              }
            }
          },
          "get": {
            "summary": "Retrieve all categories",
            "operationId": "getCategories",
            "responses": {
              "200": {
                "description": "A list of categories",
                "content": {
                  "application/json": {
                    "schema": {
                      "type": "array",
                      "items": {
                        "$ref": "#/components/schemas/Category"
                      }
                    }
                  }
                }
              }
            }
          }
        },
        "/categories/{id}": {
          "delete": {
            "summary": "Delete a category",
            "operationId": "deleteCategory",
            "parameters": [
              {
                "name": "id",
                "in": "path",
                "required": true,
                "schema": {
                  "type": "integer"
                }
              }
            ],
            "responses": {
              "200": {
                "description": "Category deleted successfully",
                "content": {
                  "application/json": {
                    "schema": {
                      "type": "object",
                      "properties": {
                        "message": {
                          "type": "string"
                        }
                      }
                    }
                  }
                }
              }
            }
          },
          "put": {
            "summary": "Update a category",
            "operationId": "updateCategory",
            "parameters": [
              {
                "name": "id",
                "in": "path",
                "required": true,
                "schema": {
                  "type": "integer"
                }
              }
            ],
            "requestBody": {
              "required": true,
              "content": {
                "application/json": {
                  "schema": {
                    "type": "object",
                    "properties": {
                      "name": {
                        "type": "string"
                      },
                      "color": {
                        "type": "string"
                      }
                    }
                  }
                }
              },
              "responses": {
                "200": {
                  "description": "Category updated successfully",
                  "content": {
                    "application/json": {
                      "schema": {
                        "type": "object",
                        "properties": {
                          "message": {
                            "type": "string"
                          }
                        }
                      }
                    }
                  }
                }
              }
            }
          },
          "get": {
            "summary": "Retrieve a category by ID",
            "operationId": "getCategoryById",
            "parameters": [
              {
                "name": "id",
                "in": "path",
                "required": true,
                "schema": {
                  "type": "integer"
                }
              }
            ],
            "responses": {
              "200": {
                "description": "A category",
                "content": {
                  "application/json": {
                    "schema": {
                      "$ref": "#/components/schemas/Category"
                    }
                  }
                }
              }
            }
          }
        },
        "/categories/{id}/grant": {
          "put": {
            "summary": "Grant access to a category",
            "operationId": "grantAccess",
            "parameters": [
              {
                "name": "id",
                "in": "path",
                "required": true,
                "schema": {
                  "type": "integer"
                              }
                            },
                            {
                              "name": "level",
                              "in": "query",
                              "required": true,
                              "schema": {
                                "type": "integer"
                              }
                            },
                            {
                              "name": "user",
                              "in": "query",
                              "required": true,
                              "schema": {
                                "type": "integer"
                              }
                            }
                          ],
                          "responses": {
                            "200": {
                              "description": "Permissions granted successfully",
                              "content": {
                                "application/json": {
                                  "schema": {
                                    "type": "object",
                                    "properties": {
                                      "message": {
                                        "type": "string"
                                      }
                                    }
                                  }
                                }
                              }
                            }
                          }
                        }
                      }
                    },
                    "components": {
                      "schemas": {
                        "Task": {
                          "type": "object",
                          "properties": {
                            "id": {
                              "type": "integer"
                            },
                            "name": {
                              "type": "string"
                            },
                            "parent": {
                              "type": "integer"
                            },
                            "status_id": {
                              "type": "integer"
                            },
                            "category_id": {
                              "type": "integer"
                            },
                            "creation": {
                              "type": "string",
                              "format": "date-time"
                            },
                            "edited": {
                              "type": "string",
                              "format": "date-time"
                            },
                          }
                        },
                        "Status": {
                          "type": "object",
                          "properties": {
                            "id": {
                              "type": "integer"
                            },
                            "name": {
                              "type": "string"
                            },
                            "description": {
                              "type": "string"
                            }
                          }
                        },
                        "Category": {
                          "type": "object",
                          "properties": {
                            "id": {
                              "type": "integer"
                            },
                            "name": {
                              "type": "string"
                            },
                            "color": {
                              "type": "string"
                            }
                          }
                        },
                        "User": {
                          "type": "object",
                          "properties": {
                            "id": {
                              "type": "integer"
                            },
                            "username": {
                              "type": "string"
                            },
                            "password": {
                              "type": "string",
                              "format": "password"
                            }
                          }
                        },
                        "Token": {
                          "type": "object",
                          "properties": {
                            "id": {
                              "type": "integer"
                            },
                            "user_id": {
                              "type": "integer"
                            },
                            "token": {
                              "type": "string"
                            },
                            "expiration": {
                              "type": "string",
                              "format": "date-time"
                            }
                          }
                        }
                      }
                    }
                  }"""

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
- Do not use placeholder API keys.
- In order to authenticate in the 127.0.0.1:8080 API, you must add an auth token to the Authorization header under the format "Bearer <TOKEN>"
- In order to use a tool, simply end your answer by something of this form: {"name": "tool", "arguments": {"param_1": 35, "param_2": "test", "headers": {"Authorization": "Bearer abcdefGHIJKlmnOPQrstUvwXYZ"}}}

# Avoiding and Handling errors
1. **Strict Adherence to Data**: Only provide information based on the data recieved from the tools and the context provided. Do not infer or assume information that isn't supported by the data.
2. **Error Handling**: When a tool returns an error, acknowledge the error and inform the user. Do not fabricate a response to cover up the error.
3. **Verification Steps**: Before providing a response, verivy that the data makes sense and is consistent with expected results. If something feels off, double-check with additional tools or data points.
4. **Consistent Responses**: Maintain consistency in the responses. If a particular piece of information is not available, state that clearly instead of making up details.
5. **User Feedback**: Incorporate user feedback to identify and correct any inaccuracies or hallucinations. This helps in refining the process over time.
6. **Documentation and Guidelines**: Follow detailed documentation and guidelines strictly. These often include rules and constraints that help prevent incorrect or fabricated information.
7. **Transparency**: Be transparent about the sources of information. Clearly indicate when data is retrieved from tools or databases and when it is based on previous interactions.

Here's an example of how to handle an error without hallucinating:

**User Query**: "Get all the tasks from the API."

**Tool Call**: {"name": "perform_request", "arguments": {"url": "http://127.0.0.1:8080/tasks", "method": "GET", "headers": {"Authorization": "Bearer "}}}

**Tool Response**:
```json
{
    "error": "Unauthorized",
    "message": "Bearer token is missing or invalid."
}

**Assistant response**: I received an error from the API: "Unauthorized - Bearer token is missing or invalid." Please ensure you have a valid token and try again.
```
"""

# Basic Example (no streaming)
llm = OpenAI(
    base_url="https://qwen-2-5-coder-32b-instruct.endpoints.kepler.ai.cloud.ovh.net/api/openai_compat/v1",
    api_key=API_KEY,
    model="Qwen2.5-Coder-32B-Instruct",
    temperature=0.3,
    top_p=0.6
)

messages_save = []

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


async def ask_model(query: str) -> str:
    global messages_save
    server_params = StdioServerParameters(
        command="python3",
        args=[
            "mcp-postgres/server2.py",
        ],
        env=None
    )
    
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
        
        try:
            response, messages_save = await agent_loop(query, tools, messages_save)
            return response
        except Exception as e:
            return f"\n{type(e).__name__} occurred: {e}"

def reset_chat():
    global messages_save
    messages_save = []

TOKEN = ""

def set_token(token):
    global TOKEN
    TOKEN = token

def get_token():
    global TOKEN
    return "" if TOKEN == "" else f"\n\n# User information:\nThe user's token is '{TOKEN}'."

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

async def agent_loop(query: str, functions: List[dict], messages: List[BaseMessage] = None):
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
        messages = [None]
    messages = [BaseMessage(SWAGGER + SYSTEM_PROMPT.replace("{tools}", 
                                                        "\n- ".join(
                [f"{functions[f]['schema']['function']}" for f in functions]
            )
        ) + get_token(), type="System")] + messages[1:]
    messages.append(HumanMessage(query))
    
    ok = True
    
    while ok:
        ok = False
        answer = llm.invoke(
            messages
        )
        
        messages.append(AIMessage(answer))
        
        ok, fn_call = str_to_tool_call(answer)
        if ok:
            fn_name: str = fn_call.get('name', '')
            fn_args: dict = fn_call.get("arguments", dict())
            if not fn_name:
                print("Function call received without a valid function name.")
            callable_fn = None
            for fn in functions.values():
                if fn["schema"]['function']["name"] == fn_name:
                    callable_fn = fn['callable']
                    break
            if callable_fn is None:
                print(f"No callable found for function name: {fn_name}")
            try:
                fn_res: str = await callable_fn(**fn_args)
                if any([fn_res.startswith(e) for e in ["Invalid HTTP method: ", "Request is not allowed from this URL", "HTTP error occurred: ", "Connection error occurred: ", "Timeout error occurred: ", "An error occurred: "]]):
                    raise Exception(fn_res)
                messages.append({
                    "role": "function",
                    "name": fn_name,
                    "content": json.dumps(fn_res),
                })
                messages.append(BaseMessage(
                    "The tool call terminated. As I can't read anything said since my last question, you are going to sum up what happened since. You will avoid talking about technical details such as requests if possible.",
                    type="Tool"
                ))
            except Exception as e:
                print(f"Error executing function {fn_name}: {e}")
                messages.append({
                    "role": "function",
                    "name": fn_name,
                    "content": json.dumps(f"Error executing function: {e}"),
                })
                messages.append(BaseMessage(
                    "The tool call terminated with an error. You will explain what happened. You will explain the issue and establish a strategy about how to fix it. If it is very simple, try to do so. Else, just ask the user. If you cannot fulfill their request, just tell them.",
                    type="Tool"
                ))
    return messages[-1].get("content", ""), messages
