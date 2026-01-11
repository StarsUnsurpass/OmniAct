import base64
import json
import os
from typing import Optional, Dict, Any, List
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from .types import InteractiveElement

class VLMAgent:
    def __init__(self, provider: str = "mock", model_name: str = ""):
        self.provider = provider
        self.model_name = model_name
        self.history = []
        
        # Initialize models if API keys are present
        if provider == "openai" and os.getenv("OPENAI_API_KEY"):
            self.llm = ChatOpenAI(model=model_name or "gpt-4o", temperature=0)
        elif provider == "anthropic" and os.getenv("ANTHROPIC_API_KEY"):
            self.llm = ChatAnthropic(model=model_name or "claude-3-5-sonnet-20240620", temperature=0)
        else:
            self.llm = None # Mock mode

        async def reason(self, objective: str, screenshot_base64: str, elements: List[InteractiveElement], text_map: str = "") -> Dict[str, Any]:
            """
            Analyzes the screenshot and elements to decide the next action.
            """
            
            # 1. Prepare Element Context
            elements_desc = "\n".join(
                [f"ID {el.id}: <{el.tag_name}> {el.text_content} {el.attributes}" 
                 for el in elements]
            )
    
                    system_prompt = """You are an AI Agent. Complete the objective via JSON output.
                    
                    Actions:
                    - Browser: "click", "type", "scroll", "hover", "navigate", "wait", "press_key"
                    - System: "tool_use" (value format: "tool_name|arg1|arg2...")
                    - Flow: "done", "fail"
                    
                    Tools Available:
                    - "write_file|filename|content"
                    - "read_file|filename"
                    
                    Output format:
                    {
                        "reasoning": "...",
                        "action": "click" | "type" | ... | "tool_use",
                        "element_id": <int> (optional for navigate/tool_use), 
                        "value": "..." (text to type, URL, key to press, or tool arguments)
                    }
                    """
                        user_text = f"Objective: {objective}\n\nVisible Interactive Elements:\n{elements_desc}"
            if text_map:
                user_text += f"\n\nPage Text Content (OCR-like):\n{text_map}"
    
            user_content = [
                {"type": "text", "text": user_text},
                {
                    "type": "image_url",
                    "image_url": {"url": f"data:image/png;base64,{screenshot_base64}"}
                }
            ]
            if self.llm:
            try:
                message = HumanMessage(content=user_content)
                response = await self.llm.ainvoke([SystemMessage(content=system_prompt), message])
                
                # Naive JSON parsing (Robust agents use structured output parsers)
                content = response.content
                # Strip markdown code blocks if present
                if "```json" in content:
                    content = content.split("```json")[1].split("```")[0]
                elif "```" in content:
                    content = content.split("```")[1].split("```")[0]
                    
                return json.loads(content.strip())
            except Exception as e:
                print(f"Error calling VLM: {e}")
                return {
                    "action": "fail",
                    "reasoning": f"VLM Error: {str(e)}",
                    "element_id": None
                }
        else:
            # --- MOCK LOGIC for Demo without API Keys ---
            print("\n[VLM] Mock Mode: Simulating decision...")
            
            # Simple heuristic for demo: 
            # If input is found and empty, type. If button found, click.
            
            # Search for an input field
            input_el = next((e for e in elements if e.tag_name == "input"), None)
            if input_el:
                 return {
                    "reasoning": "Found an input field, I should type the search query.",
                    "action": "type",
                    "element_id": input_el.id,
                    "value": "Rust Programming"
                }
            
            # Else search for a button or link?
            return {
                "reasoning": "No obvious input found, ending task.",
                "action": "done",
                "element_id": None
            }
