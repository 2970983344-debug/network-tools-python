"""Network latency and download speed testing with a standard-library fallback."""

import time
from dataclasses import dataclass
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from ping import ping_host


FALLBACK_DOWNLOAD_URL = "https://speed.cloudflare.com/__down?bytes=2000000"


@dataclass
class SpeedTestResult:
    success: bool
    latency_ms: float | None
    download_mbps: float | None
    method: str
    message: str

    def to_text(self):
        latency = f"{self.latency_ms:.1f} ms" if self.latency_ms is not None else "unknown"
        download = (
            f"{self.download_mbps:.2f} Mbps"
            if self.download_mbps is not None
            else "unknown"
        )
        return "\n".join(
            [
                f"Status: {'success' if self.success else 'failed'}",
                f"Latency: {latency}",
                f"Download speed: {download}",
                f"Method: {self.method}",
                f"Message: {self.message}",
            ]
        )


def run_speed_test(timeout=15.0, prefer_library=True):
    """Test latency and download speed.

    ``speedtest-cli`` is used when available. If it is missing or fails, the
    function falls back to system ping plus a timed HTTPS download.
    """
    if prefer_library:
        try:
            import speedtest

            tester = speedtest.Speedtest(timeout=timeout, secure=True)
            tester.get_best_server()
            download_mbps = tester.download() / 1_000_000
            latency_ms = float(tester.results.ping)
            return SpeedTestResult(
                True,
                latency_ms,
                download_mbps,
                "speedtest-cli",
                "Speed test completed with speedtest-cli.",
            )
        except ImportError:
            fallback_reason = "speedtest-cli is not installed; fallback used."
        except Exception as exc:
            fallback_reason = f"speedtest-cli failed ({exc}); fallback used."
    else:
        fallback_reason = "Standard-library fallback requested."

    return _fallback_speed_test(timeout, fallback_reason)


def _fallback_speed_test(timeout, reason):
    ping_result = ping_host("1.1.1.1", count=3, timeout=max(1, int(timeout / 3)))
    latency_ms = ping_result.avg_ms
    start = time.perf_counter()
    total_bytes = 0

    try:
        request = Request(
            FALLBACK_DOWNLOAD_URL,
            headers={"User-Agent": "Network-Tools-Python/1.0"},
        )
        with urlopen(request, timeout=timeout) as response:
            while True:
                chunk = response.read(64 * 1024)
                if not chunk:
                    break
                total_bytes += len(chunk)
        elapsed = max(time.perf_counter() - start, 0.001)
        download_mbps = total_bytes * 8 / elapsed / 1_000_000
        return SpeedTestResult(
            True,
            latency_ms,
            download_mbps,
            "urllib fallback",
            reason,
        )
    except (HTTPError, URLError, TimeoutError, PermissionError, OSError) as exc:
        return SpeedTestResult(
            ping_result.success,
            latency_ms,
            None,
            "ping-only fallback",
            f"{reason} Download test failed: {exc}",
        )
