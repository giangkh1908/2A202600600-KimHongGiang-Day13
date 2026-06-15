import argparse
import concurrent.futures
import json
import time
from statistics import mean
from pathlib import Path

import httpx

BASE_URL = "http://127.0.0.1:8000"
QUERIES = Path("data/sample_queries.jsonl")


def send_request(client: httpx.Client, payload: dict, results: list) -> None:
    try:
        start = time.perf_counter()
        r = client.post(f"{BASE_URL}/chat", json=payload)
        latency = (time.perf_counter() - start) * 1000
        data = r.json()
        cid = data.get("correlation_id", "NONE")
        print(f"[{r.status_code}] {cid} | {payload['feature']} | {latency:.1f}ms")
        results.append({"status": r.status_code, "cid": cid, "latency_ms": latency, "feature": payload["feature"]})
    except Exception as e:
        print(f"Error: {e}")
        results.append({"status": 0, "cid": "ERROR", "latency_ms": 0, "feature": payload.get("feature", "?")})


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--concurrency", type=int, default=1, help="Number of concurrent requests")
    args = parser.parse_args()

    lines = [line for line in QUERIES.read_text(encoding="utf-8").splitlines() if line.strip()]
    results: list[dict] = []
    
    with httpx.Client(timeout=30.0) as client:
        if args.concurrency > 1:
            with concurrent.futures.ThreadPoolExecutor(max_workers=args.concurrency) as executor:
                futures = [executor.submit(send_request, client, json.loads(line), results) for line in lines]
                concurrent.futures.wait(futures)
        else:
            for line in lines:
                send_request(client, json.loads(line), results)

    print("\n--- Summary ---")
    latencies = [r["latency_ms"] for r in results if r["status"] == 200]
    cids = [r["cid"] for r in results if r["cid"] not in ("NONE", "ERROR")]
    print(f"Total requests: {len(results)}")
    print(f"Successful: {len(latencies)}")
    print(f"Avg latency: {mean(latencies):.1f}ms" if latencies else "N/A")
    print(f"Unique correlation IDs: {len(set(cids))}")
    print(f"Features tested: {set(r['feature'] for r in results)}")


if __name__ == "__main__":
    main()
