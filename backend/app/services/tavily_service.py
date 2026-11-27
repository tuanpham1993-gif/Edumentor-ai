"""
Tavily Web Search Service for EduMentor AI.
Provides scoped search and extraction capabilities strictly for enriching course syllabus,
curriculum, and module information of verified courses in the EduMentor database.
"""

import logging
from typing import Any

import httpx

from app.core.config import settings

logger = logging.getLogger("tavily_service")

TAVILY_SEARCH_URL = "https://api.tavily.com/search"
TAVILY_EXTRACT_URL = "https://api.tavily.com/extract"
REQUEST_TIMEOUT_SECONDS = 15.0


class TavilyService:
    """
    Client for Tavily Search and Extract API.
    Designed exclusively for course curriculum enrichment.
    """

    def __init__(self, api_key: str | None = None):
        if api_key is not None:
            self._api_key = api_key
        else:
            self._api_key = getattr(settings, "TAVILY_API_KEY", "")

    @property
    def is_configured(self) -> bool:
        return bool(self._api_key and str(self._api_key).strip())

    def search_course_curriculum(
        self,
        course_title: str,
        organization: str | None = None,
        max_results: int = 3,
    ) -> dict[str, Any]:
        """
        Searches web strictly for syllabus/curriculum/modules of a known EduMentor course.
        Query is constrained with quotes to target the specific course.
        """
        if not self.is_configured:
            logger.warning("Tavily API key is not configured. Web search cannot proceed.")
            return {
                "success": False,
                "error": "Tavily API key is not configured",
                "results": [],
            }

        title_clean = course_title.strip()
        org_clean = (organization or "").strip()

        if org_clean and org_clean.lower() != "n/a":
            query = f'"{title_clean}" "{org_clean}" syllabus curriculum modules lessons'
        else:
            query = f'"{title_clean}" syllabus curriculum modules lessons'

        payload = {
            "api_key": self._api_key,
            "query": query,
            "search_depth": "basic",
            "include_answer": False,
            "max_results": max(1, min(max_results, 5)),
        }

        try:
            with httpx.Client(timeout=REQUEST_TIMEOUT_SECONDS) as client:
                response = client.post(TAVILY_SEARCH_URL, json=payload)
                if response.status_code != 200:
                    logger.warning(
                        f"Tavily search returned HTTP {response.status_code}: {response.text[:200]}"
                    )
                    return {
                        "success": False,
                        "error": f"HTTP {response.status_code}",
                        "results": [],
                    }

                data = response.json()
                raw_results = data.get("results") or []
                filtered_results = []
                for item in raw_results[:max_results]:
                    filtered_results.append(
                        {
                            "title": item.get("title", ""),
                            "url": item.get("url", ""),
                            "content": (item.get("content") or "")[:1000],  # Limit length for token economy
                            "score": item.get("score", 0.0),
                        }
                    )

                return {
                    "success": True,
                    "query": query,
                    "results": filtered_results,
                }

        except httpx.TimeoutException:
            logger.warning(f"Tavily search timed out for query: '{title_clean}'")
            return {
                "success": False,
                "error": "Request timed out",
                "results": [],
            }
        except Exception as e:
            logger.warning(f"Tavily search encountered error: {e}")
            return {
                "success": False,
                "error": str(e),
                "results": [],
            }

    def extract_course_content(self, url: str) -> dict[str, Any]:
        """
        Extracts syllabus or curriculum details from a specific course page URL.
        """
        if not self.is_configured:
            return {
                "success": False,
                "error": "Tavily API key is not configured",
                "content": "",
            }

        payload = {
            "api_key": self._api_key,
            "urls": [url],
        }

        try:
            with httpx.Client(timeout=REQUEST_TIMEOUT_SECONDS) as client:
                response = client.post(TAVILY_EXTRACT_URL, json=payload)
                if response.status_code != 200:
                    return {
                        "success": False,
                        "error": f"HTTP {response.status_code}",
                        "content": "",
                    }

                data = response.json()
                results = data.get("results") or []
                if results and isinstance(results, list):
                    first_res = results[0]
                    content = first_res.get("raw_content") or first_res.get("content") or ""
                    return {
                        "success": True,
                        "url": url,
                        "content": content[:2500],  # Controlled length
                    }

                return {
                    "success": False,
                    "error": "No content extracted",
                    "content": "",
                }

        except Exception as e:
            logger.warning(f"Tavily extraction failed for URL {url}: {e}")
            return {
                "success": False,
                "error": str(e),
                "content": "",
            }


tavily_service = TavilyService()
