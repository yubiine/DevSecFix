from datetime import date, datetime
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from core.celery_app import celery_app
from core.deps import get_current_user, get_db
from core.utils import extract_domain
from models.scan import Scan
from models.user import User
from models.verification import Verification
from models.vulnerability import Vulnerability
from schemas.scan import ScanCreateRequest, ScanDetailResponse, ScanResponse

router = APIRouter(prefix="/scans", tags=["scans"])


async def check_daily_scan_quota(user: User, db: AsyncSession):
    """
    오늘 스캔 횟수가 user.daily_scan_limit 초과 시 429 발생
    """
    today_start = datetime.combine(date.today(), datetime.min.time())
    count_result = await db.execute(
        select(func.count(Scan.id)).where(
            Scan.user_id == user.id,
            Scan.created_at >= today_start,
        )
    )
    today_count = count_result.scalar()

    if today_count >= user.daily_scan_limit:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"일일 스캔 한도({user.daily_scan_limit}회)를 초과했습니다. 내일 다시 시도하세요.",
        )


@router.post("", response_model=ScanResponse, status_code=201)
async def create_scan(
    payload: ScanCreateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    # 일일 쿼터 확인
    await check_daily_scan_quota(current_user, db)

    domain = extract_domain(payload.target_url)
    result = await db.execute(
        select(Verification).where(
            Verification.domain == domain,
            Verification.user_id == current_user.id,
            Verification.is_verified.is_(True),
        )
    )

    if result.scalar_one_or_none() is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="소유권 인증이 필요합니다.",
        )

    scan = Scan(
        user_id=current_user.id,
        target_url=payload.target_url,
        domain=domain,
        status="pending",
    )
    db.add(scan)
    await db.commit()
    await db.refresh(scan)

    try:
        celery_app.send_task("worker.run_scan", args=[str(scan.id)])
    except Exception as e:
        scan.status = "failed"
        await db.commit()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"백그라운드 스캔 작업 큐잉에 실패했습니다. (원인: {str(e)})",
        )

    return ScanResponse(
        taskId=scan.id,
        status=scan.status,
        result=scan.result,
        createdAt=scan.created_at,
    )


@router.get("")
async def list_scans(
    skip: int = Query(default=0, ge=0, description="건너뛸 레코드 수"),
    limit: int = Query(default=20, ge=1, le=100, description="가져올 레코드 수 (최대 100)"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Scan)
        .where(Scan.user_id == current_user.id)
        .order_by(desc(Scan.created_at))
        .offset(skip)
        .limit(limit)
    )
    scans = result.scalars().all()

    total_result = await db.execute(
        select(func.count(Scan.id)).where(Scan.user_id == current_user.id)
    )
    total = total_result.scalar()

    return {
        "total": total,
        "skip": skip,
        "limit": limit,
        "items": [
            {
                "scanId": str(s.id),
                "targetUrl": s.target_url,
                "status": s.status,
                "securityGrade": s.security_grade,
                "totalScore": float(s.total_score) if s.total_score is not None else None,
                "createdAt": s.created_at.isoformat(),
            }
            for s in scans
        ],
    }


@router.get("/{scan_id}", response_model=ScanDetailResponse)
async def get_scan(
    scan_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    scan = await db.get(Scan, scan_id)
    if scan is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="스캔 작업을 찾을 수 없습니다.",
        )

    # 타인 스캔 접근 차단
    if scan.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="접근 권한이 없습니다.",
        )

    stmt = (
        select(Vulnerability)
        .where(Vulnerability.scan_id == scan_id)
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
