import requests
from mcp.server.fastmcp import FastMCP

# Create a named server
mcp = FastMCP("API Access")

@mcp.tool()
def perform_request(url: str, method: str, body: dict[str, str] = dict()) -> str:
    """
    Perform a web call on `url` with the method `method`.
    
    Args:
        - url:
            The URL on which the request should be performed
        - method:
            The HTTP method to use on the URL. It must be one of "GET", "POST", "PUT", "DELETE"
        - body:
            The body of the request. It should be a dict that will be used as a JSON.
    Returns:
        - str: The response content or an error message.
    """
    try:
        if method.upper() == "GET":
            response = requests.get(url, json=body)
        elif method.upper() == "POST":
            response = requests.post(url, json=body)
        elif method.upper() == "PUT":
            response = requests.put(url, json=body)
        elif method.upper() == "DELETE":
            response = requests.delete(url, json=body)
        else:
            return f"Invalid HTTP method: {method}"

        response.raise_for_status()
        return response.text
    except requests.exceptions.HTTPError as http_err:
        return f"HTTP error occurred: {http_err}"
    except requests.exceptions.ConnectionError as conn_err:
        return f"Connection error occurred: {conn_err}"
    except requests.exceptions.Timeout as timeout_err:
        return f"Timeout error occurred: {timeout_err}"
    except requests.exceptions.RequestException as req_err:
        return f"An error occurred: {req_err}"

mcp.run()