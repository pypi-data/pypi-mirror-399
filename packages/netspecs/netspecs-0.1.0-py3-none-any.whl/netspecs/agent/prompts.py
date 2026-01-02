"""System prompts for the AI diagnostic agent."""

ANALYST_SYSTEM_PROMPT = """You are an expert network diagnostics analyst. Your role is to analyze internet connectivity test results and provide clear, actionable insights.

When analyzing results, you should:

1. **Summarize the Overall Health**: Start with a brief assessment of the connection's overall quality (Excellent, Good, Fair, Poor, Critical).

2. **Identify Key Issues**: Highlight any problems found in the tests:
   - High latency (>100ms to major endpoints)
   - Packet loss (>1% is concerning, >5% is problematic)
   - High jitter (>10ms can affect real-time applications, >30ms is problematic)
   - Speed issues (compare with expected speeds)
   - Throttling patterns (if detected)

3. **Explain the Impact**: Describe how identified issues might affect:
   - Web browsing
   - Video streaming
   - Video conferencing
   - Online gaming
   - File downloads/uploads

4. **Provide Recommendations**: Suggest specific actions to address issues:
   - Router/modem restart
   - Ethernet vs WiFi considerations
   - ISP contact recommendations
   - Time-of-day testing
   - Equipment upgrade suggestions

5. **Technical Details**: Include relevant technical observations for users who want deeper insights.

Format your response in clear sections with headers. Be concise but thorough. Avoid excessive technical jargon unless explaining a specific issue.

Do not make assumptions about the user's technical level - provide explanations that work for both technical and non-technical users.
"""

RESULTS_FORMAT_TEMPLATE = """
## Internet Connectivity Diagnostic Results

### Test Timestamp
{timestamp}

### Connectivity Summary
{connectivity_summary}

### Latency Results
{latency_results}

### Jitter Measurements
{jitter_results}

### Speed Test Results
{speed_results}

### Bandwidth Variability
{variability_results}

### Prioritization Detection
{prioritization_results}

Please analyze these results and provide a comprehensive diagnostic report.
"""


def format_results_for_analysis(results: dict) -> str:
    """
    Format test results into a structured prompt for the AI analyst.
    
    Args:
        results: Dictionary of test results
        
    Returns:
        Formatted string for the AI prompt
    """
    from datetime import datetime
    
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Format connectivity summary
    connectivity_summary = "Not tested"
    if "connectivity_summary" in results:
        cs = results["connectivity_summary"]
        connectivity_summary = (
            f"- Total hosts tested: {cs.get('total_hosts', 'N/A')}\n"
            f"- Reachable: {cs.get('reachable', 'N/A')}\n"
            f"- Unreachable: {cs.get('unreachable', 'N/A')}\n"
            f"- Success rate: {cs.get('success_rate', 'N/A')}%\n"
            f"- Average response time: {cs.get('avg_response_ms', 'N/A')} ms"
        )
    
    # Format latency results
    latency_results = "Not tested"
    if "latency" in results:
        latency_lines = []
        for r in results["latency"]:
            latency_lines.append(
                f"- {r['host']}: avg={r['avg_ms']}ms, "
                f"min/max={r['min_ms']}/{r['max_ms']}ms, "
                f"jitter={r['jitter_ms']}ms, "
                f"loss={r['packet_loss_percent']}%"
            )
        latency_results = "\n".join(latency_lines)
    
    # Format jitter results
    jitter_results = "Not tested"
    if "jitter" in results:
        jitter_lines = []
        for r in results["jitter"]:
            jitter_lines.append(
                f"- {r['host']}: jitter={r['jitter_ms']}ms, "
                f"range={r['min_ms']}-{r['max_ms']}ms, "
                f"samples={r['samples']}"
            )
        jitter_results = "\n".join(jitter_lines)
    
    # Format speed results
    speed_results = "Not tested"
    if "speed" in results:
        s = results["speed"]
        speed_lines = []
        
        if s.get("ookla_available"):
            speed_lines.append("Ookla Speedtest:")
            speed_lines.append(f"  - Download: {s.get('ookla_download_mbps')} Mbps")
            speed_lines.append(f"  - Upload: {s.get('ookla_upload_mbps')} Mbps")
            speed_lines.append(f"  - Ping: {s.get('ookla_ping_ms')} ms")
            speed_lines.append(f"  - Jitter: {s.get('ookla_jitter_ms')} ms")
        
        if s.get("http_download_mbps"):
            speed_lines.append(f"HTTP Download Average: {s.get('http_download_mbps')} Mbps")
        
        if s.get("speed_difference_percent") is not None:
            speed_lines.append(
                f"Ookla vs HTTP difference: {s.get('speed_difference_percent')}% "
                "(large difference may indicate throttling)"
            )
        
        speed_results = "\n".join(speed_lines) if speed_lines else "No speed data available"
    
    # Format variability results
    variability_results = "Not tested"
    if "bandwidth_variability" in results:
        v = results["bandwidth_variability"]
        if v.get("avg_mbps"):
            variability_results = (
                f"- Iterations: {v.get('successful', 0)}/{v.get('iterations', 0)}\n"
                f"- Min speed: {v.get('min_mbps')} Mbps\n"
                f"- Max speed: {v.get('max_mbps')} Mbps\n"
                f"- Average speed: {v.get('avg_mbps')} Mbps\n"
                f"- Variability: {v.get('variability_percent')}%"
            )
    
    # Format prioritization results
    prioritization_results = "Not tested"
    if "prioritization" in results:
        p = results["prioritization"]
        prio_lines = [
            f"- Target host: {p.get('host')}",
            f"- Baseline latency: {p.get('baseline_avg_ms')} ms",
        ]
        
        if p.get("light_traffic_change_ms") is not None:
            prio_lines.append(f"- Light traffic change: {p['light_traffic_change_ms']:+.1f} ms")
        if p.get("medium_traffic_change_ms") is not None:
            prio_lines.append(f"- Medium traffic change: {p['medium_traffic_change_ms']:+.1f} ms")
        if p.get("heavy_traffic_change_ms") is not None:
            prio_lines.append(f"- Heavy traffic change: {p['heavy_traffic_change_ms']:+.1f} ms")
        
        prio_lines.append(f"- Throttling detected: {p.get('throttling_detected', False)}")
        if p.get("throttling_detected"):
            prio_lines.append(f"- Severity: {p.get('throttling_severity', 'unknown')}")
        
        prioritization_results = "\n".join(prio_lines)
    
    return RESULTS_FORMAT_TEMPLATE.format(
        timestamp=timestamp,
        connectivity_summary=connectivity_summary,
        latency_results=latency_results,
        jitter_results=jitter_results,
        speed_results=speed_results,
        variability_results=variability_results,
        prioritization_results=prioritization_results,
    )

