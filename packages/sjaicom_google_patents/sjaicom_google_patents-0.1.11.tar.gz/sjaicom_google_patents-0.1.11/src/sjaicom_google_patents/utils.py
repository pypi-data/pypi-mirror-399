import sys
import json
from typing import Any

def log_stderr(msg: str, data: Any = None):
    """
    Helper for structured logging to stderr (so it doesn't break stdout JSON).
    
    Args:
        msg: The log message.
        data: Optional data object to pretty-print (dict, list, or Pydantic model).
    """
    log_entry = f"[MCP-LOG] {msg}"
    if data is not None:
        try:
            # Try to pretty print JSON if possible
            if hasattr(data, "model_dump_json"):
                log_entry += f"\n{data.model_dump_json(indent=2)}"
            elif isinstance(data, (dict, list)):
                log_entry += f"\n{json.dumps(data, indent=2, ensure_ascii=False)}"
            else:
                log_entry += f": {str(data)}"
        except Exception:
            log_entry += f": {str(data)}"
    
    print(log_entry, file=sys.stderr)
