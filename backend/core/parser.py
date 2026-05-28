VULN_TYPES = {
    "missing_hsts",
    "missing_csp",
    "missing_x_frame_options",
    "missing_x_content_type",
    "weak_tls_protocol",
    "expired_certificate",
    "self_signed_certificate",
    "exposed_ssh_port",
    "exposed_db_port",
    "server_info_leaked",
}


def parse_scan_result(raw_result: dict) -> list[dict]:
    vulnerabilities = []
    vulnerabilities.extend(_parse_header_scan(raw_result.get("header_scan", {})))
    vulnerabilities.extend(_parse_ssl_scan(raw_result.get("ssl_scan", {})))
    vulnerabilities.extend(_parse_port_scan(raw_result.get("port_scan", {})))
    return vulnerabilities


def _parse_header_scan(header_scan: dict) -> list[dict]:
    vulnerabilities = []
    header_map = {
        "Strict-Transport-Security": {
            "type": "missing_hsts",
            "title": "HSTS 헤더 누락",
            "detail": "Strict-Transport-Security 헤더가 없습니다. HTTPS 강제 적용이 안 됩니다.",
            "severity": "high",
            "cvss_score": 7.5,
        },
        "Content-Security-Policy": {
            "type": "missing_csp",
            "title": "CSP 헤더 누락",
            "detail": "Content-Security-Policy 헤더가 없습니다. XSS 공격에 취약합니다.",
            "severity": "high",
            "cvss_score": 6.1,
        },
        "X-Frame-Options": {
            "type": "missing_x_frame_options",
            "title": "X-Frame-Options 헤더 누락",
            "detail": "클릭재킹(Clickjacking) 공격에 취약합니다.",
            "severity": "medium",
            "cvss_score": 6.1,
        },
        "X-Content-Type-Options": {
            "type": "missing_x_content_type",
            "title": "X-Content-Type-Options 헤더 누락",
            "detail": "MIME 타입 스니핑 공격에 취약합니다.",
            "severity": "medium",
            "cvss_score": 4.3,
        },
    }

    for item in header_scan.get("missing_headers", []):
        vulnerability = header_map.get(item.get("header"))
        if vulnerability:
            vulnerabilities.append(vulnerability)

    if header_scan.get("server_info_leaked"):
        vulnerabilities.append(
            {
                "type": "server_info_leaked",
                "title": "서버 버전 정보 노출",
                "detail": (
                    "Server 헤더에 버전 정보가 노출됩니다: "
                    f"{header_scan.get('server_header', '')}"
                ),
                "severity": "low",
                "cvss_score": 3.7,
            }
        )

    return vulnerabilities


def _parse_ssl_scan(ssl_scan: dict) -> list[dict]:
    vulnerabilities = []
    for vuln in ssl_scan.get("vulnerabilities", []):
        vuln_type = vuln.get("type")
        if vuln_type == "weak_protocol":
            vulnerabilities.append(
                {
                    "type": "weak_tls_protocol",
                    "title": "취약한 TLS 프로토콜 활성화",
                    "detail": vuln.get("detail", ""),
                    "severity": "high",
                    "cvss_score": 7.5,
                }
            )
        elif vuln_type == "expired_cert":
            vulnerabilities.append(
                {
                    "type": "expired_certificate",
                    "title": "SSL 인증서 만료",
                    "detail": vuln.get("detail", ""),
                    "severity": "high",
                    "cvss_score": 7.5,
                }
            )
        elif vuln_type == "self_signed_certificate":
            vulnerabilities.append(
                {
                    "type": "self_signed_certificate",
                    "title": "자체 서명 인증서 사용",
                    "detail": "신뢰할 수 없는 인증서입니다. 브라우저 경고가 표시됩니다.",
                    "severity": "medium",
                    "cvss_score": 5.3,
                }
            )

    return vulnerabilities


def _parse_port_scan(port_scan: dict) -> list[dict]:
    vulnerabilities = []
    db_services = {"MySQL", "PostgreSQL", "MongoDB", "Redis"}

    for port_info in port_scan.get("unexpected_ports", []):
        service = port_info.get("service")
        port = port_info.get("port")
        if service in db_services:
            vulnerabilities.append(
                {
                    "type": "exposed_db_port",
                    "title": f"DB 포트 외부 노출 ({service})",
                    "detail": f"포트 {port} ({service})가 외부에 노출되어 있습니다.",
                    "severity": "critical",
                    "cvss_score": 9.8,
                }
            )
        elif service == "SSH":
            vulnerabilities.append(
                {
                    "type": "exposed_ssh_port",
                    "title": "SSH 포트 외부 노출",
                    "detail": f"포트 {port} (SSH)가 외부에 노출되어 있습니다.",
                    "severity": "critical",
                    "cvss_score": 9.1,
                }
            )

    return vulnerabilities
