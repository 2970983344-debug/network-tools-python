"""Command-line entry point for Network Tools Python."""

import argparse
import sys

from dns_check import check_dns
from ip_lookup import lookup_ip
from ping import ping_host
from port_scan import parse_port_spec, scan_ports
from report import batch_results_to_entries, export_report, generate_report
from scan import batch_check_file, scan_subnet
from speed_test import run_speed_test
from version import version_text


def build_parser():
    parser = argparse.ArgumentParser(
        description=f"{version_text()} - GUI and CLI network diagnostics."
    )
    parser.add_argument("--version", action="version", version=version_text())
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("gui", help="Launch the Tkinter desktop application.")

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
        help="Ports and ranges, for example 80,443,8000-8010.",
    )
    port_parser.add_argument(
        "-t", "--timeout", type=float, default=1.5, help="Socket timeout seconds."
    )

    lan_parser = subparsers.add_parser("scan", help="Scan LAN devices by subnet.")
    lan_parser.add_argument("subnet", help="CIDR subnet, for example 192.168.1.0/24.")
    lan_parser.add_argument(
        "-p", "--ports", default="80,443", help="Ports used for device discovery."
    )
    lan_parser.add_argument(
        "-t", "--timeout", type=float, default=0.8, help="Socket timeout seconds."
    )
    lan_parser.add_argument("--limit", type=int, default=256, help="Maximum IP count.")

    dns_parser = subparsers.add_parser("dns", help="Check DNS resolution.")
    dns_parser.add_argument("host", help="Domain name, for example baidu.com.")
    dns_parser.add_argument(
        "-t", "--timeout", type=float, default=3.0, help="DNS timeout seconds."
    )

    ip_parser = subparsers.add_parser("ip", help="Look up public or specified IP.")
    ip_parser.add_argument(
        "address",
        nargs="?",
        default=None,
        help="Optional IP address. Omit it to query the current public IP.",
    )
    ip_parser.add_argument(
        "-t", "--timeout", type=float, default=5.0, help="Request timeout seconds."
    )

    speed_parser = subparsers.add_parser("speed", help="Run a network speed test.")
    speed_parser.add_argument(
        "-t", "--timeout", type=float, default=15.0, help="Test timeout seconds."
    )
    speed_parser.add_argument(
        "--fallback",
        action="store_true",
        help="Skip speedtest-cli and use the standard-library fallback.",
    )

    batch_parser = subparsers.add_parser("batch", help="Check targets from a text file.")
    batch_parser.add_argument(
        "file",
        nargs="?",
        default="targets.txt",
        help="UTF-8 target file, default: targets.txt.",
    )
    batch_parser.add_argument(
        "--scan-ports",
        action="store_true",
        help="Also scan the configured ports.",
    )
    batch_parser.add_argument(
        "-p", "--ports", default="80,443", help="Ports used with --scan-ports."
    )
    batch_parser.add_argument(
        "-t", "--timeout", type=float, default=1.0, help="Network timeout seconds."
    )
    batch_parser.add_argument(
        "-o",
        "--output",
        default=None,
        help="Optional TXT, CSV, HTML, or Markdown report path.",
    )

    report_parser = subparsers.add_parser("report", help="Generate a diagnosis report.")
    report_parser.add_argument("host", help="Host or domain name to diagnose.")
    report_parser.add_argument(
        "-p", "--ports", default="80,443,3306", help="Ports included in the report."
    )
    report_parser.add_argument(
        "-s", "--subnet", default=None, help="Optional CIDR subnet for LAN scanning."
    )
    report_parser.add_argument(
        "-o",
        "--output",
        default="network_report.txt",
        help="Output .txt, .csv, .html, or .md file.",
    )
    report_parser.add_argument(
        "--no-scan", action="store_true", help="Skip LAN scan."
    )
    return parser


def parse_ports(value):
    """Backward-compatible wrapper retained for existing imports."""
    return parse_port_spec(value)


def main(argv=None):
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        if args.command == "gui":
            from gui import launch_gui

            launch_gui()
            return 0

        if args.command == "ping":
            print(ping_host(args.host, count=args.count, timeout=args.timeout).to_text())
            return 0

        if args.command == "ports":
            for item in scan_ports(
                args.host, parse_port_spec(args.ports), timeout=args.timeout
            ):
                status = "OPEN" if item.open else "CLOSED"
                print(f"{args.host}:{item.port:<5} {status:<6} {item.message}")
            return 0

        if args.command == "scan":
            devices = scan_subnet(
                args.subnet,
                ports=parse_port_spec(args.ports),
                timeout=args.timeout,
                limit=args.limit,
            )
            if not devices:
                print("No devices found.")
            for device in devices:
                ports = ",".join(str(port) for port in device.open_ports)
                print(f"{device.ip:<16} open ports: {ports}")
            return 0

        if args.command == "dns":
            print(check_dns(args.host, timeout=args.timeout).to_text())
            return 0

        if args.command == "ip":
            print(lookup_ip(args.address, timeout=args.timeout).to_text())
            return 0

        if args.command == "speed":
            print(
                run_speed_test(
                    timeout=args.timeout, prefer_library=not args.fallback
                ).to_text()
            )
            return 0

        if args.command == "batch":
            ports = parse_port_spec(args.ports) if args.scan_ports else []
            results = batch_check_file(
                args.file,
                ports=ports,
                scan_ports_enabled=args.scan_ports,
                timeout=args.timeout,
            )
            for item in results:
                print(item.to_text())
            if args.output:
                output = export_report(
                    batch_results_to_entries(results),
                    args.output,
                    title="批量网络检测报告",
                )
                print(f"Report generated: {output}")
            return 0

        if args.command == "report":
            subnet = None if args.no_scan else args.subnet
            output = generate_report(
                args.host,
                ports=parse_port_spec(args.ports),
                subnet=subnet,
                output_path=args.output,
            )
            print(f"Report generated: {output}")
            return 0
    except (ValueError, RuntimeError, FileNotFoundError, PermissionError, OSError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 2
    except KeyboardInterrupt:
        print("\nOperation cancelled.", file=sys.stderr)
        return 130

    parser.print_help()
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
