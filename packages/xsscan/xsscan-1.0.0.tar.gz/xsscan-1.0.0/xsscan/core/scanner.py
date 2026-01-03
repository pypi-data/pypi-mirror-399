"""
XSS Scanner - Main orchestration layer.

Coordinates crawling and detection without CLI dependencies.
"""

import asyncio
from typing import List, Set
from xsscan.core.models import ScanContext, Finding, InjectionPoint
from xsscan.core.crawler import WebCrawler
from xsscan.core.detector import XSSDetector


class XSSScanner:
    """
    Main scanner class that orchestrates crawling and detection.
    
    Pure business logic - no CLI, no printing, no user interaction.
    """
    
    def __init__(self, context: ScanContext):
        """
        Initialize the scanner.
        
        Args:
            context: Scan configuration context
        """
        self.context = context
        self.findings: List[Finding] = []
        self.injection_points: Set[InjectionPoint] = set()
    
    async def scan(self) -> List[Finding]:
        """
        Perform the complete scan: crawl and detect.
        
        Returns:
            List of findings
        """
        # Phase 1: Crawling
        async with WebCrawler(self.context) as crawler:
            self.injection_points = await crawler.crawl()
        
        # Phase 2: Detection
        async with XSSDetector(self.context) as detector:
            self.findings = await detector.detect(self.injection_points)
        
        return self.findings
    
    def get_summary(self) -> dict:
        """
        Get a summary of the scan results.
        
        Returns:
            Dictionary with summary statistics
        """
        from collections import Counter
        
        severity_counts = Counter(f.severity.value for f in self.findings)
        type_counts = Counter(f.type.value for f in self.findings)
        context_counts = Counter(f.context.value for f in self.findings)
        
        return {
            "total_findings": len(self.findings),
            "total_injection_points": len(self.injection_points),
            "severity_breakdown": dict(severity_counts),
            "type_breakdown": dict(type_counts),
            "context_breakdown": dict(context_counts),
        }

