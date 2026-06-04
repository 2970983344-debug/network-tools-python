from datetime import datetime
from pathlib import Path

from dns_check import check_dns
from ping import ping_host
from port_scan import scan_ports
from scan import scan_subnet


def generate_report(host, ports=None, subnet=None, output_path="network_report.md"):
    if ports is None:
        ports = [80, 443, 3306]

    ping_result = ping_host(host, count=4, timeout=2)
    dns_result = check_dns(host)
    port_results = scan_ports(host, ports)
    devices = scan_subnet(subnet, ports=[80, 443], timeout=0.8, limit=256) if subnet else []

    output = Path(output_path)
    output.write_text(
        _render_report(host, ports, subnet, ping_result, dns_result, port_results, devices),
        encoding="utf-8",
    )
    return str(output)


def _render_report(host, ports, subnet, ping_result, dns_result, port_results, devices):
    lines = [
        "# Network Diagnosis Report",
        "",
        f"- Generated at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        f"- Target host: `{host}`",
        f"- Checked ports: `{','.join(str(port) for port in ports)}`",
        f"- LAN subnet: `{subnet or 'not scanned'}`",
        "",
        "## Ping",
        "",
        f"- Status: {'reachable' if ping_result.success else 'unreachable'}",
        f"- Packets: sent={ping_result.transmitted}, received={ping_result.received}",
        f"- Loss: {ping_result.loss_percent:.1f}%",
        f"- Average latency: {_format_latency(ping_result.avg_ms)}",
        "",
        "## DNS",
        "",
        f"- Status: {'resolved' if dns_result.success else 'failed'}",
        f"- Addresses: {', '.join(dns_result.addresses) if dns_result.addresses else 'none'}",
        f"- Duration: {dns_result.duration_ms:.1f} ms",
        f"- Message: {dns_result.message}",
        "",
        "## Ports",
        "",
        "| Port | Status | Message |",
        "| --- | --- | --- |",
    ]

    for item in port_results:
        lines.append(f"| {item.port} | {'OPEN' if item.open else 'CLOSED'} | {item.message} |")

    lines.extend(["", "## LAN Devices", ""])
    if subnet and devices:
        lines.extend(["| IP | Open Ports |", "| --- | --- |"])
        for device in devices:
            lines.append(f"| {device.ip} | {','.join(str(port) for port in device.open_ports)} |")
    elif subnet:
        lines.append("No devices found on the selected ports.")
    else:
        lines.append("LAN scan skipped.")

    lines.extend(
        [
            "",
            "## Notes",
            "",
            "- Ping uses the operating system ping command.",
            "- Port checks use TCP socket connections.",
            "- LAN discovery marks a device as found when one of the selected ports is open.",
        ]
    )
    return "\n".join(lines) + "\n"


def _format_latency(value):
    return f"{value:.1f} ms" if value is not None else "unknown"
