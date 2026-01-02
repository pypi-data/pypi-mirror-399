"""CLI interface for netspecs using Typer."""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Annotated, Optional

import typer
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

from netspecs import __version__
from netspecs.core.bufferbloat import test_bufferbloat
from netspecs.core.connectivity import check_connectivity_batch, get_connectivity_summary
from netspecs.core.jitter import measure_jitter, measure_jitter_batch
from netspecs.core.latency import test_latency, test_latency_batch
from netspecs.core.monitor import long_monitor
from netspecs.core.network_info import capture_network_info
from netspecs.core.prioritization import detect_prioritization
from netspecs.core.speed import test_bandwidth_variability, test_speed
from netspecs.reporters.console import ConsoleReporter
from netspecs.reporters.csv import CSVReporter
from netspecs.reporters.json import JSONReporter
from netspecs.utils.config import DEFAULT_ENDPOINTS, load_config

app = typer.Typer(
    name="netspecs",
    help="Cross-platform internet diagnostics with AI-powered analysis.",
    no_args_is_help=True,
)

console = Console()


class OutputFormat(str, Enum):
    """Output format options."""
    console = "console"
    json = "json"
    csv = "csv"


def version_callback(value: bool):
    """Print version and exit."""
    if value:
        console.print(f"netspecs version {__version__}")
        raise typer.Exit()


@app.callback()
def main(
    version: Annotated[
        Optional[bool],
        typer.Option("--version", "-v", callback=version_callback, is_eager=True),
    ] = None,
):
    """Netspecs - Cross-platform internet diagnostics with AI-powered analysis."""
    pass


@app.command()
def run(
    output: Annotated[OutputFormat, typer.Option("--output", "-o", help="Output format")] = OutputFormat.console,
    output_dir: Annotated[Optional[Path], typer.Option("--output-dir", "-d", help="Output directory for logs")] = None,
    endpoints: Annotated[Optional[str], typer.Option("--endpoints", "-e", help="Comma-separated list of endpoints")] = None,
    skip_speed: Annotated[bool, typer.Option("--skip-speed", help="Skip speed tests")] = False,
    skip_jitter: Annotated[bool, typer.Option("--skip-jitter", help="Skip detailed jitter tests")] = False,
    ai_report: Annotated[bool, typer.Option("--ai-report", help="Generate AI diagnostic report")] = False,
    model: Annotated[Optional[str], typer.Option("--model", "-m", help="LLM model for AI report")] = None,
    api_key: Annotated[Optional[str], typer.Option("--api-key", "-k", help="API key for LLM")] = None,
):
    """Run full diagnostic suite."""
    config = load_config(
        api_key=api_key,
        model=model,
        output_dir=str(output_dir) if output_dir else None,
        output_format=output.value,
    )
    
    if endpoints:
        config.endpoints = [e.strip() for e in endpoints.split(",")]
    
    results = {}
    reporter = _get_reporter(output)
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        # Connectivity check
        task = progress.add_task("Checking connectivity...", total=None)
        connectivity_results = check_connectivity_batch(config.endpoints)
        results["connectivity"] = [r.to_dict() for r in connectivity_results]
        results["connectivity_summary"] = get_connectivity_summary(connectivity_results)
        progress.remove_task(task)
        
        # Latency tests
        task = progress.add_task("Testing latency...", total=None)
        latency_results = test_latency_batch(config.endpoints, count=config.ping_count)
        results["latency"] = [r.to_dict() for r in latency_results]
        progress.remove_task(task)
        
        # Jitter tests (first 3 endpoints)
        if not skip_jitter:
            task = progress.add_task("Measuring jitter...", total=None)
            jitter_hosts = config.endpoints[:3]
            jitter_results = measure_jitter_batch(
                jitter_hosts,
                duration=config.jitter_duration,
                interval=config.jitter_interval,
            )
            results["jitter"] = [r.to_dict() for r in jitter_results]
            progress.remove_task(task)
        
        # Speed tests
        if not skip_speed:
            task = progress.add_task("Testing speed...", total=None)
            speed_result = test_speed()
            results["speed"] = speed_result.to_dict()
            
            variability = test_bandwidth_variability(iterations=config.speed_test_iterations)
            results["bandwidth_variability"] = variability
            progress.remove_task(task)
    
    # Generate report
    reporter.report(results, config.output_dir)
    
    # AI report if requested
    if ai_report:
        _generate_ai_report(results, config)


