import os

# Agent Configuration

# VLM Provider: "mock", "openai", "anthropic"
VLM_PROVIDER = os.getenv("VLM_PROVIDER", "mock")

# API Keys (Load from env or set here)
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")

# VLM Models
OPENAI_MODEL = "gpt-4o"
ANTHROPIC_MODEL = "claude-3-5-sonnet-20240620"

# Execution Settings
HEADLESS = False  # Set to True for server environments
VIEWPORT = {"width": 1280, "height": 800}
MAX_STEPS = 10
SELF_HEALING_THRESHOLD = 0.01 # 1% pixel change required to consider action successful
