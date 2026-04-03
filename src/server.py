from src.tools import search_wikipedia, read_local_text, write_markdown, send_email_mock

class ToolServer:
    """
    A lightweight registry mimicking an MCP (Model Context Protocol) server.
    Instead of complex JSON-RPC over stdio, it simply wraps our local Python functions.
    It exposes the available tools to our agents and handles requests to execute them.
    """
    def __init__(self):
        # Register our tools/skills
        self.registry = {
            "search_wikipedia": search_wikipedia,
            "read_local_text": read_local_text,
            "write_markdown": write_markdown,
            "send_email_mock": send_email_mock
        }

    def get_all_tools(self):
        """Returns the list of functions to pass to the LLM."""
        return list(self.registry.values())

    def execute(self, name: str, args: dict) -> str:
        """
        Executes a tool by name with the given arguments.
        This is exactly what an MCP server does when a model says "Call Tool X with Args Y".
        """
        if name not in self.registry:
            return f"Error: Tool '{name}' not found."
        
        try:
            print(f"\n[ToolServer] Executing '{name}'...")
            result = self.registry[name](**args)
            return str(result)
        except Exception as e:
            return f"Error executing {name}: {str(e)}"
