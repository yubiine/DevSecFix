import secrets
from datetime import datetime

import dns.resolver
import httpx
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from fastapi.concurrency import run_in_threadpool
from jose import jwt, JWTError
from core.security import SECRET_KEY, ALGORITHM
from models.invalidated_token import InvalidatedToken

from core.deps import get_current_user, get_db
from core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)
from core.utils import extract_domain
from models.user import User
from models.verification import Verification
from schemas.auth import (
    LoginRequest,
    RefreshRequest,
    RegisterRequest,
    VerificationConfirmRequest,
    VerificationConfirmResponse,
    VerificationRequest,
    VerificationRequestResponse,
    LogoutRequest,
)

router = APIRouter(prefix="/auth", tags=["auth"])


# --- 인증 관련 API ---

@router.post("/register", status_code=201)
async def register(body: RegisterRequest, db: AsyncSession = Depends(get_db)):
    existing = await db.execute(select(User).where(User.email == body.email))
    if existing.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="이미 사용 중인 이메일입니다.",
        )

    hashed_pwd = await run_in_threadpool(hash_password, body.password)
    user = User(
        email=body.email,
        password_hash=hashed_pwd,
        name=body.name,
        daily_scan_limit=5,  # 기본 한도: 일일 5회
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return {"userId": str(user.id), "email": user.email}


@router.post("/login")
async def login(body: LoginRequest, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.email == body.email))
    user = result.scalar_one_or_none()

    is_valid = await run_in_threadpool(verify_password, body.password, user.password_hash) if user else False
    if not user or not is_valid:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="이메일 또는 비밀번호가 올바르지 않습니다.",
        )

    return {
        "accessToken": create_access_token(str(user.id)),
        "refreshToken": create_refresh_token(str(user.id)),
        "tokenType": "bearer",
    }


@router.post("/refresh")
async def refresh_token(body: RefreshRequest, db: AsyncSession = Depends(get_db)):
    # 1. 블랙리스트 토큰 확인
    blacklist_check = await db.execute(
        select(InvalidatedToken).where(InvalidatedToken.token == body.refresh_token)
    )
    if blacklist_check.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="이미 로그아웃되었거나 유효하지 않은 Refresh Token입니다.",
        )

    try:
        user_id = decode_token(body.refresh_token, expected_type="refresh")
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="유효하지 않은 Refresh Token입니다.",
        )

    from uuid import UUID
    try:
        uuid_obj = UUID(user_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="유효하지 않은 사용자 ID입니다.",
        )

    user = await db.get(User, uuid_obj)
    if user is None or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="사용자를 찾을 수 없거나 계정이 비활성화되어 있습니다.",
        )

    return {
        "accessToken": create_access_token(str(user.id)),
        "tokenType": "bearer",
    }


@router.get("/me")
async def get_me(current_user: User = Depends(get_current_user)):
    return {
        "userId": str(current_user.id),
        "email": current_user.email,
        "name": current_user.name,
        "dailyScanLimit": current_user.daily_scan_limit,
        "createdAt": current_user.created_at.isoformat(),
    }


@router.post("/logout")
async def logout(body: LogoutRequest, db: AsyncSession = Depends(get_db)):
    try:
        payload = jwt.decode(body.refresh_token, SECRET_KEY, algorithms=[ALGORITHM])
        if payload.get("type") != "refresh":
            raise JWTError("잘못된 토큰 타입입니다.")
        
        exp = payload.get("exp")
        if exp:
            expires_at = datetime.utcfromtimestamp(exp)
        else:
            from datetime import timedelta
            expires_at = datetime.utcnow() + timedelta(days=7)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="유효하지 않은 Refresh Token입니다.",
        )

    # 블랙리스트에 추가
    existing = await db.execute(
        select(InvalidatedToken).where(InvalidatedToken.token == body.refresh_token)
    )
    if not existing.scalar_one_or_none():
        invalidated = InvalidatedToken(
            token=body.refresh_token,
            expires_at=expires_at,
        )
        db.add(invalidated)
        await db.commit()

    return {"message": "Logged out successfully"}


# --- 도메인 소유권 검증 API ---

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
    url = f"https://{domain}/.well-known/devsecfix.txt"
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, timeout=5)
            return token in response.text
        except Exception:
            return False


@router.post("/verify/request", response_model=VerificationRequestResponse)
async def request_verification(
    payload: VerificationRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    domain = extract_domain(payload.domain)
    token = f"devsecfix-verify={secrets.token_urlsafe(24)}"

    result = await db.execute(
        select(Verification).where(
            Verification.domain == domain,
            Verification.user_id == current_user.id,
        )
    )
    verification = result.scalar_one_or_none()

    if verification is None:
        verification = Verification(
            user_id=current_user.id,
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


@router.post("/verify/confirm", response_model=VerificationConfirmResponse)
async def confirm_verification(
    payload: VerificationConfirmRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    domain = extract_domain(payload.domain)
    result = await db.execute(
        select(Verification).where(
            Verification.domain == domain,
            Verification.user_id == current_user.id,
        )
    )
    verification = result.scalar_one_or_none()

    if verification is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="인증 요청 내역이 없습니다.",
        )

    if verification.method == "dns":
        verified = await check_dns_token(domain, verification.token)
    else:
        verified = await check_file_token(domain, verification.token)

    if not verified:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="인증 토큰이 확인되지 않습니다.",
        )

    verification.is_verified = True
    verification.verified_at = datetime.utcnow()
    await db.commit()

    return VerificationConfirmResponse(verified=True)
