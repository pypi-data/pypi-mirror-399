#!/usr/bin/env python3
"""Benchmark latency for different bundle delivery methods.

Compares:
1. R2 via Worker (current: CLI → Worker → R2 → Container curl)
2. Presigned URL (proposed: CLI → R2 direct → Container curl)
3. mountBucket (FUSE streaming, production only)

Run with: uv run python tests/benchmark_latency.py
"""

import io
import os
import sys
import time
import zipfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import httpx
from vmux.config import load_config


def create_test_bundle(size_mb: float) -> bytes:
    """Create a test zip bundle of approximately the given size."""
    target_bytes = int(size_mb * 1024 * 1024)
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_STORED) as zf:
        zf.writestr("test.py", 'print("Hello from benchmark!")\n')
        filler_chunk = b"X" * (1024 * 1024)
        chunks_needed = (target_bytes - buf.tell()) // len(filler_chunk)
        for i in range(max(0, chunks_needed)):
            zf.writestr(f"filler/data_{i:04d}.bin", filler_chunk)
    return buf.getvalue()


def benchmark_r2_via_worker(client: httpx.Client, headers: dict, bundle_bytes: bytes) -> dict:
    """Benchmark: CLI → Worker → R2 → Container curl."""
    results = {}

    # Step 1: Upload to R2 via Worker
    t0 = time.time()
    upload_resp = client.post(
        "/bundles/upload",
        content=bundle_bytes,
        headers={**headers, "Content-Type": "application/octet-stream"},
        timeout=300.0,
    )
    upload_resp.raise_for_status()
    bundle_id = upload_resp.json()["bundle_id"]
    results["upload_time"] = time.time() - t0

    # Step 2: Start job (container will curl from Worker)
    t1 = time.time()
    payload = {
        "command": "ls -la /workspace && echo done",
        "bundle_id": bundle_id,
        "env_vars": {},
        "editables": [],
        "ports": [],
    }

    job_id = None
    with client.stream(
        "POST", "/run", json=payload,
        headers={**headers, "Accept": "text/event-stream"},
        timeout=300.0,
    ) as response:
        response.raise_for_status()
        for line in response.iter_lines():
            if line.startswith("data: "):
                data = line[6:]
                if data == "[DONE]":
                    break
                import json
                try:
                    event = json.loads(data)
                    if "job_id" in event:
                        job_id = event["job_id"]
                    if event.get("status") == "running":
                        results["container_fetch_time"] = time.time() - t1
                        break
                except json.JSONDecodeError:
                    pass

    results["total_time"] = time.time() - t0
    results["job_id"] = job_id

    # Cleanup
    if job_id:
        try:
            client.delete(f"/jobs/{job_id}", headers=headers)
        except Exception:
            pass

    return results


def main():
    config = load_config()
    client = httpx.Client(
        base_url=config.api_url,
        timeout=httpx.Timeout(300.0, connect=60.0),
    )
    headers = {"Content-Type": "application/json"}
    if config.auth_token:
        headers["Authorization"] = f"Bearer {config.auth_token}"

    print("=" * 70)
    print("BUNDLE DELIVERY LATENCY BENCHMARK")
    print("=" * 70)
    print(f"API: {config.api_url}\n")

    # Test sizes
    sizes = [10, 30, 50, 63, 80]

    print("Method: R2 via Worker (CLI → Worker → R2 → Container curl)")
    print("-" * 70)
    print(f"{'Size':>8} | {'Upload':>10} | {'Fetch+Extract':>14} | {'Total':>10}")
    print("-" * 70)

    for size_mb in sizes:
        print(f"{size_mb:>6}MB | ", end="", flush=True)
        bundle = create_test_bundle(size_mb)

        try:
            results = benchmark_r2_via_worker(client, headers, bundle)
            upload = results.get("upload_time", 0)
            fetch = results.get("container_fetch_time", 0)
            total = results.get("total_time", 0)
            print(f"{upload:>8.1f}s | {fetch:>12.1f}s | {total:>8.1f}s")
        except Exception as e:
            print(f"ERROR: {e}")

    print()
    print("=" * 70)
    print("LATENCY BREAKDOWN ANALYSIS")
    print("=" * 70)
    print("""
R2 via Worker (current implementation):
  1. CLI → Worker: HTTP POST with raw bytes
  2. Worker → R2: env.BUNDLES.put()
  3. Return bundle_id to CLI
  4. CLI → Worker: POST /run with bundle_id
  5. Container → Worker: curl https://worker/bundles/{id}
  6. Worker → R2: env.BUNDLES.get()
  7. Worker → Container: stream response
  8. Container: unzip + run

  Bottleneck: Steps 5-7 (container fetches through worker proxy)

Presigned URL (proposed):
  1. CLI → Worker: GET /bundles/presign
  2. Worker: generates presigned PUT URL
  3. CLI → R2 DIRECT: PUT to presigned URL (bypasses worker!)
  4. CLI → Worker: POST /run with bundle_id
  5. Container → R2 DIRECT: curl presigned GET URL (bypasses worker!)
  6. Container: unzip + run

  Benefit: No worker in data path for upload OR download
  Expected: ~30-50% faster for large bundles

mountBucket (FUSE streaming):
  1. Pre-populate R2 bucket with bundle
  2. Container: sandbox.mountBucket() - FUSE mount
  3. Container: Files accessed on-demand (no full download)
  4. Container: unzip from mount or access files directly

  Benefit: No upfront transfer, streaming access
  Tradeoff: Higher per-file latency (network roundtrip per read)
  Best for: Very large datasets where you don't need all files
""")

    client.close()


if __name__ == "__main__":
    main()
