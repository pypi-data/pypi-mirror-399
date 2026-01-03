"""
Patent search implementation (Real API + Mock Fallback).
Designed to be called by the Dispatcher.
"""

import os
import requests
import sys
import json
import re
from typing import List, Dict, Any, Optional, Tuple
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from sjaicom_google_patents.utils import log_stderr as _log
from sjaicom_google_patents.models.retrieval import (
    PatentData, Region, SearchSummary, StatItem, FrequencyItem, PatentImage,
    PatentSearchResponse
)

# --- Mock Data (Fallback) ---
# IMPORTANT: This path is for LOCAL TESTING ONLY.
# In production (e.g., Aliyun Bailian FC), this logic is disabled by default.
# Use env var MCP_LOCAL_MOCK_FILE_PATH to override if needed in dev.
LOCAL_TEST_FILE = os.getenv("MCP_LOCAL_MOCK_FILE_PATH")

# --- Memory Mock Data (Fallback for Demo/No-Key) ---
# Pure memory-resident data. Safe for FC environment.
MEMORY_MOCK_DB = [
    {
        "id": "DEMO-CN112233445B",
        "title": "[Demo] 5G Massive MIMO Antenna Design",
        "snippet": "This is a memory-resident mock patent for demonstration purposes when no API key is provided.",
        "assignee": "Demo Corp",
        "publication_date": "2024-01-01",
        "region": "CN",
        "status": "GRANT",
        "kind_code": "B",
        "legal_status": "Active"
    },
    {
        "id": "DEMO-US20240012345A1",
        "title": "[Demo] AI-Driven Patent Landscape Analysis",
        "snippet": "System and method for analyzing patent landscapes using AI agents.",
        "assignee": "Future Tech Inc",
        "publication_date": "2024-02-15",
        "region": "US",
        "status": "APPLICATION",
        "kind_code": "A1",
        "legal_status": "Pending"
    }
]

def _mock_search_memory(keywords: str, country_codes: str, limit: int) -> PatentSearchResponse:
    """
    Pure memory-based mock search. Safe for FC (no file I/O).
    Used when no API Key and no File Mock are available.
    """
    _log(f"Using MEMORY MOCK. Keywords={keywords}")
    results = []
    for doc in MEMORY_MOCK_DB:
        results.append(PatentData(
            id=doc["id"],
            title=doc["title"],
            snippet=doc["snippet"],
            assignee=doc["assignee"],
            publication_date=doc["publication_date"],
            region=doc["region"],
            status=doc["status"],
            kind_code=doc["kind_code"],
            legal_status=doc["legal_status"],
            score=0.99
        ))
    
    return PatentSearchResponse(
        total_results=len(results),
        results=results,
        summary=None,
        debug_info={"source": "memory_mock", "note": "Demo data only. Set SERPAPI_KEY for real results."}
    )

