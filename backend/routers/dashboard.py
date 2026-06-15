from datetime import date, datetime, timedelta

from fastapi import APIRouter, Depends
from sqlalchemy import desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from core.deps import get_current_user, get_db
from models.scan import Scan
from models.user import User
from models.vulnerability import Vulnerability
from schemas.dashboard import DashboardSummaryResponse

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


async def _count_today_scans(user_id, db: AsyncSession) -> int:
    today_start = datetime.combine(date.today(), datetime.min.time())
    result = await db.execute(
        select(func.count(Scan.id)).where(
            Scan.user_id == user_id,
            Scan.created_at >= today_start,
        )
    )
    return result.scalar()


@router.get("/summary", response_model=DashboardSummaryResponse)
async def get_dashboard_summary(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    six_months_ago = datetime.utcnow() - timedelta(days=180)

    # 1. 6개월간 스캔 히스토리 점수 추이
    scans_result = await db.execute(
        select(Scan)
        .where(
            Scan.user_id == current_user.id,
            Scan.created_at >= six_months_ago,
            Scan.status == "done",
        )
        .order_by(Scan.created_at)
    )
    scans = scans_result.scalars().all()

    score_trend = [
        {
            "date": s.created_at.strftime("%Y-%m"),
            "score": float(s.total_score) if s.total_score is not None else 0.0,
            "grade": s.security_grade or "N/A",
        }
        for s in scans
    ]

    # 2. 최근 10개 스캔에서 발견된 위험도별 취약점 수 합계
    recent_scan_ids = [s.id for s in scans[-10:]]
    severity_counts = {"critical": 0, "high": 0, "medium": 0, "low": 0}

    if recent_scan_ids:
        severity_result = await db.execute(
            select(Vulnerability.severity, func.count(Vulnerability.id))
            .where(Vulnerability.scan_id.in_(recent_scan_ids))
            .group_by(Vulnerability.severity)
        )
        for row in severity_result.fetchall():
            sev = row[0].lower() if row[0] else "low"
            if sev in severity_counts:
                severity_counts[sev] = row[1]

    # 3. 최근 5개 스캔 목록
    recent_result = await db.execute(
        select(Scan)
        .where(Scan.user_id == current_user.id)
        .order_by(desc(Scan.created_at))
        .limit(5)
    )
    recent_scans = recent_result.scalars().all()

    # 4. 오늘 사용 횟수 계산
    today_count = await _count_today_scans(current_user.id, db)

    return {
        "scoreTrend": score_trend,
        "severityCounts": {
            "critical": severity_counts.get("critical", 0),
            "high": severity_counts.get("high", 0),
            "medium": severity_counts.get("medium", 0),
            "low": severity_counts.get("low", 0),
        },
        "recentScans": [
            {
                "scanId": str(s.id),
                "targetUrl": s.target_url,
                "grade": s.security_grade,
                "createdAt": s.created_at.isoformat(),
            }
            for s in recent_scans
        ],
        "scanQuota": {
            "used": today_count,
            "limit": current_user.daily_scan_limit,
        },
    }
