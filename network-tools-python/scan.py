import ipaddress
import re
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from itertools import islice
from pathlib import Path

from ping import ping_host
from port_scan import scan_ports


@dataclass
class DeviceResult:
    ip: str
    open_ports: list[int]


@dataclass
class BatchResult:
    target: str
    ping_success: bool
    latency_ms: float | None
    loss_percent: float
    open_ports: list[int]
    message: str

    def to_text(self):
        latency = f"{self.latency_ms:.1f} ms" if self.latency_ms is not None else "unknown"
        ports = ",".join(str(port) for port in self.open_ports) or "none"
        return (
            f"{self.target}: ping={'OK' if self.ping_success else 'FAIL'}, "
            f"latency={latency}, loss={self.loss_percent:.1f}%, open_ports={ports}, "
            f"message={self.message}"
        )


def scan_subnet(subnet, ports=None, timeout=0.8, limit=256, workers=128):
    if ports is None:
        ports = [80, 443]
    if limit < 1:
        raise ValueError("Scan limit must be greater than zero.")

    network = ipaddress.ip_network(subnet, strict=False)
    hosts = list(islice(network.hosts(), limit))
    devices = []

    def scan_host(ip):
        ip_text = str(ip)
        port_results = scan_ports(ip_text, ports, timeout=timeout, workers=len(ports))
        open_ports = [item.port for item in port_results if item.open]
        if not open_ports:
            return None
        return DeviceResult(ip=ip_text, open_ports=open_ports)

    with ThreadPoolExecutor(max_workers=min(workers, max(1, len(hosts)))) as executor:
        future_map = {executor.submit(scan_host, ip): ip for ip in hosts}
        for future in as_completed(future_map):
            result = future.result()
            if result:
                devices.append(result)

    return sorted(devices, key=lambda item: ipaddress.ip_address(item.ip))


def load_targets(path):
    """Read IP addresses or host names from a UTF-8 text file."""
    file_path = Path(path)
    if not file_path.exists():
        raise FileNotFoundError(f"Target file does not exist: {file_path}")
    if not file_path.is_file():
        raise ValueError(f"Target path is not a file: {file_path}")

    targets = []
    try:
        lines = file_path.read_text(encoding="utf-8-sig").splitlines()
    except PermissionError as exc:
        raise PermissionError(f"Permission denied: {file_path}") from exc

    for line_number, line in enumerate(lines, start=1):
        target = line.split("#", 1)[0].strip()
        if not target:
            continue
        if not is_valid_target(target):
            raise ValueError(f"Invalid target on line {line_number}: {target}")
        targets.append(target)

    if not targets:
        raise ValueError("Target file contains no valid IP addresses or domains.")
    return list(dict.fromkeys(targets))


def is_valid_target(target):
    """Validate an IPv4/IPv6 address or a conventional DNS host name."""
    try:
        ipaddress.ip_address(target)
        return True
    except ValueError:
        pass

    if len(target) > 253 or " " in target:
        return False
    hostname_pattern = re.compile(
        r"^(?=.{1,253}\.?$)(?:[A-Za-z0-9](?:[A-Za-z0-9-]{0,61}[A-Za-z0-9])?\.)*"
        r"[A-Za-z0-9](?:[A-Za-z0-9-]{0,61}[A-Za-z0-9])?\.?$"
    )
    return bool(hostname_pattern.fullmatch(target))


def batch_check(targets, ports=None, scan_ports_enabled=False, timeout=1.0, workers=16):
    """Ping multiple targets and optionally scan selected TCP ports."""
    targets = [str(target).strip() for target in targets if str(target).strip()]
    if not targets:
        return []

    def check_target(target):
        try:
            ping_result = ping_host(target, count=2, timeout=max(1, int(timeout)))
            port_results = (
                scan_ports(target, ports or [], timeout=timeout)
                if scan_ports_enabled
                else []
            )
            open_ports = [item.port for item in port_results if item.open]
            return BatchResult(
                target=target,
                ping_success=ping_result.success,
                latency_ms=ping_result.avg_ms,
                loss_percent=ping_result.loss_percent,
                open_ports=open_ports,
                message="completed",
            )
        except Exception as exc:
            return BatchResult(target, False, None, 100.0, [], str(exc))

    results = []
    with ThreadPoolExecutor(max_workers=min(workers, len(targets))) as executor:
        future_map = {executor.submit(check_target, target): target for target in targets}
        for future in as_completed(future_map):
            results.append(future.result())
    return sorted(results, key=lambda item: item.target)


def batch_check_file(path, ports=None, scan_ports_enabled=False, timeout=1.0):
    """Convenience wrapper for loading targets and running a batch check."""
    return batch_check(
        load_targets(path),
        ports=ports,
        scan_ports_enabled=scan_ports_enabled,
        timeout=timeout,
    )
