# Step 3 — 스캔 엔진 연동

## 목표
nmap, sslyze, requests를 실제로 호출하여 스캔을 수행하고,
원시 결과를 Python dict(JSON)로 정제해서 반환하는 스캔 엔진을 구현한다.
Celery 태스크와 연결하여 백그라운드에서 비동기로 실행되게 한다.

## 완료 기준 체크리스트

- [ ] `port_scan.py` — nmap 실행 후 열린 포트 목록 JSON 반환 확인
- [ ] `ssl_scan.py` — sslyze 실행 후 TLS 버전/인증서 만료 JSON 반환 확인
- [ ] `header_scan.py` — HTTP 보안 헤더 누락 목록 JSON 반환 확인
- [ ] Celery 태스크(`run_scan`)가 3개 스캐너를 순서대로 실행 확인
- [ ] 스캔 완료 후 `scans.status` → `done` 업데이트 확인
- [ ] 스캔 실패 시 `scans.status` → `failed` + 오류 메시지 저장 확인

---

## 만들어야 할 파일 목록

```
backend/
├── core/
│   └── scanner/
│       ├── __init__.py
│       ├── port_scan.py      ← nmap 래퍼
│       ├── ssl_scan.py       ← sslyze 래퍼
│       ├── header_scan.py    ← requests 기반 헤더 체크
│       └── orchestrator.py   ← 3개 스캐너 통합 실행
└── worker/
    ├── __init__.py
    └── tasks.py              ← Celery 태스크 정의
```

---

## 상세 구현 가이드

### port_scan.py

```python
import nmap

def run_port_scan(target: str) -> dict:
    """
    반환 형식:
    {
      "open_ports": [
        {"port": 80, "service": "http", "version": "nginx 1.18"},
        {"port": 443, "service": "https", "version": "..."},
        {"port": 22, "service": "ssh", "version": "OpenSSH 8.2"}
      ],
      "unexpected_ports": [22, 3306]  -- 웹서버에서 불필요한 포트
    }
    """
    nm = nmap.PortScanner()
    # --max-rate 필수 (DoS 방지)
    nm.scan(target, arguments="-sV --max-rate 100 -T3")
    # 결과 파싱 후 반환
```

**체크해야 할 위험 포트 목록**
```
22   (SSH)    — 외부 노출 여부 확인
3306 (MySQL)  — DB 직접 노출 위험
5432 (PgSQL)  — DB 직접 노출 위험
6379 (Redis)  — 인증 없이 노출 위험
27017 (Mongo) — 인증 없이 노출 위험
8080, 8443    — 개발 서버 포트 노출 여부
```

### ssl_scan.py

```python
from sslyze import ...

def run_ssl_scan(hostname: str) -> dict:
    """
    반환 형식:
    {
      "supported_protocols": ["TLSv1.2", "TLSv1.3"],
      "vulnerabilities": [
        {"type": "weak_protocol", "detail": "TLS 1.1 활성화됨"},
        {"type": "expired_cert", "detail": "인증서 만료: 2024-01-01"}
      ],
      "cert_expiry": "2025-12-31",
      "is_expired": false
    }
    """
```

**체크해야 할 항목**
```
- TLS 1.0 / TLS 1.1 활성화 여부 (취약 — 비활성화 권장)
- 인증서 만료 여부 및 만료 임박(30일 이내) 여부
- 자체 서명 인증서 여부
- 취약한 암호화 스위트 사용 여부
```

### header_scan.py

```python
import requests

def run_header_scan(url: str) -> dict:
    """
    반환 형식:
    {
      "missing_headers": [
        {"header": "Strict-Transport-Security", "severity": "high"},
        {"header": "Content-Security-Policy", "severity": "medium"},
        {"header": "X-Frame-Options", "severity": "medium"}
      ],
      "present_headers": ["X-Content-Type-Options"],
      "server_info_leaked": true   -- Server: nginx/1.18 노출 여부
    }
    """
```

**체크해야 할 보안 헤더 목록**
```
Strict-Transport-Security    (HSTS)     — severity: high
Content-Security-Policy      (CSP)      — severity: high
X-Frame-Options                         — severity: medium
X-Content-Type-Options                  — severity: medium
Referrer-Policy                         — severity: low
Permissions-Policy                      — severity: low
```

### orchestrator.py

```python
def run_full_scan(target_url: str) -> dict:
    """
    3개 스캐너 순서대로 실행 후 결과 통합
    반환 형식:
    {
      "target": "https://example.com",
      "scanned_at": "2025-01-01T00:00:00",
      "port_scan": { ... },
      "ssl_scan": { ... },
      "header_scan": { ... }
    }
    """
```

### worker/tasks.py

```python
from celery import Celery
from core.scanner.orchestrator import run_full_scan
from core.database import ...

celery_app = Celery("devsecfix", broker=REDIS_URL)

@celery_app.task
def run_scan(task_id: str, target_url: str):
    # 1. scans.status = 'running' 업데이트
    # 2. run_full_scan(target_url) 실행
    # 3. 결과를 scans.result(JSONB)에 저장
    # 4. scans.status = 'done' 업데이트
    # 실패 시: scans.status = 'failed' + 오류 메시지 저장
```

---

## 동작 확인 명령어

```bash
# Celery Worker 실행 (별도 터미널)
docker exec -it devsecfix-worker celery -A worker.tasks worker --loglevel=info

# 스캔 직접 테스트 (Python)
docker exec -it devsecfix-backend python -c "
from core.scanner.port_scan import run_port_scan
print(run_port_scan('scanme.nmap.org'))
"

# SSL 스캔 테스트
docker exec -it devsecfix-backend python -c "
from core.scanner.ssl_scan import run_ssl_scan
print(run_ssl_scan('scanme.nmap.org'))
"

# 헤더 스캔 테스트
docker exec -it devsecfix-backend python -c "
from core.scanner.header_scan import run_header_scan
print(run_header_scan('http://scanme.nmap.org'))
"
```

**테스트용 공개 허용 도메인**
```
scanme.nmap.org  — nmap 공식 테스트 서버 (스캔 허용)
badssl.com       — SSL 취약점 테스트 전용 서버
```

---

## 주의사항

- nmap 테스트는 반드시 `scanme.nmap.org` 또는 본인 소유 서버만 사용
- `--max-rate 100` 옵션 필수 — 제거 금지
- sslyze 비동기 API 사용 시 asyncio 이벤트 루프 충돌 주의
- 스캔 타임아웃: 포트 스캔 60초, SSL 30초, 헤더 10초로 제한

---

## 완료 후 다음 단계

체크리스트 전부 완료 시:
1. `CLAUDE.md`의 `Step 3` 체크박스를 `[x]`로 변경
2. `@docs/step-04-parsing-db.md` 참조하여 다음 단계 시작
