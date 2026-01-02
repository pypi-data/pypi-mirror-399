"""JSON reporter for netspecs."""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Optional

from rich.console import Console


class JSONReporter:
    """Reporter that outputs results as JSON."""
    
    def __init__(self):
        self.console = Console()
    
    def report(self, results: dict, output_dir: Optional[Path] = None):
        """
        Output results as JSON.
        
        Args:
            results: Dictionary of test results
            output_dir: If provided, save to file in this directory
        """
        # Add metadata
        output = {
            "metadata": {
                "generated_at": datetime.now().isoformat(),
                "version": "netspecs",
            },
            "results": results,
        }
        
        json_str = json.dumps(output, indent=2, default=str)
        
        if output_dir:
            output_dir = Path(output_dir)
            output_dir.mkdir(parents=True, exist_ok=True)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = output_dir / f"diagnostic_{timestamp}.json"
            
            with open(output_file, "w") as f:
                f.write(json_str)
            
            self.console.print(f"[green]Results saved to: {output_file}[/green]")
        else:
            self.console.print(json_str)

