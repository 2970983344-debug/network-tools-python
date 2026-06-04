import socket
import time
from dataclasses import dataclass


@dataclass
class DnsResult:
    host: str
    success: bool
    addresses: list[str]
    duration_ms: float
    message: str

    def to_text(self):
        status = "resolved" if self.success else "failed"
        addresses = ", ".join(self.addresses) if self.addresses else "none"
        return "\n".join(
            [
                f"Host: {self.host}",
                f"Status: {status}",
                f"Addresses: {addresses}",
                f"Duration: {self.duration_ms:.1f} ms",
                f"Message: {self.message}",
            ]
        )


def check_dns(host, timeout=3.0):
    old_timeout = socket.getdefaulttimeout()
    socket.setdefaulttimeout(timeout)
    start = time.perf_counter()
    try:
        records = socket.getaddrinfo(host, None, proto=socket.IPPROTO_TCP)
        addresses = sorted({item[4][0] for item in records})
        duration_ms = (time.perf_counter() - start) * 1000
        return DnsResult(
            host=host,
            success=bool(addresses),
            addresses=addresses,
            duration_ms=duration_ms,
            message="DNS resolution successful" if addresses else "No address returned",
        )
    except socket.gaierror as exc:
        duration_ms = (time.perf_counter() - start) * 1000
        return DnsResult(host, False, [], duration_ms, str(exc))
    except OSError as exc:
        duration_ms = (time.perf_counter() - start) * 1000
        return DnsResult(host, False, [], duration_ms, str(exc))
    finally:
        socket.setdefaulttimeout(old_timeout)
