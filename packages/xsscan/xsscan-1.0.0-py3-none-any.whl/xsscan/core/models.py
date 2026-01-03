"""
Data models for the core engine.

Pure data structures with no business logic.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional, Dict, Any, List
from datetime import datetime
from urllib.parse import urlparse


class XSSType(str, Enum):
    """Types of XSS vulnerabilities."""
    REFLECTED = "reflected"
    STORED = "stored"
    DOM = "dom"


class Severity(str, Enum):
    """Vulnerability severity levels."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


class InjectionContext(str, Enum):
    """Context where payload is injected."""
    HTML_BODY = "html_body"
    HTML_ATTRIBUTE = "html_attribute"
    JAVASCRIPT = "javascript"
    URL = "url"
    CSS = "css"


@dataclass
class InjectionPoint:
    """Represents a point where payload can be injected."""
    url: str
    method: str  # GET, POST, etc.
    parameter: str
    context: InjectionContext
    value: Optional[str] = None
    headers: Dict[str, str] = field(default_factory=dict)
    cookies: Dict[str, str] = field(default_factory=dict)
    
    def __hash__(self):
        return hash((self.url, self.method, self.parameter, self.context))
    
    def __eq__(self, other):
        if not isinstance(other, InjectionPoint):
            return False
        return (self.url == other.url and
                self.method == other.method and
                self.parameter == other.parameter and
                self.context == other.context)


@dataclass
class Finding:
    """Represents a detected XSS vulnerability."""
    vulnerability_id: str
    type: XSSType
    url: str
    injection_point: InjectionPoint
    payload: str
    context: InjectionContext
    evidence: str  # Response snippet showing the vulnerability
    severity: Severity
    confidence: float  # 0.0 to 1.0
    timestamp: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __hash__(self):
        return hash((self.url, self.injection_point.parameter, self.payload))
    
    def __eq__(self, other):
        if not isinstance(other, Finding):
            return False
        return (self.url == other.url and
                self.injection_point.parameter == other.injection_point.parameter and
                self.payload == other.payload)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert finding to dictionary for serialization."""
        return {
            "vulnerability_id": self.vulnerability_id,
            "type": self.type.value,
            "url": self.url,
            "injection_point": {
                "url": self.injection_point.url,
                "method": self.injection_point.method,
                "parameter": self.injection_point.parameter,
                "context": self.injection_point.context.value,
                "value": self.injection_point.value,
                "headers": self.injection_point.headers,
                "cookies": self.injection_point.cookies,
            },
            "payload": self.payload,
            "context": self.context.value,
            "evidence": self.evidence,
            "severity": self.severity.value,
            "confidence": self.confidence,
            "timestamp": self.timestamp.isoformat(),
            "metadata": self.metadata,
        }


@dataclass
class ScanContext:
    """Context for a scan operation."""
    base_url: str
    max_depth: int = 2
    timeout: float = 10.0
    rate_limit: float = 1.0  # requests per second
    max_threads: int = 5
    follow_redirects: bool = True
    verify_ssl: bool = True
    user_agent: str = "XSScan/1.0.0"
    headers: Dict[str, str] = field(default_factory=dict)
    cookies: Dict[str, str] = field(default_factory=dict)
    excluded_paths: List[str] = field(default_factory=list)
    excluded_params: List[str] = field(default_factory=list)
    
    def __post_init__(self):
        """Validate and normalize the scan context."""
        parsed = urlparse(self.base_url)
        if not parsed.scheme or not parsed.netloc:
            raise ValueError(f"Invalid base URL: {self.base_url}")
        
        if self.max_depth < 0:
            raise ValueError("max_depth must be >= 0")
        
        if self.timeout <= 0:
            raise ValueError("timeout must be > 0")
        
        if self.rate_limit <= 0:
            raise ValueError("rate_limit must be > 0")
        
        if self.max_threads < 1:
            raise ValueError("max_threads must be >= 1")