@app.command()
def latency(
    output: Annotated[OutputFormat, typer.Option("--output", "-o", help="Output format")] = OutputFormat.console,
    endpoints: Annotated[Optional[str], typer.Option("--endpoints", "-e", help="Comma-separated list of endpoints")] = None,
    count: Annotated[int, typer.Option("--count", "-c", help="Number of ping packets")] = 20,
):
    """Test latency to endpoints."""
    hosts = [e.strip() for e in endpoints.split(",")] if endpoints else DEFAULT_ENDPOINTS
    reporter = _get_reporter(output)
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("Testing latency...", total=None)
        results = test_latency_batch(hosts, count=count)
        progress.remove_task(task)
    
    reporter.report({"latency": [r.to_dict() for r in results]})


@app.command()
def speed(
    output: Annotated[OutputFormat, typer.Option("--output", "-o", help="Output format")] = OutputFormat.console,
    skip_ookla: Annotated[bool, typer.Option("--skip-ookla", help="Skip Ookla Speedtest")] = False,
    iterations: Annotated[int, typer.Option("--iterations", "-i", help="Variability test iterations")] = 5,
):
    """Test internet speed."""
    reporter = _get_reporter(output)
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("Testing speed...", total=None)
        speed_result = test_speed(include_ookla=not skip_ookla)
        variability = test_bandwidth_variability(iterations=iterations)
        progress.remove_task(task)
    
    reporter.report({
        "speed": speed_result.to_dict(),
        "bandwidth_variability": variability,
    })


@app.command()
def jitter(
    output: Annotated[OutputFormat, typer.Option("--output", "-o", help="Output format")] = OutputFormat.console,
    endpoints: Annotated[Optional[str], typer.Option("--endpoints", "-e", help="Comma-separated list of endpoints")] = None,
    duration: Annotated[int, typer.Option("--duration", "-t", help="Duration in seconds")] = 30,
    interval: Annotated[int, typer.Option("--interval", help="Interval between pings")] = 1,
):
    """Measure jitter (latency variation)."""
    hosts = [e.strip() for e in endpoints.split(",")] if endpoints else DEFAULT_ENDPOINTS[:3]
    reporter = _get_reporter(output)
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("Measuring jitter...", total=None)
        results = measure_jitter_batch(hosts, duration=duration, interval=interval)
        progress.remove_task(task)
    
    reporter.report({"jitter": [r.to_dict() for r in results]})


@app.command()
def prioritization(
    output: Annotated[OutputFormat, typer.Option("--output", "-o", help="Output format")] = OutputFormat.console,
    host: Annotated[str, typer.Option("--host", "-h", help="Target host")] = "8.8.8.8",
    duration: Annotated[int, typer.Option("--duration", "-t", help="Duration per phase in seconds")] = 60,
):
    """Detect connection prioritization/throttling."""
    reporter = _get_reporter(output)
    
    console.print(f"[bold]Running prioritization detection test[/bold]")
    console.print(f"Target: {host}")
    console.print(f"Duration per phase: {duration}s (5 phases, ~{duration * 5 // 60} min total)")
    console.print()
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("Running prioritization test...", total=None)
        result = detect_prioritization(host=host, phase_duration=duration)
        progress.remove_task(task)
    
    reporter.report({"prioritization": result.to_dict()})


@app.command()
def report(
    input_file: Annotated[Path, typer.Argument(help="JSON results file to analyze")],
    output: Annotated[OutputFormat, typer.Option("--output", "-o", help="Output format")] = OutputFormat.console,
    model: Annotated[Optional[str], typer.Option("--model", "-m", help="LLM model")] = None,
    api_key: Annotated[Optional[str], typer.Option("--api-key", "-k", help="API key for LLM")] = None,
):
    """Generate AI diagnostic report from results file."""
    import json
    
    if not input_file.exists():
        console.print(f"[red]Error: File not found: {input_file}[/red]")
        raise typer.Exit(1)
    
    with open(input_file) as f:
        results = json.load(f)
    
    config = load_config(api_key=api_key, model=model)
    _generate_ai_report(results, config)


