import ipaddress
import socket
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass


@dataclass
class PortResult:
    host: str
    port: int
    open: bool
    message: str


@dataclass
class DeviceResult:
    ip: str
    open_ports: list[int]


def parse_port_spec(value, max_ports=1024):
    """Parse ports such as ``80,443,8000-8010``."""
    text = str(value or "").strip()
    if not text:
        raise ValueError("Port input cannot be empty.")

    ports = set()
    for part in text.split(","):
        part = part.strip()
        if not part:
            continue
        if "-" in part:
            start_text, end_text = part.split("-", 1)
            if not start_text.isdigit() or not end_text.isdigit():
                raise ValueError(f"Invalid port range: {part}")
            start, end = int(start_text), int(end_text)
            if start > end:
                raise ValueError(f"Port range start is greater than end: {part}")
            _validate_port(start)
            _validate_port(end)
            ports.update(range(start, end + 1))
        else:
            if not part.isdigit():
                raise ValueError(f"Invalid port: {part}")
            port = int(part)
            _validate_port(port)
            ports.add(port)

        if len(ports) > max_ports:
            raise ValueError(f"Too many ports. Maximum allowed: {max_ports}")

    if not ports:
        raise ValueError("No valid ports were provided.")
    return sorted(ports)


def _validate_port(port):
    if port < 1 or port > 65535:
        raise ValueError(f"Port out of range: {port}")


def check_port(host, port, timeout=1.5):
    host = str(host or "").strip()
    if not host:
        return PortResult("", port, False, "host cannot be empty")
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return PortResult(host, port, True, "connection successful")
    except socket.gaierror:
        return PortResult(host, port, False, "invalid host or DNS resolution failed")
    except socket.timeout:
        return PortResult(host, port, False, "timeout")
    except OSError as exc:
        return PortResult(host, port, False, str(exc))


def scan_ports(host, ports, timeout=1.5, workers=64):
    if not ports:
        return []
    results = []
    with ThreadPoolExecutor(max_workers=min(workers, max(1, len(ports)))) as executor:
        future_map = {
            executor.submit(check_port, host, port, timeout): port for port in ports
        }
        for future in as_completed(future_map):
            results.append(future.result())
    return sorted(results, key=lambda item: item.port)


def scan_subnet(subnet, ports=None, timeout=0.8, limit=256, workers=128):
    if ports is None:
        ports = [80, 443]

    network = ipaddress.ip_network(subnet, strict=False)
    hosts = list(network.hosts())[:limit]
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
