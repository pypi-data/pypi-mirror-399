"""
Core Engine - Scanner Layer

Pure Python logic for XSS detection.
No CLI, no printing, no user interaction.
Fully testable.
"""

from xsscan.core.scanner import XSSScanner
from xsscan.core.crawler import WebCrawler
from xsscan.core.payloads import PayloadGenerator
from xsscan.core.detector import XSSDetector
from xsscan.core.models import Finding, ScanContext, InjectionPoint

__all__ = [
    "XSSScanner",
    "WebCrawler",
    "PayloadGenerator",
    "XSSDetector",
    "Finding",
    "ScanContext",
    "InjectionPoint",
]