@app.command()
def bufferbloat(
    output: Annotated[OutputFormat, typer.Option("--output", "-o", help="Output format")] = OutputFormat.console,
    host: Annotated[str, typer.Option("--host", help="Target host")] = "1.1.1.1",
    baseline_duration: Annotated[int, typer.Option("--baseline", help="Baseline measurement duration")] = 15,
    load_duration: Annotated[int, typer.Option("--load-duration", help="Loaded test duration")] = 30,
    include_upload: Annotated[bool, typer.Option("--include-upload/--no-upload", help="Include upload traffic")] = True,
):
    """
    Test for bufferbloat (latency under network load).
    
    This test measures latency while generating download/upload traffic
    to detect buffer bloat issues that cause lag during normal usage.
    """
    reporter = _get_reporter(output)
    
    console.print("[bold]Bufferbloat Test[/bold]")
    console.print(f"Target: {host}")
    console.print(f"Baseline: {baseline_duration}s, Load test: {load_duration}s")
    console.print()
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("Testing bufferbloat (this generates network traffic)...", total=None)
        result = test_bufferbloat(
            host=host,
            baseline_duration=baseline_duration,
            load_duration=load_duration,
            include_upload=include_upload,
        )
        progress.remove_task(task)
    
    # Display grade prominently
    grade_colors = {"A": "green", "B": "green", "C": "yellow", "D": "red", "F": "red", "?": "white"}
    color = grade_colors.get(result.grade, "white")
    console.print(f"\n[bold]Bufferbloat Grade: [{color}]{result.grade}[/{color}][/bold]")
    console.print(f"Latency increase under load: {result.bloat_increase_ms}ms")
    
    reporter.report({"bufferbloat": result.to_dict()})


@app.command()
def monitor(
    output: Annotated[OutputFormat, typer.Option("--output", "-o", help="Output format")] = OutputFormat.console,
    output_dir: Annotated[Optional[Path], typer.Option("--output-dir", "-d", help="Output directory for CSV")] = None,
    host: Annotated[str, typer.Option("--host", help="Target host")] = "1.1.1.1",
    duration: Annotated[int, typer.Option("--duration", "-t", help="Duration in minutes")] = 60,
    interval: Annotated[float, typer.Option("--interval", help="Ping interval in seconds")] = 1.0,
):
    """
    Run long-duration monitoring (60+ minutes recommended).
    
    Logs ping statistics over time to detect intermittent issues.
    Use during gaming sessions or peak usage times.
    """
    reporter = _get_reporter(output)
    
    console.print("[bold]Long-Duration Monitoring[/bold]")
    console.print(f"Target: {host}")
    console.print(f"Duration: {duration} minutes")
    console.print(f"Ping interval: {interval}s")
    console.print()
    console.print("[yellow]Press Ctrl+C to stop early[/yellow]")
    console.print()
    
    # Setup CSV output
    csv_path = None
    if output_dir:
        output_dir.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        csv_path = output_dir / f"monitor_{timestamp}.csv"
    
    def progress_callback(elapsed: int, total: int):
        pct = (elapsed / total) * 100
        mins_elapsed = elapsed // 60
        mins_total = total // 60
        console.print(f"\r[{mins_elapsed}/{mins_total} min] {pct:.1f}% complete", end="")
    
    try:
        result = long_monitor(
            host=host,
            duration_minutes=duration,
            ping_interval=interval,
            output_csv=csv_path,
            progress_callback=progress_callback,
        )
        console.print()  # New line after progress
        
    except KeyboardInterrupt:
        console.print("\n[yellow]Monitoring stopped by user[/yellow]")
        return
    
    # Display summary
    console.print()
    console.print(f"[bold]Monitoring Complete[/bold]")
    console.print(f"Samples: {result.total_samples} ({result.total_successes} successful)")
    console.print(f"Loss: {result.overall_loss_percent}%")
    console.print(f"Latency - Avg: {result.overall_avg_ms}ms, P95: {result.overall_p95_ms}ms, P99: {result.overall_p99_ms}ms")
    console.print(f"Jitter: {result.overall_jitter_ms}ms")
    console.print(f"Spikes (>2x median): {result.spike_count}")
    
    if csv_path:
        console.print(f"\n[green]Raw data saved to: {csv_path}[/green]")
    
    reporter.report({"monitor": result.to_dict()})


