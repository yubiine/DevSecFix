import asyncio
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.deps import get_db
from core.mapper import get_snippet_for_vulnerability
from models.scan import Scan
from models.snippet import Snippet
from models.vulnerability import Vulnerability

router = APIRouter(tags=["report"])


@router.get("/scan/{task_id}/report")
async def get_scan_report(task_id: UUID, db: AsyncSession = Depends(get_db)):
    scan = await db.get(Scan, task_id)
    if not scan:
        raise HTTPException(status_code=404, detail="스캔 결과를 찾을 수 없습니다.")

    stmt = select(Vulnerability).where(Vulnerability.scan_id == task_id)
    result = await db.execute(stmt)
    vulns = result.scalars().all()

    vuln_types = [v.type for v in vulns]
    snippets_map = {}
    if vuln_types:
        snippets_result = await db.execute(
            select(Snippet).where(Snippet.vuln_type.in_(vuln_types))
        )
        for snippet in snippets_result.scalars().all():
            existing = snippets_map.get(snippet.vuln_type)
            if existing is None or snippet.server_type == "nginx":
                snippets_map[snippet.vuln_type] = snippet

    async def fetch_snippet(vuln: Vulnerability) -> dict:
        snippet = await get_snippet_for_vulnerability(
            snippets_map=snippets_map,
            vuln_type=vuln.type,
            vuln_detail=vuln.detail or "",
            server_type="nginx",
        )
        return {
            "type": vuln.type,
            "title": vuln.title,
            "detail": vuln.detail,
            "severity": vuln.severity,
            "cvssScore": float(vuln.cvss_score),
            "snippet": snippet,
        }

    vuln_results = await asyncio.gather(
        *[fetch_snippet(v) for v in vulns],
        return_exceptions=True,
    )

    clean_results = []
    for result_item in vuln_results:
        if isinstance(result_item, Exception):
            print(f"[report] 스니펫 조회 실패: {result_item}")
        else:
            clean_results.append(result_item)

    return {
        "taskId": str(scan.id),
        "target": scan.target_url,
        "status": scan.status,
        "securityGrade": scan.security_grade,
        "totalScore": float(scan.total_score) if scan.total_score else None,
        "scannedAt": scan.created_at.isoformat(),
        "vulnerabilities": clean_results,
    }
