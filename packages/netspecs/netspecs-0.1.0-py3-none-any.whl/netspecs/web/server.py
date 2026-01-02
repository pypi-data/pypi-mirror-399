"""FastAPI web server for netspecs dashboard."""

from __future__ import annotations

import asyncio
import json
import webbrowser
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from netspecs.core.connectivity import check_connectivity
from netspecs.core.jitter import measure_jitter
from netspecs.core.latency import test_latency
from netspecs.core.network_info import capture_network_info
from netspecs.core.speed import test_speed
from netspecs.utils.config import DEFAULT_ENDPOINTS

# Path to static files
STATIC_DIR = Path(__file__).parent / "static"


# Request models
class LatencyRequest(BaseModel):
    endpoints: Optional[list[str]] = None
    count: Optional[int] = 10


class JitterRequest(BaseModel):
    endpoint: Optional[str] = None
    duration: Optional[int] = 10


class SpeedRequest(BaseModel):
    include_ookla: Optional[bool] = True


class AIDiagnosticsRequest(BaseModel):
    model: Optional[str] = "gpt-4o-mini"
    custom_prompt: Optional[str] = None
    api_key: Optional[str] = None
    run_tests: Optional[dict] = None  # {"latency": True, "jitter": True, "network_info": True}
    use_existing: Optional[bool] = False
    existing_results: Optional[dict] = None


