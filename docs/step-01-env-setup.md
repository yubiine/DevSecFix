# Step 1 — 환경 세팅

## 목표
Python, FastAPI, 스캔 툴(nmap/sslyze), PostgreSQL, Redis를 Docker 기반으로 구성하고
전체 서비스가 `docker-compose up` 한 번으로 뜨는 것을 확인한다.

## 완료 기준 체크리스트

- ✅ `docker-compose up` 실행 시 전체 컨테이너 정상 기동
- ✅ `GET /health` → `{"status": "ok"}` 응답 확인
- ✅ FastAPI → PostgreSQL 연결 확인 (테이블 생성)
- ✅ FastAPI → Redis 연결 확인
- ✅ nmap, sslyze 컨테이너 내에서 실행 가능 확인
- ✅ `.env.example` 파일 작성 완료
- ✅ `.gitignore`에 `.env` 포함 확인

---

## 만들어야 할 파일 목록

```
devsecfix/
├── docker-compose.yml
├── .env.example
├── .gitignore
├── backend/
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── main.py              ← /health 엔드포인트 포함
│   └── core/
│       └── database.py      ← PostgreSQL 연결 설정
└── frontend/
    └── Dockerfile
```

---

## 상세 구현 가이드

### docker-compose.yml 구성 서비스

```yaml
services:
  frontend:   # React (port 3000)
  backend:    # FastAPI (port 8000)
  db:         # PostgreSQL 15 (port 5432)
  redis:      # Redis 7 (port 6379)
  worker:     # Celery Worker (백그라운드)
```

### backend/requirements.txt 포함 패키지

```
fastapi
uvicorn[standard]
sqlalchemy
asyncpg           # PostgreSQL 비동기 드라이버
alembic           # DB 마이그레이션
celery[redis]
redis
python-dotenv
httpx
sslyze
python-nmap
requests
pydantic-settings
```

### .env.example 작성 항목

```
POSTGRES_USER=
POSTGRES_PASSWORD=
POSTGRES_DB=devsecfix
POSTGRES_HOST=db
POSTGRES_PORT=5432

REDIS_URL=redis://redis:6379/0

GEMINI_API_KEY=
OPENAI_API_KEY=

BACKEND_PORT=8000
FRONTEND_PORT=3000
```

### backend/main.py 최소 구조

```python
from fastapi import FastAPI
from core.database import engine

app = FastAPI(title="DevSecFix API")

@app.get("/health")
async def health_check():
    return {"status": "ok"}
```

### backend/core/database.py

```python
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import declarative_base, sessionmaker
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    database_url: str
    class Config:
        env_file = ".env"

# DATABASE_URL 형식: postgresql+asyncpg://user:pass@host/db
```

---

## 동작 확인 명령어

```bash
# 전체 실행
docker-compose up --build

# 헬스체크
curl http://localhost:8000/health

# nmap 동작 확인 (backend 컨테이너 내부)
docker exec -it devsecfix-backend nmap --version

# sslyze 동작 확인
docker exec -it devsecfix-backend sslyze --version

# PostgreSQL 접속 확인
docker exec -it devsecfix-db psql -U ${POSTGRES_USER} -d devsecfix

# Redis 접속 확인
docker exec -it devsecfix-redis redis-cli ping
```

---

## 주의사항

- nmap은 root 권한이 필요하므로 backend Dockerfile에 `USER root` 또는 `--privileged` 설정 필요
- sslyze는 Python 패키지로 설치 (`pip install sslyze`)
- `asyncpg` 사용 시 DATABASE_URL 앞에 `postgresql+asyncpg://` 형식으로 작성
- `.env`는 절대 커밋하지 말 것 — `.env.example`만 커밋

---

## 완료 후 다음 단계

체크리스트 전부 완료 시:
1. `CLAUDE.md`의 `Step 1` 체크박스를 `[x]`로 변경
2. `@docs/step-02-api-skeleton.md` 참조하여 다음 단계 시작
