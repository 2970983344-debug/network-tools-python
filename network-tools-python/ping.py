import platform
import re
import subprocess
import locale
from dataclasses import dataclass


@dataclass
class PingResult:
    host: str
    success: bool
    transmitted: int
    received: int
    loss_percent: float
    avg_ms: float | None
    raw_output: str

    def to_text(self):
        status = "reachable" if self.success else "unreachable"
        avg = f"{self.avg_ms:.1f} ms" if self.avg_ms is not None else "unknown"
        return "\n".join(
            [
                f"Host: {self.host}",
                f"Status: {status}",
                f"Packets: sent={self.transmitted}, received={self.received}",
                f"Loss: {self.loss_percent:.1f}%",
                f"Average latency: {avg}",
            ]
        )


def ping_host(host, count=4, timeout=2):
    system = platform.system().lower()
    if system == "windows":
        command = ["ping", "-n", str(count), "-w", str(timeout * 1000), host]
    else:
        command = ["ping", "-c", str(count), "-W", str(timeout), host]

    completed = subprocess.run(
        command,
        capture_output=True,
        text=True,
        encoding=locale.getpreferredencoding(False),
        errors="replace",
    )
    output = "\n".join([completed.stdout, completed.stderr]).strip()
    transmitted, received, loss = _parse_packet_stats(output, count)
    avg_ms = _parse_average_latency(output)
    success = completed.returncode == 0 or received > 0

    return PingResult(
        host=host,
        success=success,
        transmitted=transmitted,
        received=received,
        loss_percent=loss,
        avg_ms=avg_ms,
        raw_output=output,
    )


def _parse_packet_stats(output, default_count):
    normalized = _normalize_ping_output(output)

    for pattern in (
        r"Sent\s*=\s*(\d+),\s*Received\s*=\s*(\d+),\s*Lost\s*=\s*(\d+)\s*\(([\d.]+)%\s*loss\)",
        r"已发送\s*=\s*(\d+),\s*已接收\s*=\s*(\d+),\s*丢失\s*=\s*(\d+)\s*\(([\d.]+)%\s*丢失\)",
    ):
        windows_match = re.search(pattern, normalized, re.IGNORECASE)
        if windows_match:
            sent = int(windows_match.group(1))
            received = int(windows_match.group(2))
            loss = float(windows_match.group(4))
            return sent, received, loss

    unix_match = re.search(
        r"(\d+) packets transmitted, (\d+).*?received, ([\d.]+)% packet loss",
        normalized,
        re.IGNORECASE,
    )
    if unix_match:
        sent = int(unix_match.group(1))
        received = int(unix_match.group(2))
        loss = float(unix_match.group(3))
        return sent, received, loss

    return default_count, 0, 100.0


def _parse_average_latency(output):
    normalized = _normalize_ping_output(output)

    for pattern in (
        r"Average\s*=\s*<?([\d.]+)\s*(?:ms|毫秒)?",
        r"平均\s*=\s*<?([\d.]+)\s*(?:ms|毫秒)?",
    ):
        windows_match = re.search(pattern, normalized, re.IGNORECASE)
        if windows_match:
            return float(windows_match.group(1))

    unix_match = re.search(
        r"=\s*[\d.]+/([\d.]+)/[\d.]+/[\d.]+\s*ms",
        normalized,
        re.IGNORECASE,
    )
    if unix_match:
        return float(unix_match.group(1))

    return None


def _normalize_ping_output(output):
    return (
        output.replace("，", ",")
        .replace("：", ":")
        .replace("（", "(")
        .replace("）", ")")
    )
