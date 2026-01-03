"""
Main CLI entry point using Typer.
"""

import sys
import asyncio
from pathlib import Path
from typing import Optional
import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich import box

from xsscan import __version__
from xsscan.core.models import ScanContext
from xsscan.core.scanner import XSSScanner
from xsscan.config.manager import ConfigManager
from xsscan.reporting.export import ReportExporter

app = typer.Typer(
    name="xsscan",
    help="Production-grade XSS detection tool",
    add_completion=False,
)
console = Console()


@app.command()
def version():
    """Show version information."""
    console.print(f"[bold green]XSScan[/bold green] version [cyan]{__version__}[/cyan]")


@app.command()
def scan(
    url: str = typer.Option(..., "-u", "--url", help="Target URL to scan"),
    depth: int = typer.Option(2, "-d", "--depth", help="Maximum crawl depth"),
    timeout: float = typer.Option(10.0, "--timeout", help="Request timeout in seconds"),
    rate_limit: float = typer.Option(1.0, "--rate-limit", help="Requests per second"),
    threads: int = typer.Option(5, "--threads", help="Maximum concurrent threads"),
    payload_set: Optional[str] = typer.Option(None, "--payload-set", help="Payload set to use"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Verbose output"),
    silent: bool = typer.Option(False, "--silent", "-s", help="Silent mode (minimal output)"),
    json: Optional[Path] = typer.Option(None, "--json", help="Export results as JSON"),
    html: Optional[Path] = typer.Option(None, "--html", help="Export results as HTML"),
    pdf: Optional[Path] = typer.Option(None, "--pdf", help="Export results as PDF"),
    txt: Optional[Path] = typer.Option(None, "--txt", help="Export results as TXT"),
    output: Optional[Path] = typer.Option(None, "-o", "--output", help="Output file path"),
):
    """
    Scan a target URL for XSS vulnerabilities.
    
    Example:
        xsscan scan -u https://example.com -d 2
    """
    try:
        # Load configuration
        config_manager = ConfigManager()
        config = config_manager.load()
        
        # Override with CLI options
        if timeout == 10.0 and config.get("default_timeout"):
            timeout = config["default_timeout"]
        if depth == 2 and config.get("default_depth"):
            depth = config["default_depth"]
        
        # Create scan context
        scan_context = ScanContext(
            base_url=url,
            max_depth=depth,
            timeout=timeout,
            rate_limit=rate_limit,
            max_threads=threads,
            headers=config.get("headers", {}),
            cookies=config.get("cookies", {}),
            excluded_paths=config.get("excluded_paths", []),
            excluded_params=config.get("excluded_params", []),
        )
        
        if not silent:
            console.print(Panel.fit(
                f"[bold cyan]XSScan[/bold cyan] - XSS Vulnerability Scanner\n"
                f"Target: [yellow]{url}[/yellow]\n"
                f"Depth: [yellow]{depth}[/yellow] | Timeout: [yellow]{timeout}s[/yellow]",
                border_style="cyan"
            ))
        
        # Run scan
        scanner = XSSScanner(scan_context)
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
            disable=silent,
        ) as progress:
            task = progress.add_task("[cyan]Scanning...", total=None)
            
            try:
                findings = asyncio.run(scanner.scan())
            except KeyboardInterrupt:
                console.print("\n[yellow]Scan interrupted by user[/yellow]")
                sys.exit(2)
            except Exception as e:
                if verbose:
                    console.print_exception()
                else:
                    console.print(f"[red]Error:[/red] {str(e)}")
                sys.exit(2)
            finally:
                progress.update(task, completed=True)
        
        # Display results
        if not silent:
            _display_results(scanner, findings, verbose)
        
        # Export results
        exporter = ReportExporter()
        export_paths = []
        
        if json:
            path = exporter.export_json(findings, json)
            export_paths.append(("JSON", path))
        
        if html:
            path = exporter.export_html(findings, html, scan_context)
            export_paths.append(("HTML", path))
        
        if pdf:
            path = exporter.export_pdf(findings, pdf, scan_context)
            export_paths.append(("PDF", path))
        
        if txt:
            path = exporter.export_txt(findings, txt)
            export_paths.append(("TXT", path))
        
        if output:
            # Determine format from extension
            ext = output.suffix.lower()
            if ext == ".json":
                path = exporter.export_json(findings, output)
            elif ext == ".html":
                path = exporter.export_html(findings, output, scan_context)
            elif ext == ".pdf":
                path = exporter.export_pdf(findings, output, scan_context)
            elif ext == ".txt":
                path = exporter.export_txt(findings, output)
            else:
                # Default to JSON
                path = exporter.export_json(findings, output.with_suffix(".json"))
            export_paths.append(("Report", path))
        
        if export_paths and not silent:
            console.print("\n[green]Reports exported:[/green]")
            for fmt, path in export_paths:
                console.print(f"  [cyan]{fmt}:[/cyan] {path}")
        
        # Exit code
        if findings:
            sys.exit(1)  # Vulnerabilities found
        else:
            sys.exit(0)  # No vulnerabilities
    
    except Exception as e:
        if verbose:
            console.print_exception()
        else:
            console.print(f"[red]Error:[/red] {str(e)}")
        sys.exit(2)


