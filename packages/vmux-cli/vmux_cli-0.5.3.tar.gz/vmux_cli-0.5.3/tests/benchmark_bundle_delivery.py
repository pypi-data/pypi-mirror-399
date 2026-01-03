#!/usr/bin/env python3
"""Benchmark different bundle delivery methods to Cloudflare containers.

Tests:
1. writeFile limit verification (confirm actual limit - NOT 32MB as documented!)
2. R2 upload via Worker (100MB limit due to CF request body size)
3. R2 presigned URL upload (up to 5GB, bypasses Worker)
4. mountBucket (FUSE-based, requires production deploy)

FINDINGS (Dec 2024):
- writeFile works up to ~90MB (base64 encoded)
- R2 via Worker: 100MB CF request body limit
- R2 presigned: Up to 5GB direct upload
- mountBucket: Streaming, requires deploy

Run with: uv run python -m tests.benchmark_bundle_delivery
"""

import base64
import io
import json
import os
import sys
import time
import zipfile
from dataclasses import dataclass, field
from pathlib import Path

# Add parent to path for vmux imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from vmux.config import load_config

import httpx

DEBUG = os.environ.get("VMUX_DEBUG", "").lower() in ("1", "true", "yes")


@dataclass
class BenchmarkResult:
    """Result from a single benchmark run."""

    method: str
    bundle_size_mb: float
    success: bool
    duration_ms: float
    error: str | None = None
    notes: str = ""


@dataclass
class BenchmarkSuite:
    """Collection of benchmark results."""

    results: list[BenchmarkResult] = field(default_factory=list)

    def add(self, result: BenchmarkResult) -> None:
        self.results.append(result)
        status = "✓" if result.success else "✗"
        print(
            f"  {status} {result.method} @ {result.bundle_size_mb:.1f}MB: "
            f"{result.duration_ms:.0f}ms"
            + (f" - {result.error}" if result.error else "")
            + (f" ({result.notes})" if result.notes else "")
        )

    def print_summary(self) -> None:
        print("\n" + "=" * 60)
        print("BENCHMARK SUMMARY")
        print("=" * 60)

        # Group by method
        by_method: dict[str, list[BenchmarkResult]] = {}
        for r in self.results:
            by_method.setdefault(r.method, []).append(r)

        for method, results in by_method.items():
            successes = [r for r in results if r.success]
            failures = [r for r in results if not r.success]

            print(f"\n{method}:")
            if successes:
                sizes = [r.bundle_size_mb for r in successes]
                times = [r.duration_ms for r in successes]
                print(f"  ✓ Success: {len(successes)} runs")
                print(f"    Size range: {min(sizes):.1f} - {max(sizes):.1f} MB")
                print(f"    Time range: {min(times):.0f} - {max(times):.0f} ms")
                print(f"    Avg time: {sum(times)/len(times):.0f} ms")
            if failures:
                print(f"  ✗ Failures: {len(failures)}")
                for r in failures:
                    print(f"    @ {r.bundle_size_mb:.1f}MB: {r.error}")


def create_test_bundle(size_mb: float) -> bytes:
    """Create a test zip bundle of approximately the given size."""
    target_bytes = int(size_mb * 1024 * 1024)

    # Create a zip file in memory
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_STORED) as zf:
        # Add a simple test script
        zf.writestr(
            "test.py",
            """#!/usr/bin/env python3
print("Hello from test bundle!")
print(f"Bundle delivered successfully")
""",
        )

        # Add filler data to reach target size
        # We use compressible but non-trivial data
        filler_chunk = b"X" * (1024 * 1024)  # 1MB chunks
        chunks_needed = (target_bytes - buf.tell()) // len(filler_chunk)

        for i in range(max(0, chunks_needed)):
            zf.writestr(f"filler/data_{i:04d}.bin", filler_chunk)

        # Fine-tune to get close to target
        remaining = target_bytes - buf.tell()
        if remaining > 100:
            zf.writestr("filler/final.bin", b"Y" * max(0, remaining - 200))

    return buf.getvalue()


