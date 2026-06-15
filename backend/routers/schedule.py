from datetime import time, datetime
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.deps import get_current_user, get_db
from models.scan_schedule import ScanSchedule
from models.user import User
from models.verification import Verification
from schemas.schedule import ScheduleCreateRequest, ScheduleResponse

router = APIRouter(prefix="/schedules", tags=["schedules"])


@router.post("", response_model=ScheduleResponse, status_code=201)
async def create_schedule(
    body: ScheduleCreateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    # Verify that the user has verified domain ownership
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
            detail="소유권 인증이 완료된 도메인만 스케줄을 생성할 수 있습니다.",
        )

    # Check if a schedule already exists for this domain and user
    sched_result = await db.execute(
        select(ScanSchedule).where(
            ScanSchedule.domain == body.domain,
            ScanSchedule.user_id == current_user.id,
        )
    )
    schedule = sched_result.scalar_one_or_none()

    if schedule is None:
        schedule = ScanSchedule(
            user_id=current_user.id,
            domain=body.domain,
            frequency=body.interval,  # Map interval to frequency
            run_time=time(0, 0),  # Default: midnight
            timezone="Asia/Seoul",
            is_enabled=True,
        )
        db.add(schedule)
    else:
        schedule.frequency = body.interval
        schedule.is_enabled = True
        schedule.updated_at = datetime.utcnow()

    await db.commit()
    await db.refresh(schedule)

    return ScheduleResponse(
        id=str(schedule.id),
        domain=schedule.domain,
        interval=schedule.frequency,
        isEnabled=schedule.is_enabled,
        createdAt=schedule.created_at.isoformat(),
        nextRunAt=schedule.next_run_at.isoformat() if schedule.next_run_at else None,
    )


@router.get("", response_model=list[ScheduleResponse])
async def list_schedules(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(ScanSchedule).where(
            ScanSchedule.user_id == current_user.id,
            ScanSchedule.is_enabled == True,
        )
    )
    schedules = result.scalars().all()
    return [
        ScheduleResponse(
            id=str(s.id),
            domain=s.domain,
            interval=s.frequency,
            isEnabled=s.is_enabled,
            createdAt=s.created_at.isoformat(),
            nextRunAt=s.next_run_at.isoformat() if s.next_run_at else None,
        )
        for s in schedules
    ]


@router.delete("/{schedule_id}", status_code=204)
async def delete_schedule(
    schedule_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    schedule = await db.get(ScanSchedule, schedule_id)
    if not schedule or schedule.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="스케줄을 찾을 수 없습니다.",
        )

    # Disable schedule
    schedule.is_enabled = False
    schedule.updated_at = datetime.utcnow()
    await db.commit()
    return
