import base64
import json
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from .state import AgentState
from .perception import capture_interactive_elements, annotate_screenshot, get_page_text_map
from .llm import VLMAgent
from .executor import ActionEngine
from .system_ops import SystemTools
from .types import InteractiveElement
import config

try:
    import vision_core
    RUST_AVAILABLE = True
except ImportError:
    RUST_AVAILABLE = False

def create_agent_graph(agent_brain: VLMAgent, executor: ActionEngine, page):
    
    async def perceive_node(state: AgentState):
        print(f"\n[Node: Perceive] Step {state['steps_taken'] + 1}")
        elements = await capture_interactive_elements(page)
        text_map = await get_page_text_map(page)
        annotated_img_bytes = await annotate_screenshot(page, elements)
        
        # Save debug view
        with open(f"step_{state['steps_taken']}_view.png", "wb") as f:
            f.write(annotated_img_bytes)
            
        return {
            "elements": elements,
            "text_map": text_map,
            "screenshot": base64.b64encode(annotated_img_bytes).decode('utf-8'),
            "last_raw_screenshot": await page.screenshot() if RUST_AVAILABLE else None
        }

    async def reason_node(state: AgentState):
        print("[Node: Reason]")
        decision = await agent_brain.reason(
            state["objective"], 
            state["screenshot"], 
            state["elements"],
            text_map=state.get("text_map", "")
        )
        return {"decision": decision}

    async def act_node(state: AgentState):
        print("[Node: Act]")
        decision = state["decision"]
        action = decision["action"]
        
        if action in ["done", "fail"]:
            return {"status": action}
        
        if action == "human_request":
            return {"status": "wait_for_human"}

        if action == "tool_use":
            # format: tool_name|arg1...
            parts = decision.get("value", "").split("|", 1)
            tool_name = parts[0]
            args = parts[1] if len(parts) > 1 else ""
            
            print(f"   [Tool] Invoking {tool_name}...")
            result = "Unknown Tool"
            
            if tool_name == "write_file":
                # split args into filename|content
                f_parts = args.split("|", 1)
                if len(f_parts) == 2:
                    result = SystemTools.write_file(f_parts[0], f_parts[1])
                else:
                    result = "Error: write_file requires 'filename|content'"
            
            elif tool_name == "read_file":
                result = SystemTools.read_file(args)
                
            print(f"   [Tool Result] {result}")
            # Tool use doesn't need visual verification usually, but we keep the loop
            return {"steps_taken": state["steps_taken"] + 1, "status": "running"}
            
        await executor.execute(decision, state["elements"])
        return {"steps_taken": state["steps_taken"] + 1, "status": "running"}

    async def verify_node(state: AgentState):
        print("[Node: Verify]")
        if not RUST_AVAILABLE or not state.get("last_raw_screenshot"):
            return {"status": "running"}
            
        await page.wait_for_timeout(1000)
        current_screenshot = await page.screenshot()
        
        diff = vision_core.calculate_pixel_diff(state["last_raw_screenshot"], current_screenshot)
        print(f"   [Verification] Screen Change Ratio: {diff:.4f}")
        
        if diff < config.SELF_HEALING_THRESHOLD:
            print("   [!] Self-Healing Triggered: Action had no effect.")
            if state["error_count"] >= 2:
                print("   [!] Multiple failures. Requesting Human Intervention...")
                return {"status": "wait_for_human"}
            return {"status": "retry", "error_count": state["error_count"] + 1}
            
        return {"status": "running", "error_count": 0}

    async def human_node(state: AgentState):
        """
        Pauses execution and waits for user input.
        """
        print("\n" + "="*40)
        print("HUMAN INTERVENTION REQUIRED")
        print(f"Current Objective: {state['objective']}")
        print(f"Status: {state['status']}")
        print(f"Reasoning: {state['decision'].get('reasoning') if state['decision'] else 'N/A'}")
        print("="*40)
        print("Review 'step_X_view.png' to see the agent's view.")
        
        user_input = input("\nEnter 'c' to continue, 'r' to retry, or a new instruction: ")
        
        if user_input.lower() == 'c':
            return {"status": "running", "error_count": 0}
        elif user_input.lower() == 'r':
            return {"status": "retry", "error_count": 0}
        else:
            # Update objective based on human feedback
            print(f"Updating objective to: {user_input}")
            return {"objective": user_input, "status": "running", "error_count": 0}

    # Define Graph
    workflow = StateGraph(AgentState)

    workflow.add_node("perceive", perceive_node)
    workflow.add_node("reason", reason_node)
    workflow.add_node("act", act_node)
    workflow.add_node("verify", verify_node)
    workflow.add_node("human", human_node)

    workflow.set_entry_point("perceive")
    workflow.add_edge("perceive", "reason")
    workflow.add_edge("reason", "act")
    workflow.add_edge("act", "verify")

    def should_continue(state: AgentState):
        if state["status"] == "done": return END
        if state["status"] == "fail": return END
        if state["status"] == "wait_for_human": return "human"
        if state["steps_taken"] >= state["max_steps"]: return END
        return "perceive"

    workflow.add_conditional_edges("verify", should_continue)
    workflow.add_edge("human", "perceive")

    # Initialize Memory for Checkpointing
    memory = MemorySaver()

    return workflow.compile(checkpointer=memory)

