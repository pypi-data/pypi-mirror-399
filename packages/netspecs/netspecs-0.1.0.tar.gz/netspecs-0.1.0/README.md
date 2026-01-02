# Netspecs <img src="./docs/assets/netspecs-hexicon-dark.png" align="right" width="224px" height="224px" />

Cross-platform internet diagnostics with AI-powered analysis.

Main Features:
- Comprehensive internet diagnostics
  - Connectivity testing
  - Latency measurement
  - Jitter measurement
  - Speed testing (HTTP and Ookla)
  - Throttling detection
  - Network information capture
  - Bandwidth variability analysis
- AI-powered diagnostic reports
- Cross-platform support (macOS, Linux, Windows)

## Installation

```bash
pip install netspecs
```

For development:

```bash
git clone https://github.com/colinconwell/NetSpecs.git
cd NetSpecs
pip install -e ".[dev]"
```

## Quick Start

```bash
# Run full diagnostic suite
netspecs run

# Individual tests
netspecs latency
netspecs speed
netspecs jitter
netspecs prioritization

# With AI analysis
netspecs run --ai-report --api-key YOUR_OPENAI_KEY

# Output formats
netspecs run --output json --output-dir ./results
netspecs run --output csv --output-dir ./results
```

## CLI Commands

| Command | Description |
|---------|-------------|
| `netspecs run` | Full diagnostic suite |
| `netspecs latency` | Test latency to endpoints |
| `netspecs speed` | Test download/upload speed |
| `netspecs jitter` | Measure latency variation |
| `netspecs prioritization` | Detect throttling patterns |
| `netspecs report FILE` | Generate AI report from results |
| `netspecs config --show` | Show configuration |

## Options

```bash
netspecs run --help

Options:
  --output, -o       Output format: console, json, csv
  --output-dir, -d   Directory to save results
  --endpoints, -e    Comma-separated test endpoints
  --skip-speed       Skip speed tests
  --skip-jitter      Skip jitter tests
  --ai-report        Generate AI diagnostic report
  --model, -m        LLM model (default: gpt-5.2)
  --api-key, -k      API key for AI reports
```

## Python API

```python
from netspecs.core.latency import test_latency
from netspecs.core.speed import test_speed
from netspecs.agent.analyst import generate_diagnostic_report

# Run tests
latency_result = test_latency("8.8.8.8", count=20)
speed_result = test_speed()

# Generate AI report
results = {
    "latency": [latency_result.to_dict()],
    "speed": speed_result.to_dict(),
}
report = generate_diagnostic_report(results, api_key="your-key")
print(report)
```

## Shell Scripts

Original shell scripts are available in `scripts/`:

```bash
# Bash (macOS/Linux)
./scripts/internet-test.sh
./scripts/prioritization-detector.sh

# PowerShell (Windows)
.\scripts\internet-test.ps1
```

## Documentation

Full documentation: https://colinconwell.github.io/NetSpecs
