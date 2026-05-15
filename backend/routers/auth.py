import secrets
from datetime import datetime

import dns.resolver
import httpx
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.deps import get_db
from core.utils import extract_domain
from models.verification import Verification
from schemas.auth import (
    VerificationConfirmRequest,
    VerificationConfirmResponse,
    VerificationRequest,
    VerificationRequestResponse,
)

router = APIRouter(prefix="/auth/verify", tags=["auth"])


async def check_dns_token(domain: str, token: str) -> bool:
    try:
        answers = dns.resolver.resolve(domain, "TXT")
        for rdata in answers:
            if token in str(rdata):
                return True
    except Exception:
        return False
    return False


async def check_file_token(domain: str, token: str) -> bool:
    url = f"https://{domain}/devsecfix-{token}.txt"
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, timeout=5)
            return token in response.text
        except Exception:
            return False


@router.post("/request", response_model=VerificationRequestResponse)
async def request_verification(
    payload: VerificationRequest,
    db: AsyncSession = Depends(get_db),
):
    domain = extract_domain(payload.domain)
    token = f"devsecfix-verify={secrets.token_urlsafe(24)}"

    result = await db.execute(
        select(Verification).where(Verification.domain == domain)
    )
    verification = result.scalar_one_or_none()

    if verification is None:
        verification = Verification(
            domain=domain,
            method=payload.method,
            token=token,
            is_verified=False,
        )
        db.add(verification)
    else:
        verification.method = payload.method
        verification.token = token
        verification.is_verified = False
        verification.verified_at = None

    await db.commit()
    return VerificationRequestResponse(domain=domain, token=token)


@router.post("/confirm", response_model=VerificationConfirmResponse)
async def confirm_verification(
    payload: VerificationConfirmRequest,
    db: AsyncSession = Depends(get_db),
):
    domain = extract_domain(payload.domain)
    result = await db.execute(
        select(Verification).where(Verification.domain == domain)
    )
    verification = result.scalar_one_or_none()

    if verification is None:
        raise HTTPException(status_code=404, detail="인증 요청 내역이 없습니다.")

    if verification.method == "dns":
        verified = await check_dns_token(domain, verification.token)
    else:
        verified = await check_file_token(domain, verification.token)

    if not verified:
        raise HTTPException(status_code=400, detail="인증 토큰이 확인되지 않습니다.")

    verification.is_verified = True
    verification.verified_at = datetime.utcnow()
    await db.commit()

    return VerificationConfirmResponse(verified=True)
