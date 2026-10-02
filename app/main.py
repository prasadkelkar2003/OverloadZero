import os
import time
import socket
import psycopg2
import redis
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

app = FastAPI(title="FlashShield Result Delivery Engine")

# Mount static directory for CSS/assets
os.makedirs("static", exist_ok=True)
os.makedirs("templates", exist_ok=True)
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

REDIS_HOST = os.getenv("REDIS_HOST", "redis-service")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
POD_NAME = socket.gethostname()

# Redis Client
try:
    cache = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True, socket_connect_timeout=2)
except Exception:
    cache = None

ops_metrics = {
    "requests_handled": 0,
    "cache_hits": 0,
    "cache_misses": 0
}

@app.get("/", response_class=HTMLResponse)
async def student_page(request: Request):
    """Page 1: Student Result Search Portal"""
    return templates.TemplateResponse("index.html", {"request": request, "pod": POD_NAME})

@app.get("/ops", response_class=HTMLResponse)
async def ops_dashboard(request: Request):
    """Page 2: DevOps / SRE Live Monitoring & Load Trigger Dashboard"""
    return templates.TemplateResponse("ops.html", {"request": request, "pod": POD_NAME})

@app.get("/api/result")
async def get_result(roll_no: str):
    start = time.time()
    ops_metrics["requests_handled"] += 1

    # 1. In-Memory Hot Path: Check Pre-warmed Redis Cache
    if cache:
        try:
            cached_data = cache.get(f"student:{roll_no}")
            if cached_data:
                ops_metrics["cache_hits"] += 1
                return {
                    "source": "REDIS_CACHE (L1)",
                    "latency_ms": round((time.time() - start) * 1000, 2),
                    "served_by_pod": POD_NAME,
                    "data": cached_data
                }
        except Exception:
            pass  # Fallback to DB if cache fails

    # 2. Cold Path: Fallback to DB simulation / PgBouncer
    ops_metrics["cache_misses"] += 1
    time.sleep(0.045)  # Simulate 45ms DB disk I/O & query latency
    mock_db_result = f"GPA: 8.85 | Status: CLEARED (Roll: {roll_no})"

    # Populate cache for subsequent hits
    if cache:
        try:
            cache.set(f"student:{roll_no}", mock_db_result, ex=300)
        except Exception:
            pass

    return {
        "source": "POSTGRES_DB_PGBOUNCER (Fallback)",
        "latency_ms": round((time.time() - start) * 1000, 2),
        "served_by_pod": POD_NAME,
        "data": mock_db_result
    }

@app.get("/api/ops/stats")
async def get_ops_stats():
    """Live metrics polled by SRE Dashboard"""
    return {
        "pod_name": POD_NAME,
        "total_requests": ops_metrics["requests_handled"],
        "cache_hits": ops_metrics["cache_hits"],
        "cache_misses": ops_metrics["cache_misses"]
    }
