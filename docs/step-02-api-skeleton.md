# Step 2 — API 뼈대 구축

## 목표
FastAPI 기반으로 스캔 요청을 받고 Task ID를 발급하는 엔드포인트를 구현한다.
소유권 인증(DNS TXT 레코드 / 파일 업로드) 로직을 설계하고,
미인증 요청은 반드시 403으로 차단한다.

## 완료 기준 체크리스트

- [ ] `POST /scan` → Task ID 발급 및 DB 저장 확인
- [ ] `GET /scan/{task_id}` → 스캔 상태 조회 확인
- [ ] `POST /auth/verify` → 소유권 인증 로직 동작 확인
- [ ] 미인증 대상 스캔 요청 시 403 반환 확인
- [ ] PostgreSQL에 `scans`, `verifications` 테이블 생성 확인
- [ ] Alembic 마이그레이션 적용 확인

---

## 만들어야 할 파일 목록

```
backend/
├── routers/
│   ├── __init__.py
│   ├── scan.py          ← POST /scan, GET /scan/{task_id}
│   └── auth.py          ← POST /auth/verify
├── models/
│   ├── __init__.py
│   ├── scan.py          ← Scan ORM 모델
│   └── verification.py  ← Verification ORM 모델
├── schemas/
│   ├── __init__.py
│   ├── scan.py          ← 요청/응답 Pydantic 스키마
│   └── auth.py
├── core/
│   └── deps.py          ← 공통 의존성 (DB 세션 등)
└── alembic/             ← DB 마이그레이션
    └── versions/
```

---

## 상세 구현 가이드

### DB 테이블 설계

**scans 테이블**
```
id          UUID PRIMARY KEY DEFAULT gen_random_uuid()
target_url  VARCHAR(500) NOT NULL
status      VARCHAR(20) DEFAULT 'pending'   -- pending | running | done | failed
result      JSONB                            -- 스캔 결과 저장
created_at  TIMESTAMP DEFAULT now()
updated_at  TIMESTAMP DEFAULT now()
```

**verifications 테이블**
```
id            UUID PRIMARY KEY DEFAULT gen_random_uuid()
domain        VARCHAR(255) NOT NULL UNIQUE
method        VARCHAR(20)   -- dns | file
is_verified   BOOLEAN DEFAULT false
verified_at   TIMESTAMP
created_at    TIMESTAMP DEFAULT now()
```

### API 엔드포인트 명세

**POST /scan**
```
Request:  { "targetUrl": "https://example.com" }
Response: { "taskId": "uuid", "status": "pending", "createdAt": "..." }
오류:     인증되지 않은 도메인 → 403 { "detail": "소유권 인증이 필요합니다." }
```

**GET /scan/{task_id}**
```
Response: { "taskId": "uuid", "status": "running", "result": null, "createdAt": "..." }
오류:     존재하지 않는 task_id → 404
```

**POST /auth/verify**
```
Request:  { "domain": "example.com", "method": "dns" | "file" }
Response: { "verified": true, "domain": "example.com" }
```

### 소유권 인증 로직

```
DNS 방식:
  1. 사용자에게 TXT 레코드 값 발급 (예: devsecfix-verify=abc123)
  2. DNS 조회로 TXT 레코드 존재 여부 확인
  3. 확인되면 verifications 테이블에 is_verified=true 저장

파일 방식:
  1. 사용자에게 파일명/내용 발급 (예: devsecfix-abc123.txt)
  2. https://도메인/devsecfix-abc123.txt GET 요청으로 내용 확인
  3. 확인되면 verifications 테이블에 is_verified=true 저장
```

### POST /scan 내부 처리 흐름

```
1. targetUrl에서 도메인 추출
2. verifications 테이블에서 해당 도메인 is_verified 확인
3. False → 403 반환
4. True  → scans 테이블에 레코드 생성 (status='pending')
5. Task ID(UUID) 반환
6. (Step 3에서) Celery 태스크 큐에 전달 예정
```

---

## 동작 확인 명령어

```bash
# 스캔 요청 (인증 전 → 403 확인)
curl -X POST http://localhost:8000/scan \
  -H "Content-Type: application/json" \
  -d '{"targetUrl": "https://example.com"}'

# 소유권 인증 요청
curl -X POST http://localhost:8000/auth/verify \
  -H "Content-Type: application/json" \
  -d '{"domain": "example.com", "method": "dns"}'

# 스캔 상태 조회
curl http://localhost:8000/scan/{task_id}

# Alembic 마이그레이션 실행
docker exec -it devsecfix-backend alembic upgrade head

# API 문서 확인
open http://localhost:8000/docs
```

---

## 주의사항

- 모든 ID는 UUID 사용 (int auto-increment 금지)
- DB 세션은 의존성 주입(`Depends`)으로 관리
- 라우터는 `app.include_router()`로 `main.py`에 등록
- 스키마(Pydantic)와 모델(SQLAlchemy)을 반드시 분리할 것

---

## 완료 후 다음 단계

체크리스트 전부 완료 시:
1. `CLAUDE.md`의 `Step 2` 체크박스를 `[x]`로 변경
2. `@docs/step-03-scan-engine.md` 참조하여 다음 단계 시작
