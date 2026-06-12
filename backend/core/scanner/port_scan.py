import signal

import nmap

from core.scanner.validator import validate_target


DANGEROUS_PORTS = {
    21: "FTP",
    22: "SSH",
    23: "Telnet",
    3306: "MySQL",
    5432: "PostgreSQL",
    6379: "Redis",
    27017: "MongoDB",
    8080: "HTTP-Alt",
    8443: "HTTPS-Alt",
}
PORT_SCAN_TIMEOUT = 120


def _timeout_handler(signum, frame):
    raise TimeoutError(f"nmap 스캔 타임아웃 ({PORT_SCAN_TIMEOUT}초 초과)")


def run_port_scan(target: str) -> dict:
    clean_target = validate_target(target)
    scanner = nmap.PortScanner()

    previous_handler = signal.getsignal(signal.SIGALRM)
    signal.signal(signal.SIGALRM, _timeout_handler)
    signal.alarm(PORT_SCAN_TIMEOUT)
    try:
        scanner.scan(clean_target, arguments="-sV -Pn -F -T4")
    finally:
        signal.alarm(0)
        signal.signal(signal.SIGALRM, previous_handler)

    open_ports = []
    unexpected_ports = []

    for host in scanner.all_hosts():
        for proto in scanner[host].all_protocols():
            for port in scanner[host][proto].keys():
                port_data = scanner[host][proto][port]
                if port_data.get("state") != "open":
                    continue

                service = port_data.get("name", "unknown")
                version = port_data.get("version", "")
                open_ports.append(
                    {
                        "port": port,
                        "protocol": proto,
                        "service": service,
                        "version": version,
                    }
                )

                if port in DANGEROUS_PORTS:
                    service_name = DANGEROUS_PORTS[port]
                    unexpected_ports.append(
                        {
                            "port": port,
                            "service": service_name,
                            "reason": f"외부 노출된 {service_name} 포트",
                        }
                    )

    return {
        "open_ports": open_ports,
        "unexpected_ports": unexpected_ports,
    }
