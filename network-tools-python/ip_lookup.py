"""Public IP and IP geolocation helpers using keyless HTTPS services."""

import ipaddress
import json
from dataclasses import dataclass
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


PUBLIC_IP_URL = "https://api.ipify.org?format=json"
LOOKUP_URL = "https://ipapi.co/{ip}/json/"
USER_AGENT = "Network-Tools-Python/1.0"


@dataclass
class IPLookupResult:
    ip: str
    success: bool
    country: str = ""
    region: str = ""
    city: str = ""
    isp: str = ""
    message: str = ""

    def to_text(self):
        status = "success" if self.success else "failed"
        return "\n".join(
            [
                f"IP: {self.ip or 'unknown'}",
                f"Status: {status}",
                f"Country: {self.country or 'unknown'}",
                f"Region: {self.region or 'unknown'}",
                f"City: {self.city or 'unknown'}",
                f"ISP: {self.isp or 'unknown'}",
                f"Message: {self.message or '-'}",
            ]
        )


def get_public_ip(timeout=5.0):
    """Return the current public IP without requiring an API key."""
    try:
        data = _request_json(PUBLIC_IP_URL, timeout)
        ip = str(data.get("ip", "")).strip()
        ipaddress.ip_address(ip)
        return ip
    except (ValueError, KeyError, HTTPError, URLError, TimeoutError, OSError) as exc:
        raise RuntimeError(f"Unable to get public IP: {exc}") from exc


def lookup_ip(ip=None, timeout=5.0):
    """Look up country, region, city, and ISP for an IP address.

    If ``ip`` is empty, the machine's public IP is queried first. All network
    and validation failures are converted into a result object so callers do
    not crash.
    """
    try:
        target_ip = str(ip or "").strip() or get_public_ip(timeout)
        ipaddress.ip_address(target_ip)
        data = _request_json(LOOKUP_URL.format(ip=target_ip), timeout)
        if data.get("error"):
            return IPLookupResult(
                target_ip,
                False,
                message=str(data.get("reason") or "IP service returned an error."),
            )
        return IPLookupResult(
            ip=target_ip,
            success=True,
            country=str(data.get("country_name") or data.get("country") or ""),
            region=str(data.get("region") or ""),
            city=str(data.get("city") or ""),
            isp=str(data.get("org") or data.get("asn") or ""),
            message="IP lookup completed.",
        )
    except ValueError:
        return IPLookupResult(str(ip or ""), False, message="Invalid IP address.")
    except (RuntimeError, HTTPError, URLError, TimeoutError, OSError, json.JSONDecodeError) as exc:
        return IPLookupResult(str(ip or ""), False, message=f"Network request failed: {exc}")


def _request_json(url, timeout):
    request = Request(url, headers={"User-Agent": USER_AGENT, "Accept": "application/json"})
    with urlopen(request, timeout=timeout) as response:
        return json.loads(response.read().decode("utf-8"))
