from typing import TypedDict, List, Dict, Any, Optional
from .types import InteractiveElement

class AgentState(TypedDict):
    objective: str
    steps_taken: int
    max_steps: int
    history: List[Dict[str, Any]]
    screenshot: Optional[str] # Base64
    text_map: Optional[str] # OCR-like text
    elements: List[InteractiveElement]
    decision: Optional[Dict[str, Any]]
    last_raw_screenshot: Optional[bytes]
    status: str # "running", "done", "fail", "retry"
    error_count: int
