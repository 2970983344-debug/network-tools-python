"""Diagnosis collection and TXT/CSV/HTML/Markdown report export."""

import csv
import html
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path

from dns_check import check_dns
from ping import ping_host
from port_scan import scan_ports
from scan import scan_subnet


@dataclass
class ReportEntry:
    checked_at: str
    target: str
    check_type: str
    result: str
    status: str


def create_entry(target, check_type, result, status, checked_at=None):
    """Create a normalized report row."""
    return ReportEntry(
        checked_at=checked_at or datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        target=str(target),
        check_type=str(check_type),
        result=str(result),
        status=str(status),
    )


def generate_report(host, ports=None, subnet=None, output_path="network_report.txt"):
    """Run common checks and export a diagnosis report.

    The existing function name and parameters are preserved. Output format is
    selected by the file extension: .txt, .csv, .html/.htm, or .md.
    """
    host = str(host or "").strip()
    if not host:
        raise ValueError("Report target cannot be empty.")
    ports = ports or [80, 443, 3306]
    entries = collect_diagnosis(host, ports, subnet)
    return export_report(entries, output_path, title="网络诊断报告")


def collect_diagnosis(host, ports=None, subnet=None):
    """Collect Ping, DNS, ports, and optional LAN scan into report entries."""
    ports = ports or [80, 443, 3306]
    entries = []

    ping_result = ping_host(host, count=4, timeout=2)
    entries.append(
        create_entry(
            host,
            "Ping 检测",
            (
                f"sent={ping_result.transmitted}, received={ping_result.received}, "
                f"loss={ping_result.loss_percent:.1f}%, "
                f"avg={_format_latency(ping_result.avg_ms)}"
            ),
            "正常" if ping_result.success else "异常",
        )
    )

    dns_result = check_dns(host)
    entries.append(
        create_entry(
            host,
            "DNS 解析",
            (
                f"addresses={','.join(dns_result.addresses) or 'none'}, "
                f"duration={dns_result.duration_ms:.1f}ms, message={dns_result.message}"
            ),
            "正常" if dns_result.success else "异常",
        )
    )

    for item in scan_ports(host, ports):
        entries.append(
            create_entry(
                f"{host}:{item.port}",
                "端口扫描",
                item.message,
                "开放" if item.open else "关闭/不可达",
            )
        )

    if subnet:
        try:
            devices = scan_subnet(subnet, ports=[80, 443], timeout=0.8, limit=256)
            if devices:
                for device in devices:
                    entries.append(
                        create_entry(
                            device.ip,
                            "局域网扫描",
                            f"open_ports={','.join(str(port) for port in device.open_ports)}",
                            "发现设备",
                        )
                    )
            else:
                entries.append(create_entry(subnet, "局域网扫描", "No devices found.", "无结果"))
        except (ValueError, PermissionError, OSError) as exc:
            entries.append(create_entry(subnet, "局域网扫描", str(exc), "失败"))

    return entries


def batch_results_to_entries(results):
    """Convert scan.BatchResult objects to report rows."""
    entries = []
    for item in results:
        latency = _format_latency(item.latency_ms)
        ports = ",".join(str(port) for port in item.open_ports) or "none"
        entries.append(
            create_entry(
                item.target,
                "批量检测",
                (
                    f"ping={'OK' if item.ping_success else 'FAIL'}, latency={latency}, "
                    f"loss={item.loss_percent:.1f}%, open_ports={ports}, "
                    f"message={item.message}"
                ),
                "正常" if item.ping_success else "异常",
            )
        )
    return entries


def export_report(entries, output_path, title="网络运维检测报告"):
    """Export report entries according to the output file extension."""
    path = Path(output_path).expanduser()
    suffix = path.suffix.lower()
    if suffix not in {".txt", ".csv", ".html", ".htm", ".md"}:
        raise ValueError("Report format must be TXT, CSV, HTML, or Markdown.")

    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        if suffix == ".csv":
            _write_csv(path, entries)
        elif suffix in {".html", ".htm"}:
            path.write_text(_render_html(entries, title), encoding="utf-8")
        elif suffix == ".md":
            path.write_text(_render_markdown(entries, title), encoding="utf-8")
        else:
            path.write_text(_render_text(entries, title), encoding="utf-8")
    except PermissionError as exc:
        raise PermissionError(f"No permission to write report: {path}") from exc
    except OSError as exc:
        raise OSError(f"Unable to write report {path}: {exc}") from exc
    return str(path.resolve())


def _write_csv(path, entries):
    with path.open("w", encoding="utf-8-sig", newline="") as file:
        writer = csv.DictWriter(
            file,
            fieldnames=["checked_at", "target", "check_type", "result", "status"],
        )
        writer.writeheader()
        for entry in entries:
            writer.writerow(asdict(entry))


def _render_text(entries, title):
    lines = [title, "=" * len(title), ""]
    for index, entry in enumerate(entries, start=1):
        lines.extend(
            [
                f"[{index}] 检测时间：{entry.checked_at}",
                f"检测目标：{entry.target}",
                f"检测类型：{entry.check_type}",
                f"检测结果：{entry.result}",
                f"状态说明：{entry.status}",
                "",
            ]
        )
    return "\n".join(lines)


def _render_markdown(entries, title):
    lines = [
        f"# {title}",
        "",
        "| 检测时间 | 检测目标 | 检测类型 | 检测结果 | 状态说明 |",
        "| --- | --- | --- | --- | --- |",
    ]
    for entry in entries:
        values = [
            entry.checked_at,
            entry.target,
            entry.check_type,
            entry.result,
            entry.status,
        ]
        lines.append("| " + " | ".join(value.replace("|", "\\|") for value in values) + " |")
    return "\n".join(lines) + "\n"


def _render_html(entries, title):
    rows = []
    for entry in entries:
        cells = [
            entry.checked_at,
            entry.target,
            entry.check_type,
            entry.result,
            entry.status,
        ]
        rows.append(
            "<tr>" + "".join(f"<td>{html.escape(value)}</td>" for value in cells) + "</tr>"
        )
    return f"""<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{html.escape(title)}</title>
  <style>
    body {{ font-family: "Microsoft YaHei", sans-serif; margin: 32px; color: #172033; }}
    h1 {{ font-size: 24px; }}
    table {{ width: 100%; border-collapse: collapse; }}
    th, td {{ border: 1px solid #d7dee8; padding: 10px; text-align: left; }}
    th {{ background: #eef4fb; }}
    tr:nth-child(even) {{ background: #f8fafc; }}
  </style>
</head>
<body>
  <h1>{html.escape(title)}</h1>
  <table>
    <thead><tr><th>检测时间</th><th>检测目标</th><th>检测类型</th><th>检测结果</th><th>状态说明</th></tr></thead>
    <tbody>{''.join(rows)}</tbody>
  </table>
</body>
</html>
"""


def _format_latency(value):
    return f"{value:.1f} ms" if value is not None else "unknown"
