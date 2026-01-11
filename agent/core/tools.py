from typing import Dict, Any

class ToolRegistry:
    def __init__(self):
        self.tools = {}

    def register(self, name: str, func):
        self.tools[name] = func

    async def call(self, name: str, args: Dict[str, Any]) -> str:
        if name not in self.tools:
            return f"Error: Tool {name} not found."
        try:
            return await self.tools[name](**args)
        except Exception as e:
            return f"Error calling tool {name}: {str(e)}"

# Example Tool: Read File
async def read_local_file(path: str):
    import os
    if not os.path.exists(path):
        return f"File {path} not found."
    with open(path, 'r') as f:
        return f.read(1000) # Limit to 1000 chars

# Initialize Registry
registry = ToolRegistry()
registry.register("read_file", read_local_file)
