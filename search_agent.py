"""
Deep Research v2 - Legal Search Agent
Executes concurrent API calls to specific jurisdictions and strictly filters output to reduce LLM latency.
"""

import os
import json
import asyncio
import aiohttp
from typing import List, Dict, Any

# ==========================================
# Load API Keys from Environment
# ==========================================
COURTLISTENER_API_KEY = os.getenv("COURTLISTENER_API_KEY", "")
# Note: EUR-Lex uses basic auth (username/password) which we will implement later.
# HUDOC is public but requires a proper User-Agent to avoid rate limits.

HEADERS = {
    "User-Agent": "LegalTechAgent/1.0 (MVP Testing; admin@example.com)"
}

# ==========================================
# Jurisdiction-Specific Fetch Functions
# ==========================================

async def fetch_us_courtlistener(session: aiohttp.ClientSession, query: str) -> List[Dict[str, Any]]:
    """
    Fetches case law from US CourtListener API and prunes the massive JSON.
    """
    print(f"🇺🇸 [Search Agent] Querying CourtListener for: '{query}'")
    
    # Official CourtListener Search API Endpoint
    url = f"https://www.courtlistener.com/api/rest/v3/search/?q={query}"
    auth_headers = HEADERS.copy()
    if COURTLISTENER_API_KEY:
        auth_headers["Authorization"] = f"Token {COURTLISTENER_API_KEY}"

    try:
        async with session.get(url, headers=auth_headers, timeout=10) as response:
            if response.status != 200:
                return [{"error": f"CourtListener API returned status {response.status}"}]
            
            data = await response.json()
            results = data.get("results", [])
            
            # --- INTENT FILTERING (Crucial for lowering latency & token cost) ---
            # We only keep the top 3 cases and extract ONLY the absolute necessary fields.
            pruned_cases = []
            for case in results[:3]:
                pruned_cases.append({
                    "case_name": case.get("caseName", "Unknown Case"),
                    "date_filed": case.get("dateFiled", "Unknown Date"),
                    "court": case.get("court", "Unknown Court"),
                    # We extract 'snippet' which usually contains the exact keyword context
                    "summary_snippet": case.get("snippet", "").replace("<em>", "").replace("</em>", ""),
                    "url": f"https://www.courtlistener.com{case.get('absolute_url', '')}"
                })
            return pruned_cases

    except Exception as e:
        return [{"error": f"CourtListener connection failed: {str(e)}"}]


async def fetch_eu_lex(session: aiohttp.ClientSession, query: str) -> List[Dict[str, Any]]:
    """
    Placeholder for EUR-Lex API. 
    (Will implement SOAP/REST parsing once credentials are approved).
    """
    print(f"🇪🇺 [Search Agent] Querying EUR-Lex for: '{query}'")
    await asyncio.sleep(1) # Simulate network delay
    return [{"status": "Pending EUR-Lex API credentials", "mock_data": "GDPR Art. 9 prohibition."}]


async def fetch_eu_hudoc(session: aiohttp.ClientSession, query: str) -> List[Dict[str, Any]]:
    """
    Fetches human rights cases from HUDOC Open Data API.
    """
    print(f"⚖️ [Search Agent] Querying HUDOC for: '{query}'")
    
    # HUDOC OData endpoint (requires careful URL encoding)
    url = f"https://hudoc.echr.coe.int/app/query/results?query=contents:{query}&select=sharepointid,itemid,docname,importance,conclusion&sort=kpdate Descending&length=3"
    
    try:
        async with session.get(url, headers=HEADERS, timeout=10) as response:
            if response.status != 200:
                return [{"error": f"HUDOC API returned status {response.status}"}]
                
            data = await response.json()
            results = data.get("results", [])
            
            # --- INTENT FILTERING ---
            pruned_cases = []
            for case in results:
                pruned_cases.append({
                    "case_name": case.get("columns", {}).get("docname", "Unknown"),
                    "importance": case.get("columns", {}).get("importance", "N/A"),
                    "conclusion": case.get("columns", {}).get("conclusion", "No conclusion snippet available"),
                })
            return pruned_cases
            
    except Exception as e:
         return [{"error": f"HUDOC connection failed: {str(e)}"}]

# ==========================================
# Main Execution Tool (Called by LLM)
# ==========================================

async def execute_legal_searches(search_tasks: List[Dict[str, Any]]) -> str:
    """
    Takes the structured tasks from Planner Agent, executes them in parallel, 
    and returns a highly compressed JSON string for the Fact Checker.
    """
    print("\n" + "="*50)
    print("🚀 [Search Agent] Initiating Parallel Multi-Jurisdiction Search...")
    print("="*50)

    # We use a single ClientSession for optimal connection pooling
    async with aiohttp.ClientSession() as session:
        tasks = []
        
        # Route tasks to the correct API function based on Planner's logic
        for task in search_tasks:
            target = task.get("api_target")
            query = task.get("search_query", "")
            
            if target == "US_COURT":
                tasks.append(fetch_us_courtlistener(session, query))
            elif target == "EU_LEX":
                tasks.append(fetch_eu_lex(session, query))
            elif target == "EU_HUDOC":
                tasks.append(fetch_eu_hudoc(session, query))
            else:
                # Fallback for GENERAL_WEB (Can wire up Tavily or Google Search API here later)
                print(f"🌐 [Search Agent] Skipping GENERAL_WEB for now: '{query}'")
                tasks.append(asyncio.sleep(0.1))

        # Execute all API calls concurrently
        raw_results = await asyncio.gather(*tasks, return_exceptions=True)

    # Compile the final evidence payload
    compiled_evidence = []
    for i, task in enumerate(search_tasks):
        result = raw_results[i]
        # Handle potential asyncio exceptions
        if isinstance(result, Exception):
            result = [{"error": str(result)}]
            
        compiled_evidence.append({
            "task_id": task.get("task_id"),
            "target": task.get("api_target"),
            "query": task.get("search_query"),
            "evidence": result
        })

    # Return as a JSON string so it can be passed into the next Agent's context
    return json.dumps(compiled_evidence, ensure_ascii=False)