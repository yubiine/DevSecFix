from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.deps import get_current_user, get_db
from models.user import User
from models.verification import Verification
from models.scan_schedule import ScanSchedule
from schemas.asset import AssetRequest

router = APIRouter(prefix="/assets", tags=["assets"])


@router.post("", status_code=201)
async def register_asset(
    body: AssetRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Verification).where(
            Verification.domain == body.domain,
            Verification.user_id == current_user.id,
            Verification.is_verified == True,
        )
    )
    verification = result.scalar_one_or_none()
    if not verification:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="소유권 인증이 완료된 도메인만 등록할 수 있습니다.",
        )

    return {"domain": body.domain, "verified": True}


@router.get("")
async def list_assets(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Verification).where(
            Verification.user_id == current_user.id,
            Verification.is_verified == True,
        )
    )
    assets = result.scalars().all()
    return [
        {
            "domain": a.domain,
            "verifiedAt": a.verified_at.isoformat() if a.verified_at else None,
        }
        for a in assets
    ]


@router.delete("/{domain}", status_code=204)
async def delete_asset(
    domain: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Verification).where(
            Verification.domain == domain,
            Verification.user_id == current_user.id,
        )
    )
    verification = result.scalar_one_or_none()
    if not verification:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="자산을 찾을 수 없습니다.",
        )

    # Delete verification record (asset)
    await db.delete(verification)

    # Disable all associated scan schedules for this domain
    schedules_result = await db.execute(
        select(ScanSchedule).where(
            ScanSchedule.domain == domain,
            ScanSchedule.user_id == current_user.id,
        )
    )
    for schedule in schedules_result.scalars().all():
        schedule.is_enabled = False

    await db.commit()
    return
