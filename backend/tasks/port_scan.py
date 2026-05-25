import nmap


# 위험 포트 목록과 설명
DANGEROUS_PORTS = {
    21: {"service": "FTP", "severity": "high", "description": "FTP는 암호화되지 않아 데이터가 노출될 수 있습니다."},
    22: {"service": "SSH", "severity": "medium", "description": "SSH가 외부에 노출되어 있습니다. 접근을 제한하세요."},
    23: {"service": "Telnet", "severity": "high", "description": "Telnet은 암호화가 없어 매우 위험합니다."},
    25: {"service": "SMTP", "severity": "medium", "description": "메일 서버가 외부에 노출되어 있습니다."},
    53: {"service": "DNS", "severity": "medium", "description": "DNS 서버가 외부에 노출되어 있습니다."},
    80: {"service": "HTTP", "severity": "low", "description": "HTTP 웹서버가 열려있습니다. HTTPS로 전환을 권장합니다."},
    110: {"service": "POP3", "severity": "medium", "description": "POP3 메일 서버가 외부에 노출되어 있습니다."},
    143: {"service": "IMAP", "severity": "medium", "description": "IMAP 메일 서버가 외부에 노출되어 있습니다."},
    443: {"service": "HTTPS", "severity": "info", "description": "HTTPS 웹서버가 열려있습니다. (정상)"},
    1433: {"service": "MSSQL", "severity": "high", "description": "MS SQL DB가 외부에 노출되어 있습니다. 즉시 차단하세요."},
    1521: {"service": "Oracle DB", "severity": "high", "description": "Oracle DB가 외부에 노출되어 있습니다. 즉시 차단하세요."},
    3306: {"service": "MySQL", "severity": "high", "description": "MySQL DB가 외부에 노출되어 있습니다. 즉시 차단하세요."},
    3389: {"service": "RDP", "severity": "high", "description": "윈도우 원격 접속이 외부에 노출되어 있습니다."},
    5432: {"service": "PostgreSQL", "severity": "high", "description": "PostgreSQL DB가 외부에 노출되어 있습니다. 즉시 차단하세요."},
    5900: {"service": "VNC", "severity": "high", "description": "VNC 원격 데스크탑이 외부에 노출되어 있습니다."},
    6379: {"service": "Redis", "severity": "high", "description": "Redis DB가 외부에 노출되어 있습니다. 즉시 차단하세요."},
    8080: {"service": "HTTP-Alt", "severity": "low", "description": "개발용 웹서버가 외부에 노출되어 있습니다."},
    8443: {"service": "HTTPS-Alt", "severity": "low", "description": "대체 HTTPS 포트가 열려있습니다."},
    9200: {"service": "Elasticsearch", "severity": "high", "description": "Elasticsearch가 외부에 노출되어 있습니다. 즉시 차단하세요."},
    27017: {"service": "MongoDB", "severity": "high", "description": "MongoDB가 외부에 노출되어 있습니다. 즉시 차단하세요."},
}


def run_port_scan(host: str) -> dict:
    """
    nmap으로 상위 1000개 포트를 스캔하고 결과를 반환합니다.
    """
    nm = nmap.PortScanner()

    try:
        # 상위 1000개 포트 스캔
        # -T4: 빠른 스캔 속도
        # --top-ports 1000: 상위 1000개 포트
        nm.scan(hosts=host, arguments="-T4 --top-ports 1000 --host-timeout 60s")
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "open_ports": [],
            "vulnerabilities": [],
        }

    # 스캔 결과에 호스트가 없으면 에러
    if host not in nm.all_hosts():
        return {
            "success": False,
            "error": "호스트에 접근할 수 없습니다.",
            "open_ports": [],
            "vulnerabilities": [],
        }

    open_ports = []
    vulnerabilities = []

    # 열린 포트 목록 수집
    for proto in nm[host].all_protocols():
        ports = nm[host][proto].keys()
        for port in ports:
            state = nm[host][proto][port]["state"]
            if state == "open":
                service = nm[host][proto][port].get("name", "unknown")
                open_ports.append({
                    "port": port,
                    "protocol": proto,
                    "service": service,
                    "state": state,
                })

                # 위험 포트 목록과 비교
                if port in DANGEROUS_PORTS:
                    info = DANGEROUS_PORTS[port]
                    # info 포트는 취약점 아님 (HTTPS 등 정상 포트)
                    if info["severity"] != "info":
                        vulnerabilities.append({
                            "port": port,
                            "service": info["service"],
                            "severity": info["severity"],
                            "description": info["description"],
                        })

    # 심각도별 개수 집계
    summary = {"high": 0, "medium": 0, "low": 0}
    for v in vulnerabilities:
        summary[v["severity"]] += 1

    return {
        "success": True,
        "host": host,
        "open_ports": open_ports,
        "vulnerabilities": vulnerabilities,
        "summary": summary,
        "total_open": len(open_ports),
        "total_vulnerabilities": len(vulnerabilities),
    }