@app.command(name="network-info")
def network_info(
    output: Annotated[OutputFormat, typer.Option("--output", "-o", help="Output format")] = OutputFormat.console,
    traceroute: Annotated[bool, typer.Option("--traceroute/--no-traceroute", help="Include traceroute")] = True,
    traceroute_host: Annotated[str, typer.Option("--traceroute-host", help="Host for traceroute")] = "8.8.8.8",
):
    """
    Capture network information (IP, gateway, DNS, interface type).
    
    Useful for detecting CGNAT, path changes, or WiFi vs Ethernet issues.
    """
    reporter = _get_reporter(output)
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("Capturing network info...", total=None)
        info = capture_network_info(
            include_traceroute=traceroute,
            traceroute_host=traceroute_host,
        )
        progress.remove_task(task)
    
    console.print("[bold]Network Information[/bold]")
    console.print(f"  Public IP: {info.public_ip or 'Unknown'}")
    console.print(f"  ISP: {info.isp or 'Unknown'}")
    console.print(f"  Local IP: {info.local_ip or 'Unknown'}")
    console.print(f"  Gateway: {info.default_gateway or 'Unknown'}")
    console.print(f"  DNS Servers: {', '.join(info.dns_servers) if info.dns_servers else 'Unknown'}")
    console.print(f"  Interface: {info.interface_type or 'Unknown'}")
    
    if info.traceroute_hops:
        console.print(f"\n[bold]First {len(info.traceroute_hops)} hops:[/bold]")
        for hop in info.traceroute_hops:
            ip = hop.get('ip') or '*'
            rtt = hop.get('rtt_ms')
            rtt_str = f"{rtt}ms" if rtt else "-"
            console.print(f"  {hop['hop']}. {ip} ({rtt_str})")
    
    reporter.report({"network_info": info.to_dict()})


@app.command()
def ui(
    port: Annotated[int, typer.Option("--port", "-p", help="Port to run server on")] = 8765,
    host: Annotated[str, typer.Option("--host", "-h", help="Host to bind to")] = "127.0.0.1",
    no_browser: Annotated[bool, typer.Option("--no-browser", help="Don't open browser automatically")] = False,
):
    """Launch web-based diagnostic dashboard."""
    from netspecs.web.server import run_server
    
    console.print(f"[bold]Starting Netspecs Dashboard[/bold]")
    console.print(f"Server: http://{host}:{port}")
    if not no_browser:
        console.print("Opening browser...")
    console.print("[yellow]Press Ctrl+C to stop[/yellow]")
    console.print()
    
    try:
        run_server(host=host, port=port, open_browser=not no_browser)
    except KeyboardInterrupt:
        console.print("\n[yellow]Server stopped[/yellow]")


@app.command()
def config(
    show: Annotated[bool, typer.Option("--show", help="Show current configuration")] = False,
):
    """Manage configuration."""
    if show:
        cfg = load_config()
        console.print("[bold]Current Configuration:[/bold]")
        console.print(f"  Model: {cfg.model}")
        console.print(f"  API Key: {'[set]' if cfg.api_key else '[not set]'}")
        console.print(f"  Output Directory: {cfg.output_dir}")
        console.print(f"  Output Format: {cfg.output_format}")
        console.print(f"  Endpoints: {len(cfg.endpoints)} configured")
        for ep in cfg.endpoints[:5]:
            console.print(f"    - {ep}")
        if len(cfg.endpoints) > 5:
            console.print(f"    ... and {len(cfg.endpoints) - 5} more")
    else:
        console.print("Use --show to display current configuration")
        console.print("Configuration is loaded from .env.local or environment variables")


def _get_reporter(output_format: OutputFormat):
    """Get the appropriate reporter for the output format."""
    if output_format == OutputFormat.json:
        return JSONReporter()
    elif output_format == OutputFormat.csv:
        return CSVReporter()
    else:
        return ConsoleReporter()


def _generate_ai_report(results: dict, config):
    """Generate AI diagnostic report."""
    from netspecs.agent.analyst import generate_diagnostic_report
    
    if not config.api_key:
        console.print("[yellow]Warning: No API key configured for AI report[/yellow]")
        console.print("Set OPENAI_API_KEY environment variable or use --api-key option")
        return
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("Generating AI report...", total=None)
        report = generate_diagnostic_report(results, model=config.model, api_key=config.api_key)
        progress.remove_task(task)
    
    console.print()
    console.print("[bold]AI Diagnostic Report[/bold]")
    console.print("-" * 40)
    console.print(report)


if __name__ == "__main__":
    app()

