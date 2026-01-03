"""
Report Exporter - Exports findings to various formats.
"""

import json
from pathlib import Path
from typing import List
from datetime import datetime
from xsscan.core.models import Finding, ScanContext


class ReportExporter:
    """Exports scan findings to various formats."""
    
    def load_json(self, file_path: Path) -> List[Finding]:
        """
        Load findings from JSON file.
        
        Args:
            file_path: Path to JSON file
        
        Returns:
            List of Finding objects
        """
        with open(file_path, "r") as f:
            data = json.load(f)
        
        findings = []
        for item in data.get("findings", []):
            # Reconstruct Finding from dict
            from xsscan.core.models import (
                InjectionPoint, InjectionContext, XSSType, Severity
            )
            
            injection_point = InjectionPoint(
                url=item["injection_point"]["url"],
                method=item["injection_point"]["method"],
                parameter=item["injection_point"]["parameter"],
                context=InjectionContext(item["injection_point"]["context"]),
                value=item["injection_point"].get("value"),
                headers=item["injection_point"].get("headers", {}),
                cookies=item["injection_point"].get("cookies", {}),
            )
            
            finding = Finding(
                vulnerability_id=item["vulnerability_id"],
                type=XSSType(item["type"]),
                url=item["url"],
                injection_point=injection_point,
                payload=item["payload"],
                context=InjectionContext(item["context"]),
                evidence=item["evidence"],
                severity=Severity(item["severity"]),
                confidence=item["confidence"],
                timestamp=datetime.fromisoformat(item["timestamp"]),
                metadata=item.get("metadata", {}),
            )
            findings.append(finding)
        
        return findings
    
    def export_json(self, findings: List[Finding], file_path: Path) -> Path:
        """
        Export findings to JSON format.
        
        Args:
            findings: List of findings
            file_path: Output file path
        
        Returns:
            Path to exported file
        """
        data = {
            "scan_date": datetime.utcnow().isoformat(),
            "total_findings": len(findings),
            "findings": [f.to_dict() for f in findings],
        }
        
        with open(file_path, "w") as f:
            json.dump(data, f, indent=2)
        
        return file_path
    
    def export_txt(self, findings: List[Finding], file_path: Path) -> Path:
        """
        Export findings to plain text format.
        
        Args:
            findings: List of findings
            file_path: Output file path
        
        Returns:
            Path to exported file
        """
        with open(file_path, "w") as f:
            f.write("=" * 80 + "\n")
            f.write("XSScan - XSS Vulnerability Report\n")
            f.write("=" * 80 + "\n\n")
            f.write(f"Scan Date: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}\n")
            f.write(f"Total Findings: {len(findings)}\n\n")
            
            if not findings:
                f.write("No XSS vulnerabilities detected.\n")
                return file_path
            
            for i, finding in enumerate(findings, 1):
                f.write("-" * 80 + "\n")
                f.write(f"Finding #{i}\n")
                f.write("-" * 80 + "\n")
                f.write(f"Vulnerability ID: {finding.vulnerability_id}\n")
                f.write(f"Type: {finding.type.value.upper()}\n")
                f.write(f"Severity: {finding.severity.value.upper()}\n")
                f.write(f"Confidence: {finding.confidence:.2%}\n")
                f.write(f"URL: {finding.url}\n")
                f.write(f"Method: {finding.injection_point.method}\n")
                f.write(f"Parameter: {finding.injection_point.parameter}\n")
                f.write(f"Context: {finding.context.value}\n")
                f.write(f"Payload: {finding.payload}\n")
                f.write(f"\nEvidence:\n{finding.evidence}\n")
                f.write("\n")
        
        return file_path
    
    def export_html(
        self, findings: List[Finding], file_path: Path, context: ScanContext
    ) -> Path:
        """
        Export findings to HTML format.
        
        Args:
            findings: List of findings
            file_path: Output file path
            context: Scan context
        
        Returns:
            Path to exported file
        """
        html_template = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>XSScan - XSS Vulnerability Report</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            line-height: 1.6;
            color: #333;
            background: #f5f5f5;
            padding: 20px;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            padding: 30px;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        h1 {{
            color: #2c3e50;
            border-bottom: 3px solid #3498db;
            padding-bottom: 10px;
            margin-bottom: 20px;
        }}
        .summary {{
            background: #ecf0f1;
            padding: 20px;
            border-radius: 5px;
            margin-bottom: 30px;
        }}
        .summary h2 {{
            color: #2c3e50;
            margin-bottom: 15px;
        }}
        .summary-item {{
            display: inline-block;
            margin-right: 30px;
            margin-bottom: 10px;
        }}
        .summary-item strong {{
            color: #34495e;
        }}
        .finding {{
            border: 1px solid #ddd;
            border-radius: 5px;
            padding: 20px;
            margin-bottom: 20px;
            background: #fff;
        }}
        .finding-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 15px;
            padding-bottom: 10px;
            border-bottom: 2px solid #ecf0f1;
        }}
        .finding-id {{
            font-family: 'Courier New', monospace;
            color: #7f8c8d;
            font-size: 0.9em;
        }}
        .severity {{
            padding: 5px 15px;
            border-radius: 20px;
            font-weight: bold;
            font-size: 0.9em;
        }}
        .severity-critical {{
            background: #e74c3c;
            color: white;
        }}
        .severity-high {{
            background: #c0392b;
            color: white;
        }}
        .severity-medium {{
            background: #f39c12;
            color: white;
        }}
        .severity-low {{
            background: #3498db;
            color: white;
        }}
        .severity-info {{
            background: #95a5a6;
            color: white;
        }}
        .finding-details {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 15px;
            margin-bottom: 15px;
        }}
        .detail-item {{
            padding: 10px;
            background: #f8f9fa;
            border-radius: 3px;
        }}
        .detail-label {{
            font-weight: bold;
            color: #34495e;
            margin-bottom: 5px;
        }}
        .detail-value {{
            color: #2c3e50;
            word-break: break-all;
        }}
        .evidence {{
            background: #2c3e50;
            color: #ecf0f1;
            padding: 15px;
            border-radius: 5px;
            font-family: 'Courier New', monospace;
            font-size: 0.9em;
            overflow-x: auto;
            white-space: pre-wrap;
            word-wrap: break-word;
        }}
        .no-findings {{
            text-align: center;
            padding: 40px;
            color: #27ae60;
            font-size: 1.2em;
        }}
        .footer {{
            margin-top: 30px;
            padding-top: 20px;
            border-top: 1px solid #ddd;
            text-align: center;
            color: #7f8c8d;
            font-size: 0.9em;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>XSScan - XSS Vulnerability Report</h1>
        
        <div class="summary">
            <h2>Scan Summary</h2>
            <div class="summary-item">
                <strong>Target URL:</strong> {target_url}
            </div>
            <div class="summary-item">
                <strong>Scan Date:</strong> {scan_date}
            </div>
            <div class="summary-item">
                <strong>Total Findings:</strong> {total_findings}
            </div>
        </div>
        
        {findings_html}
        
        <div class="footer">
            <p>Generated by XSScan v1.0.0</p>
            <p>Report generated on {generated_date}</p>
        </div>
    </div>
</body>
</html>"""
        
        if not findings:
            findings_html = '<div class="no-findings">✓ No XSS vulnerabilities detected</div>'
        else:
            findings_html = ""
            for i, finding in enumerate(findings, 1):
                severity_class = f"severity-{finding.severity.value}"
                
                findings_html += f"""
        <div class="finding">
            <div class="finding-header">
                <div>
                    <h2>Finding #{i}</h2>
                    <div class="finding-id">ID: {finding.vulnerability_id}</div>
                </div>
                <span class="severity {severity_class}">{finding.severity.value.upper()}</span>
            </div>
            <div class="finding-details">
                <div class="detail-item">
                    <div class="detail-label">Type</div>
                    <div class="detail-value">{finding.type.value.upper()}</div>
                </div>
                <div class="detail-item">
                    <div class="detail-label">Confidence</div>
                    <div class="detail-value">{finding.confidence:.2%}</div>
                </div>
                <div class="detail-item">
                    <div class="detail-label">URL</div>
                    <div class="detail-value">{finding.url}</div>
                </div>
                <div class="detail-item">
                    <div class="detail-label">Method</div>
                    <div class="detail-value">{finding.injection_point.method}</div>
                </div>
                <div class="detail-item">
                    <div class="detail-label">Parameter</div>
                    <div class="detail-value">{finding.injection_point.parameter}</div>
                </div>
                <div class="detail-item">
                    <div class="detail-label">Context</div>
                    <div class="detail-value">{finding.context.value}</div>
                </div>
                <div class="detail-item" style="grid-column: 1 / -1;">
                    <div class="detail-label">Payload</div>
                    <div class="detail-value">{finding.payload}</div>
                </div>
            </div>
            <div>
                <div class="detail-label" style="margin-bottom: 10px;">Evidence</div>
                <div class="evidence">{self._escape_html(finding.evidence)}</div>
            </div>
        </div>
"""
        
        html_content = html_template.format(
            target_url=context.base_url,
            scan_date=datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC"),
            total_findings=len(findings),
            findings_html=findings_html,
            generated_date=datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC"),
        )
        
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(html_content)
        
        return file_path
    
    def export_pdf(
        self, findings: List[Finding], file_path: Path, context: ScanContext
    ) -> Path:
        """
        Export findings to PDF format.
        
        Args:
            findings: List of findings
            file_path: Output file path
            context: Scan context
        
        Returns:
            Path to exported file
        """
        from reportlab.lib.pagesizes import letter, A4
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.units import inch
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
        from reportlab.lib import colors
        from reportlab.lib.enums import TA_CENTER, TA_LEFT
        
        doc = SimpleDocTemplate(
            str(file_path),
            pagesize=letter,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=18,
        )
        
        story = []
        styles = getSampleStyleSheet()
        
        # Title
        title_style = ParagraphStyle(
            "CustomTitle",
            parent=styles["Heading1"],
            fontSize=24,
            textColor=colors.HexColor("#2c3e50"),
            spaceAfter=30,
            alignment=TA_CENTER,
        )
        story.append(Paragraph("XSScan - XSS Vulnerability Report", title_style))
        story.append(Spacer(1, 0.2 * inch))
        
        # Summary
        summary_data = [
            ["Target URL", context.base_url],
            ["Scan Date", datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")],
            ["Total Findings", str(len(findings))],
        ]
        
        summary_table = Table(summary_data, colWidths=[2 * inch, 4 * inch])
        summary_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#ecf0f1")),
            ("TEXTCOLOR", (0, 0), (-1, -1), colors.black),
            ("ALIGN", (0, 0), (-1, -1), "LEFT"),
            ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 10),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 12),
            ("GRID", (0, 0), (-1, -1), 1, colors.grey),
        ]))
        story.append(summary_table)
        story.append(Spacer(1, 0.3 * inch))
        
        if not findings:
            story.append(Paragraph("✓ No XSS vulnerabilities detected", styles["Normal"]))
        else:
            # Findings
            for i, finding in enumerate(findings, 1):
                finding_style = ParagraphStyle(
                    "FindingTitle",
                    parent=styles["Heading2"],
                    fontSize=16,
                    textColor=colors.HexColor("#2c3e50"),
                    spaceAfter=12,
                )
                
                story.append(Paragraph(f"Finding #{i}", finding_style))
                
                finding_data = [
                    ["Vulnerability ID", finding.vulnerability_id],
                    ["Type", finding.type.value.upper()],
                    ["Severity", finding.severity.value.upper()],
                    ["Confidence", f"{finding.confidence:.2%}"],
                    ["URL", finding.url],
                    ["Method", finding.injection_point.method],
                    ["Parameter", finding.injection_point.parameter],
                    ["Context", finding.context.value],
                    ["Payload", finding.payload],
                ]
                
                finding_table = Table(finding_data, colWidths=[2 * inch, 4 * inch])
                finding_table.setStyle(TableStyle([
                    ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#f8f9fa")),
                    ("TEXTCOLOR", (0, 0), (-1, -1), colors.black),
                    ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                    ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
                    ("FONTSIZE", (0, 0), (-1, -1), 9),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
                    ("GRID", (0, 0), (-1, -1), 1, colors.grey),
                ]))
                story.append(finding_table)
                story.append(Spacer(1, 0.2 * inch))
                
                # Evidence
                evidence_style = ParagraphStyle(
                    "Evidence",
                    parent=styles["Code"],
                    fontSize=8,
                    textColor=colors.white,
                    backColor=colors.HexColor("#2c3e50"),
                    leftIndent=12,
                    rightIndent=12,
                    spaceAfter=12,
                )
                story.append(Paragraph("Evidence:", styles["Heading3"]))
                story.append(Paragraph(finding.evidence[:500], evidence_style))
                story.append(Spacer(1, 0.3 * inch))
                
                if i < len(findings):
                    story.append(PageBreak())
        
        # Footer
        story.append(Spacer(1, 0.3 * inch))
        footer_style = ParagraphStyle(
            "Footer",
            parent=styles["Normal"],
            fontSize=8,
            textColor=colors.grey,
            alignment=TA_CENTER,
        )
        story.append(Paragraph("Generated by XSScan v1.0.0", footer_style))
        
        doc.build(story)
        return file_path
    
    def _escape_html(self, text: str) -> str:
        """Escape HTML special characters."""
        return (
            text.replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace('"', "&quot;")
            .replace("'", "&#x27;")
        )