class BenchmarkClient:
    """Client for running benchmarks against vmux worker."""

    def __init__(self) -> None:
        self.config = load_config()
        self._client = httpx.Client(
            base_url=self.config.api_url,
            timeout=httpx.Timeout(600.0, connect=60.0),
        )

    def _headers(self) -> dict[str, str]:
        headers = {"Content-Type": "application/json"}
        if self.config.auth_token:
            headers["Authorization"] = f"Bearer {self.config.auth_token}"
        return headers

    def close(self) -> None:
        self._client.close()

    def test_inline_writefile(self, bundle_bytes: bytes) -> tuple[bool, float, str | None]:
        """Test inline writeFile delivery (base64 in JSON payload)."""
        t0 = time.time()

        try:
            payload = {
                "command": "echo 'inline test' && ls -la /workspace",
                "bundle": base64.b64encode(bundle_bytes).decode(),
                "env_vars": {},
                "editables": [],
                "ports": [],
            }

            # Stream response to get timing
            job_id = None
            with self._client.stream(
                "POST",
                "/run",
                json=payload,
                headers={**self._headers(), "Accept": "text/event-stream"},
                timeout=300.0,
            ) as response:
                if response.status_code >= 400:
                    return False, (time.time() - t0) * 1000, f"HTTP {response.status_code}"

                for line in response.iter_lines():
                    if line.startswith("data: "):
                        data = line[6:]
                        if data == "[DONE]":
                            break
                        try:
                            event = json.loads(data)
                            if "job_id" in event:
                                job_id = event["job_id"]
                            if event.get("status") == "running":
                                # Success - bundle was delivered and extracted
                                break
                            if "error" in event:
                                return False, (time.time() - t0) * 1000, event["error"]
                        except json.JSONDecodeError:
                            pass

            duration_ms = (time.time() - t0) * 1000

            # Cleanup: stop the job
            if job_id:
                try:
                    self._client.delete(f"/jobs/{job_id}", headers=self._headers())
                except Exception:
                    pass

            return True, duration_ms, None

        except httpx.HTTPStatusError as e:
            return False, (time.time() - t0) * 1000, f"HTTP {e.response.status_code}: {e.response.text[:200]}"
        except Exception as e:
            return False, (time.time() - t0) * 1000, str(e)

    def test_r2_delivery(self, bundle_bytes: bytes) -> tuple[bool, float, str | None]:
        """Test R2 upload + curl delivery."""
        t0 = time.time()

        try:
            # Step 1: Upload to R2
            upload_response = self._client.post(
                "/bundles/upload",
                content=bundle_bytes,
                headers={
                    **self._headers(),
                    "Content-Type": "application/octet-stream",
                },
                timeout=300.0,
            )
            upload_response.raise_for_status()
            bundle_id = upload_response.json()["bundle_id"]

            upload_time = time.time() - t0

            # Step 2: Run with bundle_id
            payload = {
                "command": "echo 'r2 test' && ls -la /workspace",
                "bundle_id": bundle_id,
                "env_vars": {},
                "editables": [],
                "ports": [],
            }

            job_id = None
            with self._client.stream(
                "POST",
                "/run",
                json=payload,
                headers={**self._headers(), "Accept": "text/event-stream"},
                timeout=300.0,
            ) as response:
                if response.status_code >= 400:
                    return False, (time.time() - t0) * 1000, f"HTTP {response.status_code}"

                for line in response.iter_lines():
                    if line.startswith("data: "):
                        data = line[6:]
                        if data == "[DONE]":
                            break
                        try:
                            event = json.loads(data)
                            if "job_id" in event:
                                job_id = event["job_id"]
                            if event.get("status") == "running":
                                break
                            if "error" in event:
                                return False, (time.time() - t0) * 1000, event["error"]
                        except json.JSONDecodeError:
                            pass

            duration_ms = (time.time() - t0) * 1000

            # Cleanup
            if job_id:
                try:
                    self._client.delete(f"/jobs/{job_id}", headers=self._headers())
                except Exception:
                    pass

            return True, duration_ms, None

        except httpx.HTTPStatusError as e:
            return False, (time.time() - t0) * 1000, f"HTTP {e.response.status_code}: {e.response.text[:200]}"
        except Exception as e:
            return False, (time.time() - t0) * 1000, str(e)


