import concurrent.futures
from datetime import datetime, timezone

from sslyze import Scanner, ScanCommand, ServerNetworkLocation, ServerScanRequest

from core.scanner.validator import validate_target


SSL_SCAN_TIMEOUT = 30


def run_ssl_scan(target: str) -> dict:
    clean_target = validate_target(target)

    with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
        future = executor.submit(_scan, clean_target)
        try:
            result = future.result(timeout=SSL_SCAN_TIMEOUT)
        except concurrent.futures.TimeoutError as exc:
            future.cancel()
            raise TimeoutError(f"sslyze 스캔 타임아웃 ({SSL_SCAN_TIMEOUT}초 초과)") from exc

    supported_protocols = []
    vulnerabilities = []

    protocol_checks = {
        "ssl_2_0_cipher_suites": ("SSLv2", True),
        "ssl_3_0_cipher_suites": ("SSLv3", True),
        "tls_1_0_cipher_suites": ("TLSv1.0", True),
        "tls_1_1_cipher_suites": ("TLSv1.1", True),
        "tls_1_2_cipher_suites": ("TLSv1.2", False),
        "tls_1_3_cipher_suites": ("TLSv1.3", False),
    }

    for attr, (label, is_weak) in protocol_checks.items():
        scan_result = getattr(result.scan_result, attr, None)
        accepted = getattr(scan_result, "accepted_cipher_suites", None)
        if not accepted:
            continue

        supported_protocols.append(label)
        if is_weak:
            vulnerabilities.append(
                {
                    "type": "weak_protocol",
                    "detail": f"{label} 활성화됨",
                }
            )

    cert_expiry = None
    is_expired = False
    is_self_signed = False
    cert_info = getattr(result.scan_result, "certificate_info", None)
    deployments = getattr(cert_info, "certificate_deployments", []) if cert_info else []
    if deployments:
        leaf_cert = deployments[0].received_certificate_chain[0]
        expiry = leaf_cert.not_valid_after
        if expiry.tzinfo is None:
            now = datetime.utcnow()
        else:
            now = datetime.now(timezone.utc)

        cert_expiry = expiry.strftime("%Y-%m-%d")
        is_expired = expiry < now
        is_self_signed = leaf_cert.issuer == leaf_cert.subject

    if is_expired:
        vulnerabilities.append(
            {
                "type": "expired_cert",
                "detail": f"인증서 만료: {cert_expiry}",
            }
        )
    if is_self_signed:
        vulnerabilities.append(
            {
                "type": "self_signed_certificate",
                "detail": "자체 서명 인증서 사용 중",
            }
        )

    return {
        "supported_protocols": supported_protocols,
        "vulnerabilities": vulnerabilities,
        "cert_expiry": cert_expiry,
        "is_expired": is_expired,
        "is_self_signed": is_self_signed,
    }


def _scan(target: str):
    server_location = ServerNetworkLocation(hostname=target, port=443)
    scan_request = ServerScanRequest(
        server_location=server_location,
        scan_commands={
            ScanCommand.SSL_2_0_CIPHER_SUITES,
            ScanCommand.SSL_3_0_CIPHER_SUITES,
            ScanCommand.TLS_1_0_CIPHER_SUITES,
            ScanCommand.TLS_1_1_CIPHER_SUITES,
            ScanCommand.TLS_1_2_CIPHER_SUITES,
            ScanCommand.TLS_1_3_CIPHER_SUITES,
            ScanCommand.CERTIFICATE_INFO,
        },
    )
    scanner = Scanner()
    scanner.queue_scans([scan_request])
    return list(scanner.get_results())[0]
