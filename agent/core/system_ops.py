import os

class SystemTools:
    """
    Provides local system capabilities to the Agent.
    """
    
    @staticmethod
    def write_file(filename: str, content: str) -> str:
        """Saves content to a file in the workspace."""
        try:
            # Security: Prevent traversing out of workspace (simple check)
            if ".." in filename or filename.startswith("/"):
                return "Error: Access denied. Relative paths only."
                
            with open(filename, "w", encoding="utf-8") as f:
                f.write(content)
            return f"Success: Written to {filename}"
        except Exception as e:
            return f"Error writing file: {e}"

    @staticmethod
    def read_file(filename: str) -> str:
        """Reads content from a file."""
        try:
            if not os.path.exists(filename):
                return "Error: File not found."
            with open(filename, "r", encoding="utf-8") as f:
                return f.read(2000) # Limit size
        except Exception as e:
            return f"Error reading file: {e}"
