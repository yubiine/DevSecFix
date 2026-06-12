import requests
from urllib3.exceptions import InsecureRequestWarning

from core.scanner.validator import validate_target


HEADER_SCAN_TIMEOUT = 30
SECURITY_HEADERS = [
    {"header": "Strict-Transport-Security", "severity": "high"},
    {"header": "Content-Security-Policy", "severity": "high"},
    {"header": "X-Frame-Options", "severity": "medium"},
    {"header": "X-Content-Type-Options", "severity": "medium"},
    {"header": "Referrer-Policy", "severity": "low"},
    {"header": "Permissions-Policy", "severity": "low"},
]

requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)


def run_header_scan(target_url: str) -> dict:
    clean_domain = validate_target(target_url)
    if target_url.startswith(("http://", "https://")):
        request_url = target_url
    else:
        request_url = f"https://{clean_domain}"

    try:
        response = requests.get(
            request_url,
            timeout=HEADER_SCAN_TIMEOUT,
            allow_redirects=True,
            verify=False,
        )
    except requests.Timeout as exc:
        raise TimeoutError(f"헤더 스캔 타임아웃 ({HEADER_SCAN_TIMEOUT}초 초과)") from exc
    except requests.RequestException as exc:
        raise RuntimeError(f"헤더 스캔 실패: {exc}") from exc

    headers = {key.lower(): value for key, value in response.headers.items()}
    missing_headers = []
    present_headers = []

    for item in SECURITY_HEADERS:
        if item["header"].lower() in headers:
            present_headers.append(item["header"])
        else:
            missing_headers.append(item)

    server_header = headers.get("server", "")

    return {
        "missing_headers": missing_headers,
        "present_headers": present_headers,
        "server_info_leaked": bool(server_header and "/" in server_header),
        "server_header": server_header,
        "status_code": response.status_code,
        "final_url": response.url,
    }
