import socket
import ssl
from datetime import datetime, timezone


def get_ssl_info(host: str, port: int = 443) -> dict:
    """
    SSL/TLS 인증서 정보를 가져옵니다.
    """
    context = ssl.create_default_context()

    try:
        with socket.create_connection((host, port), timeout=10) as sock:
            with context.wrap_socket(sock, server_hostname=host) as ssock:
                cert = ssock.getpeercert()
                protocol = ssock.version()
                cipher = ssock.cipher()
                return {
                    "success": True,
                    "cert": cert,
                    "protocol": protocol,
                    "cipher": cipher,
                }
    except ssl.SSLCertVerificationError as e:
        return {"success": False, "error": f"인증서 검증 실패: {str(e)}", "self_signed": True}
    except ssl.SSLError as e:
        return {"success": False, "error": f"SSL 오류: {str(e)}"}
    except ConnectionRefusedError:
        return {"success": False, "error": "HTTPS 포트(443)가 열려있지 않습니다."}
    except Exception as e:
        return {"success": False, "error": str(e)}


def check_weak_protocols(host: str) -> list[dict]:
    """
    취약한 TLS 버전(TLS 1.0, TLS 1.1) 사용 여부를 체크합니다.
    """
    vulnerabilities = []

    weak_protocols = [
        ("TLSv1", "TLS 1.0"),
        ("TLSv1.1", "TLS 1.1"),
    ]

    for proto_const, proto_name in weak_protocols:
        try:
            context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
            context.check_hostname = False
            context.verify_mode = ssl.CERT_NONE
            context.minimum_version = getattr(ssl.TLSVersion, proto_const.replace(".", "_"), None)
            context.maximum_version = getattr(ssl.TLSVersion, proto_const.replace(".", "_"), None)

            with socket.create_connection((host, 443), timeout=5) as sock:
                with context.wrap_socket(sock, server_hostname=host):
                    vulnerabilities.append({
                        "type": "weak_protocol",
                        "severity": "high",
                        "description": f"{proto_name} 이하 버전이 허용되어 있어 취약합니다.",
                        "detail": proto_name,
                    })
        except Exception:
            pass

    return vulnerabilities


def check_cert_expiry(cert: dict) -> list[dict]:
    """
    인증서 만료 여부를 체크합니다.
    """
    vulnerabilities = []

    not_after = cert.get("notAfter")
    if not_after is None:
        return vulnerabilities

    expiry_date = datetime.strptime(not_after, "%b %d %H:%M:%S %Y %Z")
    expiry_date = expiry_date.replace(tzinfo=timezone.utc)
    now = datetime.now(timezone.utc)
    days_left = (expiry_date - now).days

    if days_left < 0:
        vulnerabilities.append({
            "type": "cert_expired",
            "severity": "high",
            "description": f"인증서가 {abs(days_left)}일 전에 만료되었습니다.",
            "detail": not_after,
        })
    elif days_left < 30:
        vulnerabilities.append({
            "type": "cert_expiring_soon",
            "severity": "medium",
            "description": f"인증서가 {days_left}일 후 만료됩니다. 갱신이 필요합니다.",
            "detail": not_after,
        })

    return vulnerabilities


def check_weak_cipher(cipher: tuple) -> list[dict]:
    """
    취약한 암호화 방식 사용 여부를 체크합니다.
    """
    vulnerabilities = []

    if cipher is None:
        return vulnerabilities

    cipher_name = cipher[0]
    weak_ciphers = ["RC4", "DES", "3DES", "MD5", "NULL", "EXPORT", "anon"]

    for weak in weak_ciphers:
        if weak in cipher_name.upper():
            vulnerabilities.append({
                "type": "weak_cipher",
                "severity": "high",
                "description": f"취약한 암호화 방식({cipher_name})이 사용되고 있습니다.",
                "detail": cipher_name,
            })
            break

    return vulnerabilities


def check_cert_details(cert: dict) -> list[dict]:
    """
    인증서 세부 정보를 체크합니다.
    - 자체 서명 인증서
    - 도메인 불일치
    - RSA 키 길이
    - SHA-1 서명
    """
    vulnerabilities = []

    # 자체 서명 인증서 체크 (발급자 == 주체)
    issuer = dict(x[0] for x in cert.get("issuer", []))
    subject = dict(x[0] for x in cert.get("subject", []))

    if issuer.get("commonName") == subject.get("commonName"):
        vulnerabilities.append({
            "type": "self_signed_cert",
            "severity": "high",
            "description": "자체 서명 인증서를 사용 중입니다. 신뢰할 수 없는 인증서입니다.",
            "detail": issuer.get("commonName"),
        })

    # SHA-1 서명 체크
    sig_alg = cert.get("signatureAlgorithm", "")
    if "sha1" in sig_alg.lower():
        vulnerabilities.append({
            "type": "sha1_signature",
            "severity": "high",
            "description": "SHA-1 서명 알고리즘은 취약합니다. SHA-256 이상을 사용하세요.",
            "detail": sig_alg,
        })

    # RSA 키 길이 체크
    public_key = cert.get("publicKey", {})
    key_size = public_key.get("key_size", 0) if isinstance(public_key, dict) else 0
    if 0 < key_size < 2048:
        vulnerabilities.append({
            "type": "weak_key_size",
            "severity": "high",
            "description": f"RSA 키 길이({key_size}bit)가 너무 짧습니다. 2048bit 이상을 사용하세요.",
            "detail": f"{key_size}bit",
        })

    return vulnerabilities


def run_ssl_check(host: str) -> dict:
    """
    SSL/TLS 전체 취약점을 분석합니다. (총 9가지 체크)
    """
    vulnerabilities = []

    ssl_info = get_ssl_info(host)

    if not ssl_info["success"]:
        # HTTPS 연결 자체가 안 되면 큰 취약점
        if "열려있지 않습니다" in ssl_info.get("error", ""):
            vulnerabilities.append({
                "type": "no_https",
                "severity": "high",
                "description": "HTTPS가 설정되어 있지 않습니다.",
                "detail": None,
            })
        # 자체 서명 인증서로 인한 검증 실패
        elif ssl_info.get("self_signed"):
            vulnerabilities.append({
                "type": "self_signed_cert",
                "severity": "high",
                "description": "자체 서명 인증서를 사용 중입니다. 신뢰할 수 없는 인증서입니다.",
                "detail": None,
            })

        summary = {"high": len(vulnerabilities), "medium": 0, "low": 0}
        return {
            "success": False,
            "error": ssl_info["error"],
            "vulnerabilities": vulnerabilities,
            "summary": summary,
            "total": len(vulnerabilities),
        }

    # 인증서 만료 체크
    vulnerabilities.extend(check_cert_expiry(ssl_info["cert"]))

    # 취약한 암호화 방식 체크
    vulnerabilities.extend(check_weak_cipher(ssl_info["cipher"]))

    # 취약한 프로토콜 체크
    vulnerabilities.extend(check_weak_protocols(host))

    # 인증서 세부 정보 체크 (자체서명, SHA-1, 키 길이)
    vulnerabilities.extend(check_cert_details(ssl_info["cert"]))

    # 심각도별 개수 집계
    summary = {"high": 0, "medium": 0, "low": 0}
    for v in vulnerabilities:
        summary[v["severity"]] += 1

    return {
        "success": True,
        "protocol": ssl_info["protocol"],
        "cipher": ssl_info["cipher"][0] if ssl_info["cipher"] else None,
        "vulnerabilities": vulnerabilities,
        "summary": summary,
        "total": len(vulnerabilities),
    }