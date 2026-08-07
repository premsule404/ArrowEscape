import time
import statistics
import concurrent.futures
from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.db.init_db import init_db

client = TestClient(app)

def setup_module(module):
    init_db()

def single_user_workflow(user_idx: int):
    latencies = []
    
    # 1. Health Check
    t0 = time.perf_counter()
    res1 = client.get("/api/v1/health")
    t1 = time.perf_counter()
    assert res1.status_code == 200
    latencies.append((t1 - t0) * 1000)
    
    # 2. Config API
    t0 = time.perf_counter()
    res2 = client.get("/api/v1/config")
    t1 = time.perf_counter()
    assert res2.status_code == 200
    latencies.append((t1 - t0) * 1000)
    
    # 3. Levels List
    t0 = time.perf_counter()
    res3 = client.get("/api/v1/levels")
    t1 = time.perf_counter()
    assert res3.status_code == 200
    latencies.append((t1 - t0) * 1000)
    
    # 4. Guest Auth & Cloud Sync
    t0 = time.perf_counter()
    auth_res = client.post("/api/v1/auth/guest", json={"display_name": f"PerfUser_{user_idx}"})
    t1 = time.perf_counter()
    assert auth_res.status_code == 200
    latencies.append((t1 - t0) * 1000)
    
    token = auth_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    t0 = time.perf_counter()
    sync_res = client.post("/api/v1/cloud/sync", json={
        "levels": [{"level_id": 1, "stars": 3, "moves": 5, "time": 10.0, "base_coins": 100, "completed": True}]
    }, headers=headers)
    t1 = time.perf_counter()
    assert sync_res.status_code == 200
    latencies.append((t1 - t0) * 1000)
    
    return latencies

def test_load_and_latency_benchmarks():
    num_concurrent_users = 20
    all_latencies = []
    
    start_time = time.perf_counter()
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
        futures = [executor.submit(single_user_workflow, i) for i in range(num_concurrent_users)]
        for future in concurrent.futures.as_completed(futures):
            all_latencies.extend(future.result())
    total_duration = time.perf_counter() - start_time
    
    sorted_latencies = sorted(all_latencies)
    total_requests = len(sorted_latencies)
    p50 = sorted_latencies[int(total_requests * 0.50)]
    p95 = sorted_latencies[int(total_requests * 0.95)]
    p99 = sorted_latencies[int(total_requests * 0.99)]
    rps = total_requests / total_duration
    
    print(f"\n============================================================")
    print(f"[PERFORMANCE BENCHMARK RESULTS]")
    print(f"Total Virtual Users: {num_concurrent_users}")
    print(f"Total API Requests:  {total_requests}")
    print(f"Throughput (RPS):    {rps:.2f} req/sec")
    print(f"p50 Latency:         {p50:.2f} ms")
    print(f"p95 Latency:         {p95:.2f} ms")
    print(f"p99 Latency:         {p99:.2f} ms")
    print(f"============================================================")
    
    # SLA Assertions
    assert p50 < 1000.0, f"p50 latency ({p50:.2f}ms) exceeded SLA threshold of 1000ms"
    assert p95 < 2500.0, f"p95 latency ({p95:.2f}ms) exceeded SLA threshold of 2500ms"
