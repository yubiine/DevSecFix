# Step 4 — 파싱 및 DB 연동

## 목표
Step 3에서 받은 원시 스캔 결과를 CVSS v3.1 기반으로 점수화하고,
취약점별로 정형화된 JSON으로 파싱하여 DB에 저장한다.
코드 스니펫 시드 DB를 구축한다 (Rule-based 해결책의 핵심).

## 완료 기준 체크리스트

- [ ] `vulnerabilities` 테이블 생성 및 마이그레이션 확인
- [ ] `snippets` 테이블 생성 및 시드 데이터 10종 이상 입력 확인
- [ ] `parser.py` — 스캔 원시 결과 → 취약점 목록 변환 확인
- [ ] `scorer.py` — 각 취약점에 CVSS 점수 및 등급(A~F) 산출 확인
- [ ] 파싱 결과가 `vulnerabilities` 테이블에 정상 저장 확인
- [ ] `GET /scan/{task_id}` 응답에 파싱된 취약점 목록 포함 확인

---

## 만들어야 할 파일 목록

```
backend/
├── core/
│   ├── parser.py          ← 원시 결과 → 취약점 목록 변환
│   └── scorer.py          ← CVSS 점수 계산 및 보안 등급 산출
├── models/
│   ├── vulnerability.py   ← Vulnerability ORM 모델
│   └── snippet.py         ← Snippet ORM 모델
└── db/
    └── init.sql           ← 스니펫 시드 데이터
```

---

## 상세 구현 가이드

### DB 테이블 설계

**vulnerabilities 테이블**
```
id            UUID PRIMARY KEY DEFAULT gen_random_uuid()
scan_id       UUID REFERENCES scans(id)
type          VARCHAR(50)    -- 취약점 유형 key (아래 참고)
title         VARCHAR(200)   -- 사람이 읽을 수 있는 제목
detail        TEXT           -- 상세 설명
severity      VARCHAR(10)    -- critical | high | medium | low | info
cvss_score    DECIMAL(3,1)   -- 0.0 ~ 10.0
has_snippet   BOOLEAN DEFAULT false
created_at    TIMESTAMP DEFAULT now()
```

**snippets 테이블**
```
id              UUID PRIMARY KEY DEFAULT gen_random_uuid()
vuln_type       VARCHAR(50) UNIQUE   ← vulnerabilities.type과 매핑
server_type     VARCHAR(20)          -- nginx | apache | both
title           VARCHAR(200)
description     TEXT
code            TEXT                 ← 실제 설정 코드
verified        BOOLEAN DEFAULT true ← 수동 검증 완료 여부
created_at      TIMESTAMP DEFAULT now()
```

### 취약점 유형(type) 키 목록 — 반드시 이 키 사용

```
missing_hsts              — HSTS 헤더 누락
missing_csp               — CSP 헤더 누락
missing_x_frame_options   — X-Frame-Options 헤더 누락
missing_x_content_type    — X-Content-Type-Options 헤더 누락
weak_tls_protocol         — TLS 1.0/1.1 활성화
expired_certificate       — 인증서 만료
self_signed_certificate   — 자체 서명 인증서
exposed_ssh_port          — SSH 포트 외부 노출
exposed_db_port           — DB 포트 외부 노출
server_info_leaked        — 서버 버전 정보 노출
```

### parser.py

```python
def parse_scan_result(raw_result: dict) -> list[dict]:
    """
    orchestrator 결과 → 취약점 목록 변환
    반환 형식:
    [
      {
        "type": "missing_hsts",
        "title": "HSTS 헤더 누락",
        "detail": "Strict-Transport-Security 헤더가 설정되지 않았습니다.",
        "severity": "high"
      },
      ...
    ]
    """
```

### scorer.py — CVSS 점수 및 보안 등급

```python
# 취약점 유형별 기본 CVSS 점수 매핑
CVSS_SCORES = {
    "missing_hsts":            7.5,  # High
    "missing_csp":             6.1,  # Medium
    "missing_x_frame_options": 6.1,  # Medium
    "missing_x_content_type":  4.3,  # Medium
    "weak_tls_protocol":       7.5,  # High
    "expired_certificate":     7.5,  # High
    "self_signed_certificate": 5.3,  # Medium
    "exposed_ssh_port":        9.1,  # Critical
    "exposed_db_port":         9.8,  # Critical
    "server_info_leaked":      3.7,  # Low
}

def calculate_security_grade(vulnerabilities: list[dict]) -> str:
    """
    전체 취약점 기반 보안 등급 산출
    A: 취약점 없음
    B: low만 존재
    C: medium 존재
    D: high 존재
    F: critical 존재
    """
```

### 시드 데이터 예시 (db/init.sql)

```sql
INSERT INTO snippets (vuln_type, server_type, title, code) VALUES
(
  'missing_hsts', 'nginx',
  'HSTS 헤더 추가 (Nginx)',
  'add_header Strict-Transport-Security "max-age=31536000; includeSubDomains; preload" always;'
),
(
  'missing_hsts', 'apache',
  'HSTS 헤더 추가 (Apache)',
  'Header always set Strict-Transport-Security "max-age=31536000; includeSubDomains; preload"'
),
(
  'weak_tls_protocol', 'nginx',
  'TLS 1.0/1.1 비활성화 (Nginx)',
  'ssl_protocols TLSv1.2 TLSv1.3;'
),
-- ... 10종 이상 작성
;
```

---

## 동작 확인 명령어

```bash
# 파서 단위 테스트
docker exec -it devsecfix-backend python -c "
from core.parser import parse_scan_result
import json
raw = json.load(open('tests/fixtures/sample_scan_result.json'))
print(parse_scan_result(raw))
"

# 점수 계산 테스트
docker exec -it devsecfix-backend python -c "
from core.scorer import calculate_security_grade
vulns = [{'type': 'missing_hsts', 'severity': 'high'}]
print(calculate_security_grade(vulns))
"

# 시드 데이터 확인
docker exec -it devsecfix-db psql -U postgres -d devsecfix \
  -c "SELECT vuln_type, server_type, title FROM snippets;"
```

---

## 주의사항

- `vuln_type` 키는 위의 목록 외 임의로 추가 금지 (Step 5 매핑 로직과 연동)
- CVSS 점수는 CVSS v3.1 기준 — 임의 수정 금지
- 시드 스니펫 코드는 실제 동작 검증 후 `verified=true` 설정
- `vulnerabilities` 테이블은 `scan_id`로 `scans`에 외래키 연결

---

## 완료 후 다음 단계

체크리스트 전부 완료 시:
1. `CLAUDE.md`의 `Step 4` 체크박스를 `[x]`로 변경
2. `@docs/step-05-mapping-llm.md` 참조하여 다음 단계 시작
