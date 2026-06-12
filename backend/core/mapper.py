from core.llm import llm_client


CONFIDENCE_THRESHOLD = 0.8


async def get_snippet_for_vulnerability(
    snippets_map: dict,
    vuln_type: str,
    vuln_detail: str,
    server_type: str = "nginx",
) -> dict:
    snippet = snippets_map.get(vuln_type)

    if snippet:
        return {
            "source": "db",
            "serverType": snippet.server_type,
            "title": snippet.title,
            "code": snippet.code,
            "description": "",
            "warning": None,
        }

    llm_result = await llm_client.generate_snippet(
        vuln_type=vuln_type,
        vuln_detail=vuln_detail,
        server_type=server_type,
    )

    confidence = llm_result.get("confidence", 0.0)
    warning = (
        "전문가 확인 권장: LLM 생성 코드입니다. 적용 전 반드시 검토하세요."
        if confidence < CONFIDENCE_THRESHOLD
        else None
    )

    return {
        "source": "llm",
        "serverType": server_type,
        "title": llm_result.get("title", ""),
        "code": llm_result.get("code", ""),
        "description": llm_result.get("description", ""),
        "warning": warning,
    }