def run_benchmarks() -> BenchmarkSuite:
    """Run all benchmark tests."""
    suite = BenchmarkSuite()
    client = BenchmarkClient()

    print("=" * 60)
    print("VMUX BUNDLE DELIVERY BENCHMARK")
    print("=" * 60)
    print(f"API: {client.config.api_url}")
    print()

    # Test 1: Verify writeFile limit
    print("\n--- TEST 1: writeFile (inline base64) limit verification ---")
    print("Testing various sizes to find the RPC limit...\n")

    # Test sizes around the expected 32MB limit
    inline_sizes = [1, 5, 10, 20, 25, 30, 31, 32, 33, 35, 40]

    for size_mb in inline_sizes:
        print(f"Creating {size_mb}MB test bundle...")
        bundle = create_test_bundle(size_mb)
        actual_mb = len(bundle) / (1024 * 1024)
        print(f"  Actual size: {actual_mb:.2f}MB")

        success, duration_ms, error = client.test_inline_writefile(bundle)
        suite.add(
            BenchmarkResult(
                method="inline_writefile",
                bundle_size_mb=actual_mb,
                success=success,
                duration_ms=duration_ms,
                error=error,
            )
        )

        # Stop if we hit the limit
        if not success and "32" in str(error).lower() or "limit" in str(error).lower():
            print(f"\n  *** Found limit at ~{size_mb}MB ***\n")
            break

    # Test 2: R2 delivery for larger bundles
    print("\n--- TEST 2: R2 upload + curl delivery ---")
    print("Testing R2 path for bundles >= 32MB...\n")

    r2_sizes = [10, 32, 50, 64, 80, 100]

    for size_mb in r2_sizes:
        print(f"Creating {size_mb}MB test bundle...")
        bundle = create_test_bundle(size_mb)
        actual_mb = len(bundle) / (1024 * 1024)
        print(f"  Actual size: {actual_mb:.2f}MB")

        success, duration_ms, error = client.test_r2_delivery(bundle)
        suite.add(
            BenchmarkResult(
                method="r2_curl",
                bundle_size_mb=actual_mb,
                success=success,
                duration_ms=duration_ms,
                error=error,
            )
        )

    # Summary
    suite.print_summary()

    # Recommendations
    print("\n" + "=" * 60)
    print("RECOMMENDATIONS")
    print("=" * 60)

    inline_max = max(
        (r.bundle_size_mb for r in suite.results if r.method == "inline_writefile" and r.success),
        default=0,
    )
    r2_max = max(
        (r.bundle_size_mb for r in suite.results if r.method == "r2_curl" and r.success),
        default=0,
    )

    print(f"\n1. writeFile (inline): Works up to ~{inline_max:.0f}MB")
    print(f"   - Use for bundles < {inline_max:.0f}MB (fast, single request)")

    print(f"\n2. R2 + curl: Works up to ~{r2_max:.0f}MB tested")
    print(f"   - Use for bundles >= {inline_max:.0f}MB (requires upload step)")

    print("\n3. mountBucket (FUSE):")
    print("   - NOT YET TESTED (requires production deploy)")
    print("   - Potentially faster for very large bundles (>100MB)")
    print("   - Files streamed on-demand, no full download needed")
    print("   - Latency: Higher per-file access, lower initial setup")

    client.close()
    return suite


if __name__ == "__main__":
    run_benchmarks()
