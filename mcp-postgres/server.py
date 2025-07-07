from contextlib import asynccontextmanager
from collections.abc import AsyncIterator
from dataclasses import dataclass
import requests

from mcp.server.fastmcp import FastMCP

# Create a named server
mcp = FastMCP("ToDoList")

# Access type-safe lifespan context in tools
@mcp.tool()
def get_auth_token() -> str:
    """
        Gives the authentication token of the user.
    """
    return "{\"token\": \"test\"}"
    return requests.api.post("http://localhost:8080/users/auth", json={"name": "alice", "password": "password1"}).content

@mcp.tool()
def get_categories(auth_token: str) -> str:
    """
    List the categories accessible by the user
    """
    return requests.api.get("http://localhost:8080/categories/", headers={"Authorization": f'Bearer {auth_token}'}).content

@mcp.tool()
def get_all_tasks(auth_token: str) -> str:
    """
    List the tasks accessible by the user
    """
    return requests.api.get("http://localhost:8080/tasks/", headers={"Authorization": f'Bearer {auth_token}'}).content


@mcp.tool()
def get_tasks_in_category(category_id: int, auth_token: str) -> str:
    """
    List the categories accessible by the user
    """
    return requests.api.get("http://localhost:8080/categories/{category_id}", headers={"Authorization": f'Bearer {auth_token}'}).content

mcp.run()