def _mock_search(keywords: str, country_codes: str, limit: int, status: Optional[str] = None, type: Optional[str] = None, assignee: Optional[str] = None) -> PatentSearchResponse:
    """
    Fallback mock search logic using local file.
    Only active if MCP_USE_LOCAL_FILE_MOCK is true and file exists.
    """
    _log(f"Using MOCK DB (File Mode). Keywords={keywords}, Countries={country_codes}, Status={status}, Type={type}, Assignee={assignee}")
    
    debug_info = {
        "source": "mock_db_file",
        "file_path": LOCAL_TEST_FILE,
        "query_params": {
            "keywords": keywords,
            "country_codes": country_codes,
            "limit": limit,
            "status": status,
            "type": type,
            "assignee": assignee
        }
    }
    
    # Check if local file mock is enabled and file exists
    use_local_file_mock = os.getenv("MCP_USE_LOCAL_FILE_MOCK", "false").lower() == "true"
    
    if use_local_file_mock and LOCAL_TEST_FILE and os.path.exists(LOCAL_TEST_FILE):
        try:
            _log(f"Loading local test file: {LOCAL_TEST_FILE}")
            with open(LOCAL_TEST_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                patents, summary = _parse_serpapi_response(data)
                
                # Check if debug info is enabled
                if os.getenv("MCP_ENABLE_DEBUG_INFO", "false").lower() != "true":
                    debug_info = None
                    
                return PatentSearchResponse(
                    total_results=data.get("search_information", {}).get("total_results", len(patents)),
                    results=patents,
                    summary=summary,
                    debug_info=debug_info
                )
        except Exception as e:
            _log(f"Failed to load local test file: {e}")
            raise RuntimeError(f"Mock file loading failed: {e}")
    else:
        # Should not happen if logic is correct, but safe guard
        raise RuntimeError("Mock mode requested but not properly configured (MCP_USE_LOCAL_FILE_MOCK=true and valid MCP_LOCAL_MOCK_FILE_PATH required).")

def _fetch_from_serpapi(keywords: str, country_codes: str, limit: int, date_range: Optional[str], api_key: str, skip_cache: bool = False, status: Optional[str] = None, type: Optional[str] = None, assignee: Optional[str] = None) -> Tuple[Dict[str, Any], Dict[str, Any]]:
    """
    Execute HTTP request to SerpApi.
    Returns: (JSON Data, Request Debug Info)
    """
    base_url = os.getenv("SERPAPI_BASE_URL", "https://serpapi.com/search.json")
    
    # 1. Handle Assignee (Append to keywords if present, as SerpApi/Google Patents uses q=assignee:NAME)
    final_keywords = keywords
    if assignee:
        final_keywords = f"{final_keywords} assignee:{assignee}"

    # 2. Map Parameters
    query_params = {
        "engine": "google_patents",
        "api_key": api_key,
        "q": final_keywords,
        "num": limit,
        "output": "json",
        "country": country_codes,
        "no_cache": str(skip_cache).lower()
    }

    # 3. Optional Filters
    if status:
        query_params["status"] = status
    if type:
        query_params["type"] = type
    
    # Handle Date Range
    # Expected format: "priority:20220101" (implies after) or "before:priority:20230101"
    if date_range:
        if "before:" in date_range:
            query_params["before"] = date_range.replace("before:", "")
        elif "after:" in date_range:
            query_params["after"] = date_range.replace("after:", "")
        else:
            # Default to 'after' if not specified, or pass as is if SerpApi supports implicit
            # But SerpApi usually needs 'before' or 'after' param keys.
            # Let's assume user passes "after:priority:20220101" or just "priority:20220101" (which goes to 'after' by default?)
            # Actually, looking at docs: "before" and "after" are separate params.
            # We need to parse.
            # Simple heuristic: if user string looks like a date param, put it in 'after' by default if ambiguous, 
            # or try to split.
            # Ideally, the Agent should send `before` and `after` separately. 
            # But for now, let's put it in `after` if it doesn't have a prefix, or handle simple parsing.
            query_params["after"] = date_range
    
    # Mask API Key for logging/debug
    debug_params = query_params.copy()
    if "api_key" in debug_params:
        debug_params["api_key"] = "******"
        
    debug_info = {
        "url": base_url,
        "method": "GET",
        "params": debug_params
    }
    
    _log(f"Requesting SerpApi: {json.dumps(debug_params, default=str)}")
    
    # Check if debug info is enabled
    if os.getenv("MCP_ENABLE_DEBUG_INFO", "false").lower() != "true":
        debug_info = None

    try:
        response = requests.get(base_url, params=query_params, timeout=30)
        response.raise_for_status()
        return response.json(), debug_info
    except requests.exceptions.RequestException as e:
        _log(f"SerpApi Request Failed: {e}")
        raise e

def _parse_serpapi_response(data: Dict[str, Any]) -> Tuple[List[PatentData], Optional[SearchSummary]]:
    """
    Convert SerpApi JSON to internal Pydantic models.
    """
    # 1. Parse Results
    organic_results = data.get("organic_results", [])
    patent_data_list = []
    
    for item in organic_results:
        # Extract figures
        figures = []
        if "figures" in item:
            for fig in item["figures"]:
                figures.append(PatentImage(
                    thumbnail=fig.get("thumbnail", ""),
                    full=fig.get("full", "")
                ))
        
        # Extract country status
        country_status = item.get("country_status", {})
        
        # Determine main region (heuristic: use the country code from publication_number)
        pub_num = item.get("publication_number", "")
        region = pub_num[:2] if len(pub_num) >= 2 else "Unknown"

        kind_code = item.get("kind", "")
        if not kind_code and pub_num:
            # Try to extract from "US20240123A1" -> "A1"
            match = re.search(r'([A-Z]\d?)$', pub_num)
            if match:
                kind_code = match.group(1)

        patent = PatentData(
            kind_code=kind_code,
            id=item.get("patent_id") or item.get("publication_number", "Unknown"),
            title=item.get("title", "No Title"),
            snippet=item.get("snippet", ""),
            assignee=item.get("assignee"),
            inventor=item.get("inventor"),
            priority_date=item.get("priority_date"),
            filing_date=item.get("filing_date"),
            publication_date=item.get("publication_date"),
            publication_number=pub_num,
            language=item.get("language"),
            patent_link=item.get("patent_link"),
            serpapi_link=item.get("serpapi_link"),
            pdf_link=item.get("pdf"), # Some results might have direct PDF links
            thumbnail=item.get("thumbnail"),
            figures=figures,
            region=region,
            status=item.get("status"), # e.g. "GRANT"
            legal_status=item.get("status"), # Map status to legal_status for now
            country_status=country_status,
            score=0.0, # SerpApi doesn't return explicit score, default to 0
            extension=item # Store raw item in extension for debug/extra fields
        )
        patent_data_list.append(patent)
        
    # 2. Parse Summary
    summary_data = data.get("summary", {})
    search_summary = None
    
    if summary_data:
        # Helper to parse stat items
        def parse_stats(key: str) -> List[StatItem]:
            items = []
            raw_list = summary_data.get(key, [])
            for raw_item in raw_list:
                # Handle 'frequency' list
                freq_list = []
                for f in raw_item.get("frequency", []):
                    freq_list.append(FrequencyItem(
                        year_range=f.get("year_range", ""),
                        percentage=float(f.get("percentage", 0))
                    ))
                
                items.append(StatItem(
                    key=raw_item.get("key", "Unknown"),
                    percentage=float(raw_item.get("percentage", 0)),
                    frequency=freq_list
                ))
            return items

        search_summary = SearchSummary(
            assignees=parse_stats("assignee"),
            inventors=parse_stats("inventor"),
            cpcs=parse_stats("cpc")
        )
        
    return patent_data_list, search_summary

def search_patents(keywords: str, country_codes: str = "CN,US,WO", limit: int = 10, date_range: Optional[str] = None, status: Optional[str] = None, type: Optional[str] = None, assignee: Optional[str] = None, skip_cache: bool = False) -> PatentSearchResponse:
    """
    Execute a patent search using Google Patents API (SerpApi).
    
    Args:
        keywords: Search query, e.g. '(VR) OR (Virtual Reality)'.
        country_codes: Comma-separated country codes, e.g. 'CN,US,WO'.
        limit: Number of results (10-100).
        date_range: Date filter, e.g. 'priority:20220101' (after) or 'before:priority:20230101'.
        status: Filter by status: 'GRANT' (Granted) or 'APPLICATION' (Application).
        type: Filter by type: 'PATENT' (Invention) or 'DESIGN' (Design).
        assignee: Filter by assignee (company/person).
        skip_cache: If true, bypass SerpApi cache.
    """
    # 1. Limit Clamping
    limit = min(max(limit, 10), 100)
    
    # 2. Check Mock Mode Configuration First
    # If explicit Mock Mode is enabled, force use of local file mock.
    use_local_file_mock = os.getenv("MCP_USE_LOCAL_FILE_MOCK", "false").lower() == "true"
    
    if use_local_file_mock:
        # Check if Mock File is configured
        mock_file = os.getenv("MCP_LOCAL_MOCK_FILE_PATH")
        if not mock_file:
            error_msg = "MCP_USE_LOCAL_FILE_MOCK is true, but MCP_LOCAL_MOCK_FILE_PATH is not set."
            _log(f"ERROR: {error_msg}")
            raise ValueError(error_msg)
            
        if not os.path.exists(mock_file):
            error_msg = f"MCP_LOCAL_MOCK_FILE_PATH points to non-existent file: {mock_file}"
            _log(f"ERROR: {error_msg}")
            raise FileNotFoundError(error_msg)
            
        _log("MOCK MODE ENABLED: Using local file for search.")
        return _mock_search(keywords, country_codes, limit, status, type, assignee)

    # 3. Check API Key for Real Search
    api_key = os.getenv("SERPAPI_KEY")
    
    # Validation: Key must be present and valid for Real Search
    if not api_key or "your_serpapi_key_here" in api_key:
        # Fallback to Memory Mock if no key provided.
        # This ensures service liveness in FC environment without crashing, 
        # while strictly avoiding local file dependencies.
        _log("WARNING: No valid SERPAPI_KEY found. Falling back to MEMORY MOCK.")
        return _mock_search_memory(keywords, country_codes, limit)
        
    # 4. Execute Real Search
    try:
        raw_data, debug_info = _fetch_from_serpapi(keywords, country_codes, limit, date_range, api_key, skip_cache, status, type, assignee)
        patents, summary = _parse_serpapi_response(raw_data)
        
        # Merge debug info
        if debug_info:
            if not isinstance(debug_info, dict):
                 debug_info = {}
            # We don't overwrite debug_info from fetch, just pass it through or augment it if needed
            pass

        return PatentSearchResponse(
            total_results=raw_data.get("search_information", {}).get("total_results", len(patents)),
            results=patents,
            summary=summary,
            debug_info=debug_info
        )
    except Exception as e:
        _log(f"Search failed: {e}")
        # If Real Search fails (e.g. Quota exhausted, Network error), 
        # we might want to fallback to Memory Mock if enabled, or just raise.
        # For now, let's raise to be strict, or return empty with error info.
        # User prefers strictness for "Must Search" cases.
        raise e