def _display_results(scanner: XSSScanner, findings: list, verbose: bool):
    """Display scan results in the console."""
    summary = scanner.get_summary()
    
    # Summary panel
    summary_text = (
        f"[bold]Total Findings:[/bold] {summary['total_findings']}\n"
        f"[bold]Injection Points Tested:[/bold] {summary['total_injection_points']}"
    )
    console.print(Panel(summary_text, title="[bold cyan]Scan Summary[/bold cyan]", border_style="cyan"))
    
    if not findings:
        console.print("\n[green]✓ No XSS vulnerabilities detected[/green]")
        return
    
    # Severity breakdown
    severity_table = Table(title="Severity Breakdown", box=box.ROUNDED)
    severity_table.add_column("Severity", style="cyan")
    severity_table.add_column("Count", style="yellow", justify="right")
    
    for severity, count in summary['severity_breakdown'].items():
        color = {
            "critical": "red",
            "high": "bright_red",
            "medium": "yellow",
            "low": "blue",
            "info": "white",
        }.get(severity, "white")
        severity_table.add_row(f"[{color}]{severity.upper()}[/{color}]", str(count))
    
    console.print("\n")
    console.print(severity_table)
    
    # Findings table
    findings_table = Table(title="[bold red]XSS Vulnerabilities Detected[/bold red]", box=box.ROUNDED)
    findings_table.add_column("ID", style="cyan", width=10)
    findings_table.add_column("Type", style="yellow")
    findings_table.add_column("Severity", style="red")
    findings_table.add_column("URL", style="blue")
    findings_table.add_column("Parameter", style="magenta")
    findings_table.add_column("Context", style="green")
    
    for finding in findings:
        severity_color = {
            "critical": "red",
            "high": "bright_red",
            "medium": "yellow",
            "low": "blue",
            "info": "white",
        }.get(finding.severity.value, "white")
        
        findings_table.add_row(
            finding.vulnerability_id[:8],
            finding.type.value.upper(),
            f"[{severity_color}]{finding.severity.value.upper()}[/{severity_color}]",
            finding.url[:50] + "..." if len(finding.url) > 50 else finding.url,
            finding.injection_point.parameter,
            finding.context.value,
        )
    
    console.print("\n")
    console.print(findings_table)
    
    # Detailed view for verbose mode
    if verbose:
        console.print("\n[bold cyan]Detailed Findings:[/bold cyan]\n")
        for i, finding in enumerate(findings, 1):
            console.print(Panel(
                f"[bold]Vulnerability ID:[/bold] {finding.vulnerability_id}\n"
                f"[bold]Type:[/bold] {finding.type.value}\n"
                f"[bold]URL:[/bold] {finding.url}\n"
                f"[bold]Method:[/bold] {finding.injection_point.method}\n"
                f"[bold]Parameter:[/bold] {finding.injection_point.parameter}\n"
                f"[bold]Context:[/bold] {finding.context.value}\n"
                f"[bold]Payload:[/bold] {finding.payload}\n"
                f"[bold]Confidence:[/bold] {finding.confidence:.2%}\n"
                f"[bold]Evidence:[/bold]\n{finding.evidence[:200]}...",
                title=f"[bold red]Finding #{i}[/bold red]",
                border_style="red",
            ))


