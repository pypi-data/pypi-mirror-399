"""
Interaction tools for UI state management.
Designed to decouple state transmission from natural language response.
"""

from typing import Dict, Any, List, Optional
import json

def update_ui_state(session_id: str, stage: str, payload: Dict[str, Any], actions: List[str] = []) -> str:
    """
    Updates the frontend UI state via a structured channel (Tool Call).
    
    CRITICAL: 
    - ALWAYS call this tool when you need to update the UI or track state.
    - Do NOT output raw JSON in your text response.
    - This tool acts as the "Side Channel" for machine-readable state.

    Args:
        session_id: Unique identifier for the current session.
        stage: Current workflow stage (e.g., 'intent_parse', 'feature_confirmation', 'searching', 'analysis', 'done').
        payload: The structured data required for the frontend to render the UI (e.g., form fields, search results).
        actions: List of valid actions the user can take next (e.g., ['confirm', 'edit'], ['refine']).

    Returns:
        str: A system acknowledgement (hidden from user usually) confirming state update.
    """
    # In a real production environment (e.g., with a WebSocket or DB), 
    # this function would emit the state change event.
    # For MCP, simply being called allows the Host/Client to capture the arguments.
    
    state_summary = {
        "session_id": session_id,
        "stage": stage,
        "actions": actions,
        "payload_keys": list(payload.keys())
    }
    
    # We return a brief confirmation. The Client captures the *arguments* of this call to update the UI.
    return f"State updated to '{stage}'. Client should render payload."
