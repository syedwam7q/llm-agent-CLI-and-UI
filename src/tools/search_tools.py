"""
Search and web-related tools.
"""
import aiohttp
import asyncio
from typing import List, Dict, Any, Optional
from bs4 import BeautifulSoup
import json

import sys
from pathlib import Path

# Ensure proper path setup
current_dir = Path(__file__).parent
src_dir = current_dir.parent
sys.path.insert(0, str(src_dir))
sys.path.insert(0, str(current_dir))

from base import BaseTool, ToolResult, ToolCategory, register_tool
from config import settings


@register_tool
class WebSearchTool(BaseTool):
    """Search the web using Tavily API for current information."""
    
    def __init__(self):
        super().__init__()
        self.category = ToolCategory.SEARCH
        self.description = "Search the web for current information using Tavily API"
    
    async def execute(self, query: str, max_results: int = 5) -> ToolResult:
        """Execute web search."""
        if not settings.tavily_api_key:
            return ToolResult(
                success=False,
                error="Tavily API key not configured"
            )
        
        try:
            async with aiohttp.ClientSession() as session:
                payload = {
                    "api_key": settings.tavily_api_key,
                    "query": query,
                    "search_depth": "basic",
                    "include_answer": True,
                    "include_images": False,
                    "include_raw_content": False,
                    "max_results": max_results
                }
                
                async with session.post(
                    "https://api.tavily.com/search",
                    json=payload,
                    headers={"Content-Type": "application/json"}
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        results = []
                        for result in data.get("results", []):
                            results.append({
                                "title": result.get("title", ""),
                                "url": result.get("url", ""),
                                "content": result.get("content", ""),
                                "score": result.get("score", 0)
                            })
                        
                        return ToolResult(
                            success=True,
                            data={
                                "query": query,
                                "answer": data.get("answer", ""),
                                "results": results,
                                "total_results": len(results)
                            },
                            metadata={"source": "tavily"}
                        )
                    else:
                        return ToolResult(
                            success=False,
                            error=f"Search API returned status {response.status}"
                        )
        
        except Exception as e:
            return ToolResult(
                success=False,
                error=f"Search failed: {str(e)}"
            )


@register_tool
class WebScrapeTool(BaseTool):
    """Scrape content from a web page."""
    
    def __init__(self):
        super().__init__()
        self.category = ToolCategory.WEB_SCRAPING
        self.description = "Scrape and extract text content from a web page"
    
    async def execute(self, url: str, extract_links: bool = False) -> ToolResult:
        """Execute web scraping."""
        try:
            async with aiohttp.ClientSession() as session:
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                }
                
                async with session.get(url, headers=headers, timeout=30) as response:
                    if response.status == 200:
                        html = await response.text()
                        soup = BeautifulSoup(html, 'html.parser')
                        
                        # Remove script and style elements
                        for script in soup(["script", "style"]):
                            script.decompose()
                        
                        # Extract text
                        text = soup.get_text()
                        lines = (line.strip() for line in text.splitlines())
                        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
                        text = ' '.join(chunk for chunk in chunks if chunk)
                        
                        result_data = {
                            "url": url,
                            "title": soup.title.string if soup.title else "",
                            "content": text[:5000],  # Limit content length
                            "content_length": len(text)
                        }
                        
                        if extract_links:
                            links = []
                            for link in soup.find_all('a', href=True):
                                links.append({
                                    "text": link.get_text().strip(),
                                    "url": link['href']
                                })
                            result_data["links"] = links[:20]  # Limit number of links
                        
                        return ToolResult(
                            success=True,
                            data=result_data,
                            metadata={"status_code": response.status}
                        )
                    else:
                        return ToolResult(
                            success=False,
                            error=f"HTTP {response.status}: Could not fetch the page"
                        )
        
        except Exception as e:
            return ToolResult(
                success=False,
                error=f"Web scraping failed: {str(e)}"
            )


@register_tool
class MockSearchTool(BaseTool):
    """Mock search tool for testing when no API keys are available."""
    
    def __init__(self):
        super().__init__()
        self.category = ToolCategory.SEARCH
        self.description = "Mock search tool that returns simulated results"
    
    async def execute(self, query: str, max_results: int = 5) -> ToolResult:
        """Execute mock search."""
        # Simulate some delay
        await asyncio.sleep(0.5)
        
        mock_results = [
            {
                "title": f"Result {i+1} for '{query}'",
                "url": f"https://example.com/result-{i+1}",
                "content": f"This is mock content for result {i+1} related to your query about {query}. "
                          f"It contains relevant information that would help answer your question.",
                "score": 0.9 - (i * 0.1)
            }
            for i in range(min(max_results, 3))
        ]
        
        return ToolResult(
            success=True,
            data={
                "query": query,
                "answer": f"Based on the search results for '{query}', here's what I found...",
                "results": mock_results,
                "total_results": len(mock_results)
            },
            metadata={"source": "mock", "note": "This is simulated data"}
        )