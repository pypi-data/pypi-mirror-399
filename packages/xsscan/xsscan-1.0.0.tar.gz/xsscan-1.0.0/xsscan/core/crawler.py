"""
Web Crawler - Discovers URLs and injection points.

Pure crawling logic with no XSS detection.
"""

import re
import time
import asyncio
from typing import List, Set, Dict, Optional
from urllib.parse import urljoin, urlparse, parse_qs, urlencode, urlunparse
from collections import deque
import httpx
from bs4 import BeautifulSoup
from xsscan.core.models import ScanContext, InjectionPoint, InjectionContext


class WebCrawler:
    """Crawls web applications to discover URLs and injection points."""
    
    def __init__(self, context: ScanContext):
        """
        Initialize the crawler.
        
        Args:
            context: Scan configuration context
        """
        self.context = context
        self.visited_urls: Set[str] = set()
        self.injection_points: Set[InjectionPoint] = set()
        self.client: Optional[httpx.AsyncClient] = None
        self._last_request_time = 0.0
    
    async def __aenter__(self):
        """Async context manager entry."""
        self.client = httpx.AsyncClient(
            timeout=self.context.timeout,
            follow_redirects=self.context.follow_redirects,
            verify=self.context.verify_ssl,
            headers={
                "User-Agent": self.context.user_agent,
                **self.context.headers,
            },
            cookies=self.context.cookies,
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self.client:
            await self.client.aclose()
    
    def _should_exclude(self, url: str) -> bool:
        """Check if URL should be excluded from crawling."""
        parsed = urlparse(url)
        path = parsed.path.lower()
        
        for excluded in self.context.excluded_paths:
            if excluded.lower() in path:
                return True
        
        # Exclude common non-HTML resources
        excluded_extensions = [
            ".jpg", ".jpeg", ".png", ".gif", ".svg", ".ico",
            ".css", ".js", ".woff", ".woff2", ".ttf", ".eot",
            ".pdf", ".zip", ".tar", ".gz", ".mp4", ".mp3",
            ".avi", ".mov", ".wmv", ".flv",
        ]
        
        for ext in excluded_extensions:
            if path.endswith(ext):
                return True
        
        return False
    
    async def _rate_limit(self):
        """Apply rate limiting."""
        if self.context.rate_limit > 0:
            min_interval = 1.0 / self.context.rate_limit
            elapsed = time.time() - self._last_request_time
            if elapsed < min_interval:
                await asyncio.sleep(min_interval - elapsed)
            self._last_request_time = time.time()
    
    async def fetch_url(self, url: str) -> Optional[httpx.Response]:
        """
        Fetch a URL with rate limiting.
        
        Args:
            url: URL to fetch
        
        Returns:
            HTTP response or None if failed
        """
        if self._should_exclude(url):
            return None
        
        await self._rate_limit()
        
        try:
            response = await self.client.get(url)
            return response
        except (httpx.RequestError, httpx.HTTPStatusError) as e:
            return None
    
    def extract_links(self, html: str, base_url: str) -> Set[str]:
        """
        Extract links from HTML content.
        
        Args:
            html: HTML content
            base_url: Base URL for resolving relative links
        
        Returns:
            Set of absolute URLs
        """
        links = set()
        
        try:
            soup = BeautifulSoup(html, "lxml")
            
            # Extract <a> href attributes
            for tag in soup.find_all("a", href=True):
                href = tag["href"]
                absolute_url = urljoin(base_url, href)
                parsed = urlparse(absolute_url)
                if parsed.scheme in ("http", "https"):
                    links.add(absolute_url)
            
            # Extract <form> action attributes
            for tag in soup.find_all("form", action=True):
                action = tag["action"]
                absolute_url = urljoin(base_url, action)
                parsed = urlparse(absolute_url)
                if parsed.scheme in ("http", "https"):
                    links.add(absolute_url)
            
            # Extract <link> href attributes
            for tag in soup.find_all("link", href=True):
                href = tag["href"]
                absolute_url = urljoin(base_url, href)
                parsed = urlparse(absolute_url)
                if parsed.scheme in ("http", "https"):
                    links.add(absolute_url)
        
        except Exception:
            pass
        
        return links
    
    def extract_injection_points(
        self, url: str, html: str, response: httpx.Response
    ) -> List[InjectionPoint]:
        """
        Extract potential injection points from a URL and its response.
        
        Args:
            url: The URL
            html: HTML content
            response: HTTP response
        
        Returns:
            List of injection points
        """
        injection_points = []
        parsed = urlparse(url)
        
        # Extract GET parameters
        query_params = parse_qs(parsed.query, keep_blank_values=True)
        for param_name, param_values in query_params.items():
            if param_name.lower() in [p.lower() for p in self.context.excluded_params]:
                continue
            
            # Determine context from HTML
            context = self._detect_context(html, param_name, param_values[0] if param_values else "")
            
            injection_point = InjectionPoint(
                url=url,
                method="GET",
                parameter=param_name,
                context=context,
                value=param_values[0] if param_values else None,
            )
            injection_points.append(injection_point)
        
        # Extract POST forms
        try:
            soup = BeautifulSoup(html, "lxml")
            for form in soup.find_all("form"):
                form_action = form.get("action", "")
                form_method = form.get("method", "GET").upper()
                form_url = urljoin(url, form_action)
                
                if form_method == "POST":
                    for input_tag in form.find_all(["input", "textarea", "select"]):
                        input_name = input_tag.get("name")
                        if not input_name:
                            continue
                        
                        if input_name.lower() in [p.lower() for p in self.context.excluded_params]:
                            continue
                        
                        input_type = input_tag.get("type", "text").lower()
                        input_value = input_tag.get("value", "")
                        
                        # Determine context
                        context = self._detect_context(html, input_name, input_value)
                        
                        injection_point = InjectionPoint(
                            url=form_url,
                            method="POST",
                            parameter=input_name,
                            context=context,
                            value=input_value,
                        )
                        injection_points.append(injection_point)
        
        except Exception:
            pass
        
        return injection_points
    
    def _detect_context(
        self, html: str, param_name: str, param_value: str
    ) -> InjectionContext:
        """
        Detect the injection context for a parameter.
        
        Args:
            html: HTML content
            param_name: Parameter name
            param_value: Parameter value
        
        Returns:
            Detected injection context
        """
        # Check if parameter appears in JavaScript
        js_patterns = [
            rf"var\s+{re.escape(param_name)}\s*=",
            rf"let\s+{re.escape(param_name)}\s*=",
            rf"const\s+{re.escape(param_name)}\s*=",
            rf"['\"]{re.escape(param_name)}['\"]\s*:",
            rf"\.{re.escape(param_name)}\s*=",
        ]
        
        for pattern in js_patterns:
            if re.search(pattern, html, re.IGNORECASE):
                return InjectionContext.JAVASCRIPT
        
        # Check if parameter appears in HTML attributes
        attr_patterns = [
            rf"<[^>]+\s+{re.escape(param_name)}\s*=",
            rf"<[^>]+\s+{re.escape(param_name)}\s*=",
        ]
        
        for pattern in attr_patterns:
            if re.search(pattern, html, re.IGNORECASE):
                return InjectionContext.HTML_ATTRIBUTE
        
        # Check if parameter appears in URL
        if "javascript:" in html.lower() or "href=" in html.lower():
            return InjectionContext.URL
        
        # Default to HTML body
        return InjectionContext.HTML_BODY
    
    async def crawl(self) -> Set[InjectionPoint]:
        """
        Crawl the web application starting from base URL.
        
        Returns:
            Set of discovered injection points
        """
        queue = deque([(self.context.base_url, 0)])
        self.visited_urls.add(self.context.base_url)
        
        while queue:
            url, depth = queue.popleft()
            
            if depth > self.context.max_depth:
                continue
            
            response = await self.fetch_url(url)
            if not response or response.status_code != 200:
                continue
            
            html = response.text
            
            # Extract injection points
            points = self.extract_injection_points(url, html, response)
            self.injection_points.update(points)
            
            # Extract links for further crawling
            if depth < self.context.max_depth:
                links = self.extract_links(html, url)
                for link in links:
                    if link not in self.visited_urls:
                        self.visited_urls.add(link)
                        queue.append((link, depth + 1))
        
        return self.injection_points

