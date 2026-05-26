from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.snippet import Snippet


# 포트 번호 → 취약점 타입 매핑
PORT_TO_VULN_TYPE = {
    21: "open_ftp",
    22: "open_ssh",
    23: "open_telnet",
    3389: "open_rdp",
    5900: "open_vnc",
    3306: "open_db",
    5432: "open_db",
    6379: "open_db",
    27017: "open_db",
    1433: "open_db",
    1521: "open_db",
    9200: "open_db",
}

# 헤더 이름 → 취약점 타입 매핑
HEADER_TO_VULN_TYPE = {
    "strict-transport-security": "missing_hsts",
    "content-security-policy": "missing_csp",
    "x-frame-options": "missing_x_frame_options",
    "x-content-type-options": "missing_x_content_type_options",
    "referrer-policy": "missing_referrer_policy",
    "permissions-policy": "missing_permissions_policy",
    "x-xss-protection": "missing_x_xss_protection",
    "cross-origin-opener-policy": "missing_coop",
    "cross-origin-resource-policy": "missing_corp",
    "cache-control": "missing_cache_control",
    "server": "exposed_server",
    "x-powered-by": "exposed_x_powered_by",
    "access-control-allow-origin": "exposed_cors",
}


def _get_vuln_type(vuln: dict) -> str:
    """
    취약점 딕셔너리에서 DB 조회용 vuln_type을 추출합니다.
    """
    category = vuln.get("category", "")
    vuln_type = vuln.get("type", "")

    # 포트 취약점
    if category == "port":
        port = vuln.get("port", 0)
        return PORT_TO_VULN_TYPE.get(port, "open_port")

    # 헤더 취약점
    if category == "header":
        header = vuln.get("header", "").lower()
        return HEADER_TO_VULN_TYPE.get(header, vuln_type)

    # SSL 취약점은 type 그대로 사용
    return vuln_type


async def get_snippets_for_vulnerability(
    db: AsyncSession,
    vuln_type: str,
    server_type: str = None,
) -> list[dict]:
    """
    취약점 타입에 맞는 스니펫을 DB에서 찾아 반환합니다.
    server_type이 없으면 해당 취약점의 모든 스니펫을 반환합니다.
    """
    query = select(Snippet).where(Snippet.vuln_type == vuln_type)

    if server_type:
        query = query.where(Snippet.server_type == server_type)

    result = await db.execute(query)
    snippets = result.scalars().all()

    return [
        {
            "id": str(snippet.id),
            "title": snippet.title,
            "server_type": snippet.server_type,
            "code": snippet.code,
            "description": snippet.description,
            "reference_url": snippet.reference_url,
        }
        for snippet in snippets
    ]


async def attach_snippets_to_vulnerabilities(
    db: AsyncSession,
    vulnerabilities: list[dict],
) -> list[dict]:
    """
    취약점 목록에 해당하는 스니펫을 자동으로 붙여줍니다.
    스니펫이 없는 경우 안내 메시지를 포함합니다.
    """
    result = []

    for vuln in vulnerabilities:
        vuln_type = _get_vuln_type(vuln)

        # 스니펫 조회
        snippets = await get_snippets_for_vulnerability(db, vuln_type)

        # 스니펫이 없는 경우 안내 메시지 추가
        if not snippets:
            snippets_info = {
                "available": False,
                "message": "이 취약점에 대한 해결책을 찾을 수 없습니다. 보안 전문가에게 문의하세요.",
                "snippets": [],
            }
        else:
            snippets_info = {
                "available": True,
                "message": f"{len(snippets)}개의 해결책이 있습니다.",
                "snippets": snippets,
            }

        vuln_with_snippet = {**vuln, "fix": snippets_info}
        result.append(vuln_with_snippet)

    return result


async def get_scan_result_with_snippets(
    db: AsyncSession,
    scan_result: dict,
) -> dict:
    """
    스캔 결과에 스니펫을 붙여서 최종 결과를 반환합니다.
    """
    vulnerabilities = scan_result.get("vulnerabilities", [])

    # 취약점에 스니펫 붙이기
    vulnerabilities_with_snippets = await attach_snippets_to_vulnerabilities(
        db, vulnerabilities
    )

    # 스니펫이 있는 취약점 수 계산
    fixable_count = sum(
        1 for v in vulnerabilities_with_snippets
        if v.get("fix", {}).get("available", False)
    )

    return {
        **scan_result,
        "vulnerabilities": vulnerabilities_with_snippets,
        "fixable_count": fixable_count,
        "unfixable_count": len(vulnerabilities_with_snippets) - fixable_count,
    }