Google Patents MCP Service
A Model Context Protocol (MCP) server that provides patent search capabilities using Google Patents (via SerpApi).

Designed for AI Agents to perform professional patent analysis, landscape verification, and prior art search.

Features
Patent Search: Search patents by keywords, country, date, status, assignee, etc.
Smart Interaction: Includes UI state management tools for "Human-in-the-loop" confirmation flows.
Structured Data: Returns clean, normalized JSON data optimized for LLM consumption.
Installation
Using uvx (Recommended)
uvx sjaicom-google-patents
Using pip
pip install sjaicom-google-patents
python -m sjaicom_google_patents
Configuration
This service requires the following environment variables:

SERPAPI_KEY: Your SerpApi API key (Get one at https://serpapi.com/)
Tools
search_patents: Main tool for searching patents.
Inputs: keywords, country_codes, status (GRANT/APPLICATION), date_range, etc.
update_ui_state: Tool for managing conversational UI state (for frontend integration).
License
MIT