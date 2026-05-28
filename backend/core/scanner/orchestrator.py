from datetime import datetime

from core.scanner.header_scan import run_header_scan
from core.scanner.port_scan import run_port_scan
from core.scanner.ssl_scan import run_ssl_scan
from core.scanner.validator import validate_target


def run_full_scan(target_url: str) -> dict:
    domain = validate_target(target_url)
    result = {
        "target": target_url,
        "domain": domain,
        "scanned_at": datetime.utcnow().isoformat(),
        "port_scan": {},
        "ssl_scan": {},
        "header_scan": {},
    }

    for key, scanner, value in (
        ("port_scan", run_port_scan, domain),
        ("ssl_scan", run_ssl_scan, domain),
        ("header_scan", run_header_scan, target_url),
    ):
        try:
            result[key] = scanner(value)
        except Exception as exc:
            result[key] = {"error": str(exc)}

    return result
