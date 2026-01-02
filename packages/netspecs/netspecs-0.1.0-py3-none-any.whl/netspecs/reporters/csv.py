"""CSV reporter for netspecs."""

from __future__ import annotations

import csv
from datetime import datetime
from io import StringIO
from pathlib import Path
from typing import Optional

from rich.console import Console


class CSVReporter:
    """Reporter that outputs results as CSV files."""
    
    def __init__(self):
        self.console = Console()
    
    def report(self, results: dict, output_dir: Optional[Path] = None):
        """
        Output results as CSV files.
        
        Args:
            results: Dictionary of test results
            output_dir: Directory to save CSV files (required for CSV output)
        """
        if output_dir:
            output_dir = Path(output_dir)
            output_dir.mkdir(parents=True, exist_ok=True)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        else:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        files_created = []
        
        # Connectivity results
        if "connectivity" in results:
            csv_content = self._format_connectivity(results["connectivity"])
            if output_dir:
                file_path = output_dir / f"connectivity_{timestamp}.csv"
                self._save_csv(file_path, csv_content)
                files_created.append(file_path)
            else:
                self.console.print("[bold]Connectivity Results:[/bold]")
                self.console.print(csv_content)
        
        # Latency results
        if "latency" in results:
            csv_content = self._format_latency(results["latency"])
            if output_dir:
                file_path = output_dir / f"latency_{timestamp}.csv"
                self._save_csv(file_path, csv_content)
                files_created.append(file_path)
            else:
                self.console.print("[bold]Latency Results:[/bold]")
                self.console.print(csv_content)
        
        # Jitter results
        if "jitter" in results:
            csv_content = self._format_jitter(results["jitter"])
            if output_dir:
                file_path = output_dir / f"jitter_{timestamp}.csv"
                self._save_csv(file_path, csv_content)
                files_created.append(file_path)
            else:
                self.console.print("[bold]Jitter Results:[/bold]")
                self.console.print(csv_content)
        
        # Speed results
        if "speed" in results:
            csv_content = self._format_speed(results["speed"])
            if output_dir:
                file_path = output_dir / f"speed_{timestamp}.csv"
                self._save_csv(file_path, csv_content)
                files_created.append(file_path)
            else:
                self.console.print("[bold]Speed Results:[/bold]")
                self.console.print(csv_content)
        
        # Prioritization results
        if "prioritization" in results:
            csv_content = self._format_prioritization(results["prioritization"])
            if output_dir:
                file_path = output_dir / f"prioritization_{timestamp}.csv"
                self._save_csv(file_path, csv_content)
                files_created.append(file_path)
            else:
                self.console.print("[bold]Prioritization Results:[/bold]")
                self.console.print(csv_content)
        
        if files_created:
            self.console.print(f"[green]CSV files saved to: {output_dir}[/green]")
            for f in files_created:
                self.console.print(f"  - {f.name}")
    
    def _save_csv(self, path: Path, content: str):
        """Save CSV content to file."""
        with open(path, "w", newline="") as f:
            f.write(content)
    
    def _format_connectivity(self, results: list[dict]) -> str:
        """Format connectivity results as CSV."""
        output = StringIO()
        writer = csv.DictWriter(output, fieldnames=["host", "reachable", "response_time_ms", "error"])
        writer.writeheader()
        writer.writerows(results)
        return output.getvalue()
    
    def _format_latency(self, results: list[dict]) -> str:
        """Format latency results as CSV."""
        output = StringIO()
        fieldnames = [
            "host", "packets_sent", "packets_received", "packet_loss_percent",
            "min_ms", "avg_ms", "max_ms", "jitter_ms", "success", "error"
        ]
        writer = csv.DictWriter(output, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(results)
        return output.getvalue()
    
    def _format_jitter(self, results: list[dict]) -> str:
        """Format jitter results as CSV."""
        output = StringIO()
        fieldnames = [
            "host", "duration_seconds", "samples", "jitter_ms",
            "min_ms", "max_ms", "avg_ms", "std_dev_ms", "success", "error"
        ]
        writer = csv.DictWriter(output, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(results)
        return output.getvalue()
    
    def _format_speed(self, result: dict) -> str:
        """Format speed results as CSV."""
        output = StringIO()
        
        # HTTP tests
        if result.get("http_tests"):
            writer = csv.DictWriter(output, fieldnames=["name", "size_mb", "speed_mbps", "success"])
            writer.writeheader()
            writer.writerows(result["http_tests"])
            output.write("\n")
        
        # Summary
        summary_fields = [
            "http_download_mbps", "ookla_download_mbps", "ookla_upload_mbps",
            "ookla_ping_ms", "ookla_jitter_ms", "speed_difference_percent"
        ]
        output.write("metric,value\n")
        for field in summary_fields:
            if field in result and result[field] is not None:
                output.write(f"{field},{result[field]}\n")
        
        return output.getvalue()
    
    def _format_prioritization(self, result: dict) -> str:
        """Format prioritization results as CSV."""
        output = StringIO()
        
        # Phase results
        if result.get("phases"):
            writer = csv.DictWriter(
                output,
                fieldnames=["name", "avg_ms", "min_ms", "max_ms", "jitter_ms", "samples"]
            )
            writer.writeheader()
            writer.writerows(result["phases"])
            output.write("\n")
        
        # Summary
        output.write("metric,value\n")
        output.write(f"host,{result.get('host', '')}\n")
        output.write(f"baseline_avg_ms,{result.get('baseline_avg_ms', '')}\n")
        output.write(f"light_traffic_change_ms,{result.get('light_traffic_change_ms', '')}\n")
        output.write(f"medium_traffic_change_ms,{result.get('medium_traffic_change_ms', '')}\n")
        output.write(f"heavy_traffic_change_ms,{result.get('heavy_traffic_change_ms', '')}\n")
        output.write(f"throttling_detected,{result.get('throttling_detected', '')}\n")
        output.write(f"throttling_severity,{result.get('throttling_severity', '')}\n")
        
        return output.getvalue()

