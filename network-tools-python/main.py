import argparse

from dns_check import check_dns
from ping import ping_host
from port_scan import scan_ports
from report import generate_report
from scan import scan_subnet


def build_parser():
    parser = argparse.ArgumentParser(
        description="Network Tools Python v2.0: ping, port scan, LAN scan, DNS check, and reports."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    ping_parser = subparsers.add_parser("ping", help="Ping a host.")
    ping_parser.add_argument("host", help="Host or IP address, for example baidu.com.")
    ping_parser.add_argument("-c", "--count", type=int, default=4, help="Ping count.")
    ping_parser.add_argument(
        "-t", "--timeout", type=int, default=2, help="Timeout seconds per packet."
    )

    port_parser = subparsers.add_parser("ports", help="Scan ports on a host.")
    port_parser.add_argument("host", help="Host or IP address.")
    port_parser.add_argument(
        "-p",
        "--ports",
        default="80,443,3306",
        help="Comma-separated ports, for example 80,443,3306.",
    )
    port_parser.add_argument(
        "-t", "--timeout", type=float, default=1.5, help="Socket timeout seconds."
    )

    lan_parser = subparsers.add_parser("scan", help="Scan LAN devices by subnet.")
    lan_parser.add_argument(
        "subnet", help="CIDR subnet, for example 192.168.1.0/24."
    )
    lan_parser.add_argument(
        "-p",
        "--ports",
        default="80,443",
        help="Ports used to judge whether a device is alive.",
    )
    lan_parser.add_argument(
        "-t", "--timeout", type=float, default=0.8, help="Socket timeout seconds."
    )
    lan_parser.add_argument(
        "--limit",
        type=int,
        default=256,
        help="Maximum IP addresses to scan.",
    )

    dns_parser = subparsers.add_parser("dns", help="Check DNS resolution.")
    dns_parser.add_argument("host", help="Domain name, for example baidu.com.")
    dns_parser.add_argument(
        "-t", "--timeout", type=float, default=3.0, help="DNS timeout seconds."
    )

    report_parser = subparsers.add_parser("report", help="Generate a network diagnosis report.")
    report_parser.add_argument("host", help="Host or domain name to diagnose.")
    report_parser.add_argument(
        "-p",
        "--ports",
        default="80,443,3306",
        help="Comma-separated ports for port diagnosis.",
    )
    report_parser.add_argument(
        "-s",
        "--subnet",
        default=None,
        help="Optional CIDR subnet for LAN scan, for example 192.168.1.0/24.",
    )
    report_parser.add_argument(
        "-o",
        "--output",
        default="network_report.md",
        help="Output markdown report path.",
    )
    report_parser.add_argument(
        "--no-scan",
        action="store_true",
        help="Skip LAN scan even if subnet is provided.",
    )

    return parser


def parse_ports(value):
    ports = []
    for part in value.split(","):
        part = part.strip()
        if not part:
            continue
        port = int(part)
        if port < 1 or port > 65535:
            raise ValueError(f"Invalid port: {port}")
        ports.append(port)
    return ports


def main():
    parser = build_parser()
    args = parser.parse_args()

    if args.command == "ping":
        result = ping_host(args.host, count=args.count, timeout=args.timeout)
        print(result.to_text())
        return

    if args.command == "ports":
        ports = parse_ports(args.ports)
        results = scan_ports(args.host, ports, timeout=args.timeout)
        for item in results:
            status = "OPEN" if item.open else "CLOSED"
            print(f"{args.host}:{item.port:<5} {status:<6} {item.message}")
        return

    if args.command == "scan":
        ports = parse_ports(args.ports)
        devices = scan_subnet(
            args.subnet,
            ports=ports,
            timeout=args.timeout,
            limit=args.limit,
        )
        if not devices:
            print("No devices found.")
            return
        for device in devices:
            open_ports = ",".join(str(port) for port in device.open_ports)
            print(f"{device.ip:<16} open ports: {open_ports}")
        return

    if args.command == "dns":
        result = check_dns(args.host, timeout=args.timeout)
        print(result.to_text())
        return

    if args.command == "report":
        ports = parse_ports(args.ports)
        subnet = None if args.no_scan else args.subnet
        output = generate_report(args.host, ports=ports, subnet=subnet, output_path=args.output)
        print(f"Report generated: {output}")


if __name__ == "__main__":
    main()