class ValidateKeyRequest(BaseModel):
    api_key: str


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    app = FastAPI(
        title="Netspecs Dashboard",
        description="Network diagnostics dashboard",
        version="0.1.0",
    )

    # CORS for local development
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Mount static files
    app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

    @app.get("/")
    async def index():
        """Serve the main dashboard page."""
        return FileResponse(STATIC_DIR / "index.html")

    @app.get("/api/status")
    async def get_status():
        """Quick connectivity check."""
        result = await asyncio.to_thread(check_connectivity, "1.1.1.1")
        return {
            "connected": result.success,
            "latency_ms": result.latency_ms,
            "endpoint": result.endpoint,
        }

    @app.post("/api/latency")
    async def run_latency_test(request: LatencyRequest = LatencyRequest()):
        """Run latency test."""
        hosts = request.endpoints or DEFAULT_ENDPOINTS[:5]
        count = request.count or 10
        results = []
        for host in hosts:
            result = await asyncio.to_thread(test_latency, host, count=count)
            results.append(result.to_dict())
        return {"results": results}

    @app.post("/api/speed")
    async def run_speed_test(request: SpeedRequest = SpeedRequest()):
        """Run speed test."""
        include_ookla = request.include_ookla if request.include_ookla is not None else True
        result = await asyncio.to_thread(test_speed, include_ookla=include_ookla)
        return {"result": result.to_dict()}

    @app.post("/api/jitter")
    async def run_jitter_test(request: JitterRequest = JitterRequest()):
        """Run jitter measurement."""
        host = request.endpoint or "1.1.1.1"
        duration = request.duration or 10
        result = await asyncio.to_thread(measure_jitter, host, duration=duration, interval=0.5)
        return {"result": result.to_dict()}

    @app.get("/api/network-info")
    async def get_network_info():
        """Get network information."""
        info = await asyncio.to_thread(
            capture_network_info, include_traceroute=False
        )
        return {"info": info.to_dict()}

    @app.get("/api/settings")
    async def get_settings():
        """Get server settings status."""
        from netspecs.utils.config import load_config
        config = load_config()
        return {
            "has_api_key": bool(config.api_key),
            "default_model": config.model or "gpt-4o-mini",
        }

    @app.post("/api/validate-key")
    async def validate_api_key(request: ValidateKeyRequest):
        """Validate an API key."""
        if not request.api_key:
            return {"valid": False, "message": "No API key provided"}
        
        try:
            import litellm
            # Try a minimal completion to validate the key
            response = await asyncio.to_thread(
                litellm.completion,
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": "Hi"}],
                max_tokens=1,
                api_key=request.api_key,
            )
            return {"valid": True, "message": "API key is valid"}
        except Exception as e:
            error_msg = str(e)
            if "invalid_api_key" in error_msg.lower() or "incorrect api key" in error_msg.lower():
                return {"valid": False, "message": "Invalid API key"}
            elif "quota" in error_msg.lower():
                return {"valid": True, "message": "API key valid (quota warning)"}
            else:
                return {"valid": False, "message": f"Validation error: {error_msg[:100]}"}

    @app.post("/api/ai-diagnostics")
    async def run_ai_diagnostics(request: AIDiagnosticsRequest = AIDiagnosticsRequest()):
        """Generate AI diagnostics report."""
        from netspecs.utils.config import load_config
        
        config = load_config()
        
        # Use provided API key or fall back to environment
        api_key = request.api_key or config.api_key
        
        if not api_key:
            return {"error": "No API key configured. Set OPENAI_API_KEY or provide one in settings."}
        
        # Determine which tests to run
        run_tests = request.run_tests or {"latency": True, "jitter": True, "network_info": True}
        
        # Use existing results if requested and available
        diagnostics = {}
        if request.use_existing and request.existing_results:
            for key, value in request.existing_results.items():
                if isinstance(value, dict) and "data" in value:
                    diagnostics[key.replace("-", "_")] = value["data"]
        
        try:
            # Run requested tests if not using existing results
            if run_tests.get("latency") and "latency" not in diagnostics:
                latency_result = await asyncio.to_thread(test_latency, "1.1.1.1", count=5)
                diagnostics["latency"] = [latency_result.to_dict()]
            
            if run_tests.get("network_info") and "network_info" not in diagnostics:
                net_info = await asyncio.to_thread(capture_network_info, include_traceroute=False)
                diagnostics["network_info"] = net_info.to_dict()
            
            if run_tests.get("jitter") and "jitter" not in diagnostics:
                jitter_result = await asyncio.to_thread(measure_jitter, "1.1.1.1", duration=5, interval=0.5)
                diagnostics["jitter"] = [jitter_result.to_dict()]
            
        except Exception as e:
            return {"error": f"Failed to gather diagnostics: {str(e)}"}
        
        # Generate AI report
        try:
            from netspecs.agent.analyst import generate_diagnostic_report
            
            model = request.model or config.model or "gpt-4o-mini"
            report = await asyncio.to_thread(
                generate_diagnostic_report,
                diagnostics,
                model=model,
                api_key=api_key,
                custom_prompt=request.custom_prompt,
            )
            return {"report": report, "diagnostics": diagnostics}
            
        except Exception as e:
            return {"error": f"Failed to generate AI report: {str(e)}"}

    @app.websocket("/ws/live")
    async def websocket_live(websocket: WebSocket):
        """WebSocket endpoint for live latency streaming."""
        await websocket.accept()
        try:
            while True:
                # Run a quick ping with minimal count for speed
                result = await asyncio.to_thread(test_latency, "1.1.1.1", count=1, timeout=2)
                from datetime import datetime
                data = {
                    "type": "ping",
                    "latency_ms": result.avg_ms if result.success else None,
                    "packet_loss": result.packet_loss_percent,
                    "success": result.success,
                    "timestamp": datetime.now().isoformat(),
                }
                await websocket.send_text(json.dumps(data))
                await asyncio.sleep(2)  # Ping every 2 seconds to avoid overwhelming
        except WebSocketDisconnect:
            pass
        except Exception as e:
            print(f"WebSocket error: {e}")
            try:
                await websocket.close()
            except Exception:
                pass

    return app


def run_server(
    host: str = "127.0.0.1",
    port: int = 8765,
    open_browser: bool = True,
) -> None:
    """Run the web server."""
    import uvicorn

    if open_browser:
        # Open browser after a short delay
        import threading

        def open_browser_delayed():
            import time
            time.sleep(1.5)
            webbrowser.open(f"http://{host}:{port}")

        threading.Thread(target=open_browser_delayed, daemon=True).start()

    uvicorn.run(
        create_app(),
        host=host,
        port=port,
        log_level="info",
    )

