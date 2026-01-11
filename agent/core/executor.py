from playwright.async_api import Page
from typing import List, Dict, Any
from .types import InteractiveElement

class ActionEngine:
    def __init__(self, page: Page):
        self.page = page

    async def execute(self, decision: Dict[str, Any], elements: List[InteractiveElement]):
        """
        Executes the action decided by the VLM.
        """
        action = decision.get("action")
        el_id = decision.get("element_id")
        value = decision.get("value")
        reasoning = decision.get("reasoning")
        
        print(f"\n[Action] Decided to: {action.upper()} on ID {el_id}")
        print(f"         Reasoning: {reasoning}")

        if action in ["done", "fail", "human_request", "tool_use"]:
            return

        if action == "navigate":
            await self.page.goto(value)
            print(f"         Navigated to {value}")
            return
            
        if action == "wait":
            print("         Waiting for 2 seconds...")
            await self.page.wait_for_timeout(2000)
            return

        # For element-based actions, find the element
        target_el = next((e for e in elements if e.id == el_id), None)
        if not target_el:
            # Fallback: If action is press_key, maybe we don't need an element if it's global?
            if action == "press_key":
                await self.page.keyboard.press(value)
                print(f"         Pressed key '{value}' globally")
                return
            raise ValueError(f"Element ID {el_id} not found in current perception context.")

        x, y = target_el.bbox.center
        
        try:
            if action == "click":
                await self.page.mouse.click(x, y)
                print(f"         Clicked at ({x}, {y})")
                
            elif action == "type":
                await self.page.mouse.click(x, y)
                # Clear existing text if needed? For now just type.
                await self.page.keyboard.type(value)
                await self.page.keyboard.press("Enter")
                print(f"         Typed '{value}' and pressed Enter")
                
            elif action == "hover":
                await self.page.mouse.move(x, y)
                print(f"         Hovered at ({x}, {y})")
                
            elif action == "press_key":
                await self.page.mouse.click(x, y) # Focus first
                await self.page.keyboard.press(value)
                print(f"         Pressed key '{value}' on element")

            elif action == "scroll":
                await self.page.mouse.wheel(0, 500)
                print("         Scrolled down")
                
            # Wait for UI reaction
            await self.page.wait_for_timeout(1000)
            
        except Exception as e:
            print(f"         [Error] Action execution failed: {e}")
            raise e