@app.command()
def config(
    action: str = typer.Argument(..., help="Action: set, get, show, reset"),
    key: Optional[str] = typer.Argument(None, help="Configuration key"),
    value: Optional[str] = typer.Argument(None, help="Configuration value"),
):
    """
    Manage configuration settings.
    
    Examples:
        xsscan config show
        xsscan config set default_depth 3
        xsscan config get default_depth
        xsscan config reset
    """
    config_manager = ConfigManager()
    
    if action == "show":
        config = config_manager.load()
        if not config:
            console.print("[yellow]No configuration found. Using defaults.[/yellow]")
            return
        
        table = Table(title="Configuration", box=box.ROUNDED)
        table.add_column("Key", style="cyan")
        table.add_column("Value", style="yellow")
        
        for k, v in config.items():
            if isinstance(v, dict):
                v = str(v)
            table.add_row(k, str(v))
        
        console.print(table)
    
    elif action == "set":
        if not key:
            console.print("[red]Error:[/red] Key is required for 'set' action")
            sys.exit(2)
        if not value:
            console.print("[red]Error:[/red] Value is required for 'set' action")
            sys.exit(2)
        
        config_manager.set(key, value)
        console.print(f"[green]✓[/green] Set [cyan]{key}[/cyan] = [yellow]{value}[/yellow]")
    
    elif action == "get":
        if not key:
            console.print("[red]Error:[/red] Key is required for 'get' action")
            sys.exit(2)
        
        value = config_manager.get(key)
        if value is None:
            console.print(f"[yellow]Key '{key}' not found in configuration[/yellow]")
        else:
            console.print(f"[cyan]{key}[/cyan] = [yellow]{value}[/yellow]")
    
    elif action == "reset":
        if typer.confirm("Are you sure you want to reset all configuration?"):
            config_manager.reset()
            console.print("[green]✓[/green] Configuration reset")
        else:
            console.print("[yellow]Reset cancelled[/yellow]")
    
    else:
        console.print(f"[red]Error:[/red] Unknown action '{action}'")
        console.print("Available actions: show, set, get, reset")
        sys.exit(2)


@app.command()
def report(
    input_file: Path = typer.Argument(..., help="Input JSON report file"),
    format: str = typer.Option("html", "--format", "-f", help="Output format: json, html, pdf, txt"),
    output: Path = typer.Option(..., "-o", "--output", help="Output file path"),
):
    """
    Convert or regenerate reports from JSON results.
    
    Example:
        xsscan report results.json -f html -o report.html
    """
    try:
        exporter = ReportExporter()
        
        # Load findings from JSON
        findings = exporter.load_json(input_file)
        
        # Export in requested format
        if format == "json":
            path = exporter.export_json(findings, output)
        elif format == "html":
            # Create a minimal scan context for HTML export
            from xsscan.core.models import ScanContext
            context = ScanContext(base_url="unknown")
            path = exporter.export_html(findings, output, context)
        elif format == "pdf":
            from xsscan.core.models import ScanContext
            context = ScanContext(base_url="unknown")
            path = exporter.export_pdf(findings, output, context)
        elif format == "txt":
            path = exporter.export_txt(findings, output)
        else:
            console.print(f"[red]Error:[/red] Unknown format '{format}'")
            sys.exit(2)
        
        console.print(f"[green]✓[/green] Report exported to [cyan]{path}[/cyan]")
    
    except Exception as e:
        console.print(f"[red]Error:[/red] {str(e)}")
        sys.exit(2)


def main():
    """Main entry point for the CLI."""
    app()


if __name__ == "__main__":
    main()

