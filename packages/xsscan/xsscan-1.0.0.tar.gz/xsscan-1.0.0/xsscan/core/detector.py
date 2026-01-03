"""
XSS Detector - Detects XSS vulnerabilities in responses.

Pure detection logic with no crawling or CLI.
"""

import re
import hashlib
from typing import List, Optional, Set, Tuple
from urllib.parse import urlencode, urlunparse, urlparse, parse_qs
import httpx
from bs4 import BeautifulSoup
from xsscan.core.models import (
    Finding,
    InjectionPoint,
    InjectionContext,
    XSSType,
    Severity,
    ScanContext,
)
from xsscan.core.payloads import PayloadGenerator


class XSSDetector:
    """Detects XSS vulnerabilities by injecting payloads and analyzing responses."""
    
    def __init__(self, context: ScanContext):
        """
        Initialize the detector.
        
        Args:
            context: Scan configuration context
        """
        self.context = context
        self.payload_generator = PayloadGenerator()
        self.client: Optional[httpx.AsyncClient] = None
        self._findings: Set[Finding] = set()
    
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
    
    def _generate_vulnerability_id(
        self, url: str, parameter: str, payload: str
    ) -> str:
        """Generate a unique vulnerability ID."""
        data = f"{url}:{parameter}:{payload}"
        return hashlib.md5(data.encode()).hexdigest()[:16]
    
    def _check_reflection(self, response_text: str, payload: str) -> bool:
        """
        Check if payload is reflected in the response.
        
        Args:
            response_text: Response body
            payload: Injected payload
        
        Returns:
            True if payload is reflected
        """
        # Direct reflection
        if payload in response_text:
            return True
        
        # HTML entity encoded
        encoded = payload.replace("<", "&lt;").replace(">", "&gt;")
        if encoded in response_text:
            return True
        
        # URL encoded
        import urllib.parse
        url_encoded = urllib.parse.quote(payload)
        if url_encoded in response_text:
            return True
        
        # Check for partial reflection (common in filters)
        payload_words = payload.split()
        if len(payload_words) > 1:
            reflected_count = sum(1 for word in payload_words if word in response_text)
            if reflected_count >= len(payload_words) * 0.5:  # 50% reflection
                return True
        
        return False
    
    def _check_execution_context(
        self, response_text: str, payload: str, context: InjectionContext
    ) -> Tuple[bool, str]:
        """
        Check if payload is in an executable context.
        
        Args:
            response_text: Response body
            payload: Injected payload
            context: Expected injection context
        
        Returns:
            Tuple of (is_executable, evidence_snippet)
        """
        evidence = ""
        
        if context == InjectionContext.HTML_BODY:
            # Check if payload appears in script tags or event handlers
            script_pattern = rf"<script[^>]*>.*?{re.escape(payload)}.*?</script>"
            if re.search(script_pattern, response_text, re.IGNORECASE | re.DOTALL):
                evidence = re.search(script_pattern, response_text, re.IGNORECASE | re.DOTALL).group(0)
                return True, evidence
            
            # Check event handlers
            event_pattern = rf"on\w+\s*=\s*['\"].*?{re.escape(payload)}.*?['\"]"
            if re.search(event_pattern, response_text, re.IGNORECASE):
                evidence = re.search(event_pattern, response_text, re.IGNORECASE).group(0)
                return True, evidence
            
            # Check if payload is in HTML without encoding
            if payload in response_text and "<script" in payload:
                # Extract surrounding context
                idx = response_text.find(payload)
                start = max(0, idx - 100)
                end = min(len(response_text), idx + len(payload) + 100)
                evidence = response_text[start:end]
                return True, evidence
        
        elif context == InjectionContext.HTML_ATTRIBUTE:
            # Check if payload is in attribute value
            attr_pattern = rf"<[^>]+\s+\w+\s*=\s*['\"].*?{re.escape(payload)}.*?['\"][^>]*>"
            if re.search(attr_pattern, response_text, re.IGNORECASE):
                evidence = re.search(attr_pattern, response_text, re.IGNORECASE).group(0)
                return True, evidence
        
        elif context == InjectionContext.JAVASCRIPT:
            # Check if payload is in JavaScript code
            js_pattern = rf"(?:var|let|const|function|['\"])[^'\"]*?{re.escape(payload)}[^'\"]*?['\"]?"
            if re.search(js_pattern, response_text, re.IGNORECASE):
                evidence = re.search(js_pattern, response_text, re.IGNORECASE).group(0)
                return True, evidence
        
        elif context == InjectionContext.URL:
            # Check if payload is in URL/href
            url_pattern = rf"(?:href|src|action)\s*=\s*['\"].*?{re.escape(payload)}.*?['\"]"
            if re.search(url_pattern, response_text, re.IGNORECASE):
                evidence = re.search(url_pattern, response_text, re.IGNORECASE).group(0)
                return True, evidence
        
        # Fallback: check for reflection
        if self._check_reflection(response_text, payload):
            idx = response_text.find(payload)
            if idx == -1:
                # Try encoded versions
                encoded = payload.replace("<", "&lt;").replace(">", "&gt;")
                idx = response_text.find(encoded)
                if idx == -1:
                    return False, ""
            
            start = max(0, idx - 100)
            end = min(len(response_text), idx + len(payload) + 100)
            evidence = response_text[start:end]
            return True, evidence
        
        return False, ""
    
    def _calculate_severity(
        self, context: InjectionContext, is_executable: bool, confidence: float
    ) -> Severity:
        """Calculate severity based on context and confidence."""
        if not is_executable:
            return Severity.LOW
        
        if context == InjectionContext.JAVASCRIPT:
            if confidence >= 0.8:
                return Severity.CRITICAL
            elif confidence >= 0.6:
                return Severity.HIGH
            else:
                return Severity.MEDIUM
        
        elif context == InjectionContext.HTML_BODY:
            if confidence >= 0.8:
                return Severity.HIGH
            elif confidence >= 0.6:
                return Severity.MEDIUM
            else:
                return Severity.LOW
        
        elif context == InjectionContext.HTML_ATTRIBUTE:
            if confidence >= 0.7:
                return Severity.MEDIUM
            else:
                return Severity.LOW
        
        else:
            return Severity.LOW
    
    async def test_injection_point(
        self, injection_point: InjectionPoint
    ) -> Optional[Finding]:
        """
        Test an injection point for XSS vulnerabilities.
        
        Args:
            injection_point: The injection point to test
        
        Returns:
            Finding if vulnerability detected, None otherwise
        """
        payloads = self.payload_generator.get_payloads(
            injection_point.context, count=10
        )
        
        for payload in payloads:
            try:
                # Construct request with payload
                if injection_point.method == "GET":
                    parsed = urlparse(injection_point.url)
                    query_params = parse_qs(parsed.query, keep_blank_values=True)
                    query_params[injection_point.parameter] = [payload]
                    new_query = urlencode(query_params, doseq=True)
                    new_url = urlunparse((
                        parsed.scheme,
                        parsed.netloc,
                        parsed.path,
                        parsed.params,
                        new_query,
                        parsed.fragment,
                    ))
                    
                    response = await self.client.get(new_url)
                
                elif injection_point.method == "POST":
                    data = {injection_point.parameter: payload}
                    response = await self.client.post(
                        injection_point.url, data=data
                    )
                
                else:
                    continue
                
                if response.status_code != 200:
                    continue
                
                response_text = response.text
                
                # Check for reflection
                if not self._check_reflection(response_text, payload):
                    continue
                
                # Check execution context
                is_executable, evidence = self._check_execution_context(
                    response_text, payload, injection_point.context
                )
                
                if not evidence:
                    continue
                
                # Calculate confidence
                confidence = 0.5
                if is_executable:
                    confidence = 0.8
                if injection_point.context == InjectionContext.JAVASCRIPT:
                    confidence = 0.9
                
                # Determine XSS type (reflected for now, stored detection would require follow-up)
                xss_type = XSSType.REFLECTED
                
                # Calculate severity
                severity = self._calculate_severity(
                    injection_point.context, is_executable, confidence
                )
                
                # Create finding
                finding = Finding(
                    vulnerability_id=self._generate_vulnerability_id(
                        injection_point.url, injection_point.parameter, payload
                    ),
                    type=xss_type,
                    url=injection_point.url,
                    injection_point=injection_point,
                    payload=payload,
                    context=injection_point.context,
                    evidence=evidence[:500],  # Limit evidence length
                    severity=severity,
                    confidence=confidence,
                )
                
                return finding
            
            except Exception:
                continue
        
        return None
    
    async def detect(self, injection_points: Set[InjectionPoint]) -> List[Finding]:
        """
        Detect XSS vulnerabilities in a set of injection points.
        
        Args:
            injection_points: Set of injection points to test
        
        Returns:
            List of findings
        """
        findings = []
        
        for injection_point in injection_points:
            finding = await self.test_injection_point(injection_point)
            if finding:
                # Deduplicate
                if finding not in self._findings:
                    self._findings.add(finding)
                    findings.append(finding)
        
        return findings

