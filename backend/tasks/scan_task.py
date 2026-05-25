import asyncio
from uuid import UUID

from celery import shared_task

from core.database import AsyncSessionLocal
from models.scan import Scan
from tasks.header_check import run_header_check
from tasks.port_scan import run_port_scan
from tasks.ssl_check import run_ssl_check


# CVSS v3.1 기반 취약점 점수 매핑
# 각 취약점 type에 점수를 부여합니다 (0.0 ~ 10.0)
CVSS_SCORES = {
    # 헤더 취약점
    "missing_hsts": 7.4,
    "missing_csp": 6.1,
    "missing_x_frame_options": 4.3,
    "missing_x_content_type_options": 4.3,
    "missing_referrer_policy": 3.1,
    "missing_permissions_policy": 3.1,
    "missing_x_xss_protection": 3.1,
    "missing_corp": 4.3,
    "missing_coop": 4.3,
    "missing_cache_control": 3.1,
    "exposed_server": 3.1,
    "exposed_x_powered_by": 3.1,
    "exposed_cors": 7.4,

    # 포트 취약점
    "open_ftp": 7.4,
    "open_telnet": 9.8,
    "open_rdp": 9.8,
    "open_vnc": 8.8,
    "open_db": 9.8,       # MySQL, PostgreSQL, Redis 등
    "open_ssh": 5.3,
    "open_smtp": 5.3,

    # SSL 취약점
    "no_https": 7.4,
    "cert_expired": 7.4,
    "cert_expiring_soon": 4.3,
    "weak_protocol": 7.4,
    "weak_cipher": 7.4,
    "self_signed_cert": 6.8,
    "sha1_signature": 5.9,
    "weak_key_size": 5.9,
}

# severity 기본값 (CVSS 점수 기반)
def get_severity_from_cvss(score: float) -> str:
    if score >= 9.0:
        return "critical"
    elif score >= 7.0:
        return "high"
    elif score >= 4.0:
        return "medium"
    else:
        return "low"


@shared_task(name="tasks.run_scan")
def run_scan(scan_id: str):
    """
    Celery 태스크: 스캔 전체 실행
    header_check + port_scan + ssl_check 를 한번에 실행하고
    결과를 DB에 저장합니다.
    """
    asyncio.run(_run_scan_async(scan_id))


async def _run_scan_async(scan_id: str):
    """
    실제 스캔 로직 (비동기)
    """
    async with AsyncSessionLocal() as db:
        scan = await db.get(Scan, UUID(scan_id))
        if scan is None:
            return

        # 스캔 시작 - 상태를 running으로 변경
        scan.status = "running"
        await db.commit()

        try:
            target_url = scan.target_url
            host = scan.domain

            # header, ssl 동시 실행
            header_result, ssl_result = await asyncio.gather(
                run_header_check(target_url),
                asyncio.to_thread(run_ssl_check, host),
            )

            # nmap은 별도 실행 (동기 함수)
            port_result = await asyncio.to_thread(run_port_scan, host)

            # 결과 합치기 + CVSS 점수 적용
            result = _merge_results(header_result, port_result, ssl_result)

            scan.status = "completed"
            scan.result = result
            await db.commit()

        except Exception as e:
            scan.status = "failed"
            scan.result = {"error": str(e)}
            await db.commit()


def _get_cvss_score(vulnerability: dict) -> float:
    """
    취약점 타입에 맞는 CVSS 점수를 반환합니다.
    매핑에 없으면 severity 기반으로 기본값 반환합니다.
    """
    vuln_type = vulnerability.get("type", "")
    category = vulnerability.get("category", "")

    # 포트 취약점은 포트 번호로 구분
    if category == "port":
        port = vulnerability.get("port", 0)
        if port in [3306, 5432, 6379, 27017, 1433, 1521, 9200]:
            return CVSS_SCORES["open_db"]
        elif port in [3389]:
            return CVSS_SCORES["open_rdp"]
        elif port in [23]:
            return CVSS_SCORES["open_telnet"]
        elif port in [5900]:
            return CVSS_SCORES["open_vnc"]
        elif port in [21]:
            return CVSS_SCORES["open_ftp"]
        elif port in [22]:
            return CVSS_SCORES["open_ssh"]

    # 헤더 취약점은 헤더 이름으로 구분
    if category == "header":
        header = vulnerability.get("header", "").lower().replace("-", "_")
        key = f"missing_{header}" if vulnerability.get("type") == "missing" else f"exposed_{header}"
        if key in CVSS_SCORES:
            return CVSS_SCORES[key]

    # SSL 취약점
    if vuln_type in CVSS_SCORES:
        return CVSS_SCORES[vuln_type]

    # 매핑 없으면 severity 기반 기본값
    severity = vulnerability.get("severity", "low")
    defaults = {"critical": 9.0, "high": 7.0, "medium": 5.0, "low": 3.0}
    return defaults.get(severity, 3.0)


def _merge_results(
    header_result: dict,
    port_result: dict,
    ssl_result: dict,
) -> dict:
    """
    세 가지 스캔 결과를 하나로 합치고 CVSS 점수를 적용합니다.
    """
    all_vulnerabilities = []

    for v in header_result.get("vulnerabilities", []):
        all_vulnerabilities.append({**v, "category": "header"})

    for v in port_result.get("vulnerabilities", []):
        all_vulnerabilities.append({**v, "category": "port"})

    for v in ssl_result.get("vulnerabilities", []):
        all_vulnerabilities.append({**v, "category": "ssl"})

    # CVSS 점수 적용
    for v in all_vulnerabilities:
        score = _get_cvss_score(v)
        v["cvss_score"] = score
        v["severity"] = get_severity_from_cvss(score)

    # CVSS 점수 기반 심각도 집계
    summary = {"critical": 0, "high": 0, "medium": 0, "low": 0}
    for v in all_vulnerabilities:
        severity = v.get("severity", "low")
        if severity in summary:
            summary[severity] += 1

    # 보안 등급 계산 (CVSS 평균 점수 기반)
    grade = _calculate_grade(all_vulnerabilities)

    return {
        "grade": grade,
        "total_vulnerabilities": len(all_vulnerabilities),
        "summary": summary,
        "vulnerabilities": all_vulnerabilities,
        "details": {
            "header": header_result,
            "port": port_result,
            "ssl": ssl_result,
        },
    }


def _calculate_grade(vulnerabilities: list) -> str:
    """
    CVSS 평균 점수로 보안 등급을 계산합니다. (A~F)
    """
    if not vulnerabilities:
        return "A"

    # 최고 CVSS 점수 기준으로 등급 계산
    max_score = max(v.get("cvss_score", 0) for v in vulnerabilities)

    if max_score == 0:
        return "A"
    elif max_score < 4.0:
        return "B"
    elif max_score < 6.0:
        return "C"
    elif max_score < 7.0:
        return "D"
    elif max_score < 9.0:
        return "E"
    else:
        return "F"