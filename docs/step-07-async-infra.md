# Step 7 — 비동기 인프라 고도화

## 목표
Celery + Redis로 대량 스캔 요청을 안정적으로 처리하고,
Rate Limiting으로 DoS 방지, 스캔 로그를 DB에 기록한다.

## 완료 기준 체크리스트

- [ ] 동시 스캔 요청 5개 처리 시 Worker 분산 처리 확인
- [ ] Rate Limiting — 동일 IP 분당 요청 10회 초과 시 429 반환 확인
- [ ] 스캔 로그(`scan_logs`) 테이블에 기록 확인 (누가/언제/어떤 대상)
- [ ] Worker 장애 시 자동 재시도(최대 3회) 동작 확인
- [ ] 스캔 타임아웃(5분) 초과 시 `failed` 처리 확인

---

## 만들어야 할 파일 목록

```
backend/
├── worker/
│   ├── tasks.py          ← Celery 태스크 (재시도 로직 추가)
│   └── celery_app.py     ← Celery 앱 설정 분리
└── core/
    └── rate_limiter.py   ← Redis 기반 Rate Limiting
```

---

## 상세 구현 가이드

### celery_app.py 설정

```python
from celery import Celery

celery_app = Celery("devsecfix")
celery_app.conf.update(
    broker_url=settings.REDIS_URL,
    result_backend=settings.REDIS_URL,
    task_serializer="json",
    result_serializer="json",
    task_time_limit=300,        # 5분 타임아웃
    task_soft_time_limit=270,   # 4분 30초에 경고
    worker_concurrency=4,       # 동시 처리 Worker 수
    task_acks_late=True,        # Worker 장애 시 재큐
)
```

### tasks.py — 재시도 로직

```python
@celery_app.task(
    bind=True,
    max_retries=3,
    default_retry_delay=10,   # 10초 후 재시도
)
def run_scan(self, task_id: str, target_url: str):
    try:
        # 스캔 실행
        ...
    except Exception as exc:
        # 최대 3회 재시도 후 failed 처리
        raise self.retry(exc=exc)
```

### scan_logs 테이블

```sql
CREATE TABLE scan_logs (
  id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  scan_id     UUID REFERENCES scans(id),
  ip_address  VARCHAR(45),
  target_url  VARCHAR(500),
  action      VARCHAR(50),   -- 'scan_started' | 'scan_done' | 'scan_failed'
  created_at  TIMESTAMP DEFAULT now()
);
```

### rate_limiter.py — Redis 기반

```python
import redis

async def check_rate_limit(ip: str, limit: int = 10, window: int = 60) -> bool:
    """
    동일 IP에서 분당 limit회 초과 시 False 반환
    Redis key: rate_limit:{ip}
    """
    key = f"rate_limit:{ip}"
    count = await redis_client.incr(key)
    if count == 1:
        await redis_client.expire(key, window)
    return count <= limit
```

---

## 동작 확인 명령어

```bash
# Worker 4개 동시 실행
docker exec -it devsecfix-worker \
  celery -A worker.celery_app worker --concurrency=4 --loglevel=info

# Celery 모니터링 (Flower)
docker exec -it devsecfix-worker \
  celery -A worker.celery_app flower --port=5555
open http://localhost:5555

# Rate Limiting 테스트 (11번째 요청에서 429 확인)
for i in {1..11}; do
  curl -X POST http://localhost:8000/scan \
    -H "Content-Type: application/json" \
    -d '{"targetUrl": "https://example.com"}'
  echo "요청 $i"
done

# 스캔 로그 확인
docker exec -it devsecfix-db psql -U postgres -d devsecfix \
  -c "SELECT * FROM scan_logs ORDER BY created_at DESC LIMIT 10;"
```

---

## 주의사항

- `task_time_limit=300` (5분) 초과 시 Celery가 강제 종료 → `failed` 처리
- Rate Limiting은 Nginx 레벨이 아닌 FastAPI 레벨에서 구현 (컨테이너 내부 요청도 포함)
- `worker_concurrency`는 서버 CPU 코어 수에 맞게 조정

---

## 완료 후 다음 단계

체크리스트 전부 완료 시:
1. `CLAUDE.md`의 `Step 7` 체크박스를 `[x]`로 변경
2. `@docs/step-08-final.md` 참조하여 다음 단계 시작
