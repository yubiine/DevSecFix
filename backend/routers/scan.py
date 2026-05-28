from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from core.celery_app import celery_app
from core.deps import get_db
from core.utils import extract_domain
from models.scan import Scan
from models.verification import Verification
from models.vulnerability import Vulnerability
from schemas.scan import ScanCreateRequest, ScanDetailResponse, ScanResponse

router = APIRouter(prefix="/scan", tags=["scan"])


@router.post("", response_model=ScanResponse)
async def create_scan(
    payload: ScanCreateRequest,
    db: AsyncSession = Depends(get_db),
):
    domain = extract_domain(payload.target_url)
    result = await db.execute(
        select(Verification).where(
            Verification.domain == domain,
            Verification.is_verified.is_(True),
        )
    )

    if result.scalar_one_or_none() is None:
        raise HTTPException(status_code=403, detail="소유권 인증이 필요합니다.")

    scan = Scan(target_url=payload.target_url, domain=domain, status="pending")
    db.add(scan)
    await db.commit()
    await db.refresh(scan)

    celery_app.send_task("worker.run_scan", args=[str(scan.id)])

    return ScanResponse(
        taskId=scan.id,
        status=scan.status,
        result=scan.result,
        createdAt=scan.created_at,
    )


@router.get("/{task_id}", response_model=ScanDetailResponse)
async def get_scan(
    task_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    scan = await db.get(Scan, task_id)
    if scan is None:
        raise HTTPException(status_code=404, detail="스캔 작업을 찾을 수 없습니다.")

    stmt = (
        select(Vulnerability)
        .where(Vulnerability.scan_id == task_id)
        .options(selectinload(Vulnerability.snippets))
    )
    result = await db.execute(stmt)
    vulnerabilities = result.scalars().all()

    return ScanDetailResponse(
        taskId=scan.id,
        target=scan.target_url,
        status=scan.status,
        securityGrade=scan.security_grade,
        totalScore=float(scan.total_score) if scan.total_score is not None else None,
        scannedAt=scan.updated_at,
        vulnerabilities=[
            {
                "type": vulnerability.type,
                "title": vulnerability.title,
                "detail": vulnerability.detail,
                "severity": vulnerability.severity,
                "cvssScore": float(vulnerability.cvss_score),
                "snippets": [
                    {
                        "serverType": snippet.server_type,
                        "title": snippet.title,
                        "code": snippet.code,
                    }
                    for snippet in vulnerability.snippets
                ],
            }
            for vulnerability in vulnerabilities
        ],
    )
