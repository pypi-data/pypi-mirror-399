"""
FastMCP Server Configuration and Entry Point.
"""

from mcp.server.fastmcp import FastMCP
from dotenv import load_dotenv
import os

# Import tools
# from sjaicom_google_patents.tools import register_tools
from sjaicom_google_patents.tools.patent_search import search_patents
from sjaicom_google_patents.tools.interaction import update_ui_state

# Load environment variables
load_dotenv()

# Initialize FastMCP server
mcp = FastMCP("Google Patents MCP Service")

# Register tools directly
mcp.add_tool(search_patents)
mcp.add_tool(update_ui_state)

# register_tools(mcp) # Deprecated: using direct registration

def main() -> None:
    """
    Main entry point for the MCP service
    """
    mcp.run()

if __name__ == "__main__":
    main()
