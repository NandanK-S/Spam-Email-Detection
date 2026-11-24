"""
run_load_test.py — Phase 5: Performance & Load Testing Suite

Measures:
1. Memory allocation across payload sizes using Python tracemalloc
2. Throughput, error rates, and latency percentiles (min, avg, median, p90, p95, p99, max)
   across configurable concurrent virtual user scenarios (10, 50, 100)
3. Endpoint profiles for /api/predict, /api/blockchain/log, and /api/blockchain/verify
"""

import sys
import os
import time
import statistics
import tracemalloc
from concurrent.futures import ThreadPoolExecutor
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend import app
import backend
from blockchain import Blockchain
from inference import predict_email


def profile_memory_usage():
    """Measure peak memory and allocation for different email input sizes."""
    print("\n" + "=" * 70)
    print("1. MEMORY PROFILING (tracemalloc) — Input Size Scaling")
    print("=" * 70)

    sizes = [
        ("Small (100 bytes)", "This is a brief update regarding tomorrow's scheduled team sync. See you all at ten."),
        ("Medium (1 KB)", ("Subject: Monthly Project Report\nDear team, please find attached the weekly summary. " * 12)[:1000]),
        ("Large (10 KB)", ("URGENT: Verify your account credentials immediately at http://security-update-fake.com " * 120)[:10000]),
        ("Max Boundary (50 KB)", ("Confidential notification: Review transaction records before the deadline today. " * 700)[:50000]),
    ]

    print(f"{'Payload Size':<24s} {'Peak Memory (KB)':>18s} {'Execution Time (ms)':>22s}")
    print("-" * 70)

    for label, payload in sizes:
        tracemalloc.start()
        start_time = time.perf_counter()
        
        result = predict_email(payload)
        
        elapsed_ms = (time.perf_counter() - start_time) * 1000
        current, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()

        print(f"{label:<24s} {peak / 1024:>18.2f} {elapsed_ms:>22.2f}")


def run_concurrency_test(client: TestClient, scenario_name: str, endpoint: str, method: str, payload_fn, num_requests: int, concurrency: int):
    """Execute concurrent requests and capture real latency distributions."""
    latencies = []
    errors = 0
    start_suite = time.perf_counter()

    def single_worker(worker_id):
        nonlocal errors
        req_start = time.perf_counter()
        try:
            if method == "POST":
                res = client.post(endpoint, json=payload_fn(worker_id))
            else:
                res = client.get(endpoint)
            req_duration = (time.perf_counter() - req_start) * 1000  # ms
            if res.status_code == 200:
                latencies.append(req_duration)
            else:
                errors += 1
        except Exception:
            errors += 1

    with ThreadPoolExecutor(max_workers=concurrency) as executor:
        futures = [executor.submit(single_worker, i) for i in range(num_requests)]
        for f in futures:
            f.result()

    total_time = time.perf_counter() - start_suite
    rps = len(latencies) / total_time if total_time > 0 else 0

    if not latencies:
        print(f"❌ {scenario_name}: All requests failed.")
        return

    latencies.sort()
    avg_lat = statistics.mean(latencies)
    median_lat = statistics.median(latencies)
    p90 = latencies[int(len(latencies) * 0.90)]
    p95 = latencies[int(len(latencies) * 0.95)]
    p99 = latencies[min(int(len(latencies) * 0.99), len(latencies) - 1)]
    min_lat = min(latencies)
    max_lat = max(latencies)
    error_rate = (errors / num_requests) * 100

    print(f"\n📊 Scenario: {scenario_name}")
    print(f"   Total Requests: {num_requests} | Concurrency: {concurrency} workers")
    print(f"   Throughput:     {rps:.2f} req/sec | Total Duration: {total_time:.2f}s")
    print(f"   Error Rate:     {error_rate:.1f}% ({errors} errors)")
    print(f"   Latency (ms):   Min: {min_lat:.1f} | Avg: {avg_lat:.1f} | Med: {median_lat:.1f}")
    print(f"   Percentiles:    p90: {p90:.1f}ms | p95: {p95:.1f}ms | p99: {p99:.1f}ms | Max: {max_lat:.1f}ms")

    return {
        "scenario": scenario_name,
        "concurrency": concurrency,
        "requests": num_requests,
        "rps": round(rps, 2),
        "error_rate": round(error_rate, 2),
        "min": round(min_lat, 2),
        "avg": round(avg_lat, 2),
        "median": round(median_lat, 2),
        "p90": round(p90, 2),
        "p95": round(p95, 2),
        "p99": round(p99, 2),
        "max": round(max_lat, 2),
    }


def main():
    print("=" * 70)
    print("🚀 PHASE 5: PERFORMANCE & LOAD TESTING EXECUTION")
    print("=" * 70)
    print(f"Timestamp: {time.strftime('%Y-%m-%d %H:%M:%S UTC', time.gmtime())}")
    print(f"Python:    {sys.version.split()[0]}")

    # 1. Memory Profiling
    profile_memory_usage()

    # 2. Concurrency Scenarios
    print("\n" + "=" * 70)
    print("2. CONCURRENT LOAD SCENARIOS")
    print("=" * 70)

    # Initialize client in isolated environment
    with TestClient(app) as client:
        # Predict endpoint at 10, 50, 100 concurrent workers
        run_concurrency_test(
            client=client,
            scenario_name="POST /api/predict (10 Virtual Users)",
            endpoint="/api/predict",
            method="POST",
            payload_fn=lambda idx: {"text": f"Performance verification test message #{idx} with standard length."},
            num_requests=50,
            concurrency=10,
        )

        run_concurrency_test(
            client=client,
            scenario_name="POST /api/predict (50 Virtual Users)",
            endpoint="/api/predict",
            method="POST",
            payload_fn=lambda idx: {"text": f"Performance verification test message #{idx} with urgency and links http://example.com."},
            num_requests=100,
            concurrency=50,
        )

        run_concurrency_test(
            client=client,
            scenario_name="POST /api/predict (100 Virtual Users)",
            endpoint="/api/predict",
            method="POST",
            payload_fn=lambda idx: {"text": f"Load test message #{idx} evaluating sustained throughput under high concurrency."},
            num_requests=200,
            concurrency=100,
        )

        # Blockchain Log endpoint (Read heavy)
        run_concurrency_test(
            client=client,
            scenario_name="GET /api/blockchain/log (50 Virtual Users)",
            endpoint="/api/blockchain/log",
            method="GET",
            payload_fn=lambda idx: None,
            num_requests=150,
            concurrency=50,
        )

        # Blockchain Verify endpoint
        run_concurrency_test(
            client=client,
            scenario_name="POST /api/blockchain/verify (50 Virtual Users)",
            endpoint="/api/blockchain/verify",
            method="POST",
            payload_fn=lambda idx: {"simulate_tamper": False},
            num_requests=100,
            concurrency=50,
        )

    print("\n" + "=" * 70)
    print("✅ Performance and load test suite execution complete.")
    print("=" * 70)


if __name__ == "__main__":
    main()

