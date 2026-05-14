# Step 8 — 최종 마무리

## 목표
통합 테스트로 KPI를 검증하고, PDF 리포트를 완성하고, 발표 자료를 준비한다.

## 완료 기준 체크리스트

### KPI 검증
- [ ] 취약 서버 10종 스캔 → 탐지율 90% 이상 확인
- [ ] 정상 서버 5종 스캔 → 오탐 0건 확인
- [ ] 단일 타겟 스캔 + PDF 생성 → 2분 이내 완료 확인

### PDF 리포트
- [ ] PDF에 보안 등급, 취약점 목록, 코드 스니펫 모두 포함 확인
- [ ] `GET /scan/{task_id}/pdf` 엔드포인트 동작 확인

### 발표 준비
- [ ] 테스트 결과 표 작성 (취약점 종류 / 탐지 여부 / 스니펫 제공 여부 / 소요 시간)
- [ ] 데모 시나리오 작성 및 리허설 완료

---

## 만들어야 할 파일 목록

```
backend/
├── core/
│   └── pdf_generator.py      ← PDF 생성 모듈
└── routers/
    └── report.py              ← GET /scan/{task_id}/pdf 엔드포인트 추가

tests/
├── vulnerable_servers/        ← Docker 취약 서버 10종
│   ├── docker-compose.yml
│   └── configs/               ← 각 서버별 설정 파일
├── normal_servers/            ← Docker 정상 서버 5종
│   └── docker-compose.yml
└── test_kpi.py                ← KPI 자동 검증 스크립트
```

---

## 상세 구현 가이드

### PDF 생성 (pdf_generator.py)

```python
# 권장 라이브러리: reportlab 또는 weasyprint
# weasyprint: HTML → PDF 변환 (스타일링 자유로움)

from weasyprint import HTML

def generate_report_pdf(scan_data: dict) -> bytes:
    """
    HTML 템플릿 렌더링 후 PDF 변환
    포함 내용:
    - 표지: 대상 URL, 스캔 일시, 보안 등급
    - 요약: 취약점 통계 (severity별 개수)
    - 상세: 취약점별 설명 + 코드 스니펫
    """
    html_content = render_template("report.html", data=scan_data)
    return HTML(string=html_content).write_pdf()
```

### 테스트 서버 구성 (취약 서버 10종)

```yaml
# tests/vulnerable_servers/docker-compose.yml

services:
  # 1. TLS 1.1 허용 서버
  tls11-server:
    image: nginx:alpine
    volumes: ["./configs/tls11.conf:/etc/nginx/nginx.conf"]

  # 2. HSTS 누락 서버
  no-hsts-server:
    image: nginx:alpine
    volumes: ["./configs/no-hsts.conf:/etc/nginx/nginx.conf"]

  # 3. CSP 누락 서버
  # 4. X-Frame-Options 누락
  # 5. 만료 인증서 서버
  # 6. 자체 서명 인증서
  # 7. SSH 포트 노출
  # 8. DB 포트 노출
  # 9. 서버 정보 노출
  # 10. X-Content-Type-Options 누락
```

### KPI 자동 검증 스크립트 (test_kpi.py)

```python
"""
결과 기록 형식:
| 취약점 종류              | 탐지 여부 | 스니펫 제공 | 소요 시간 |
|--------------------------|-----------|-------------|-----------|
| TLS 1.1 허용             | ✅        | ✅          | 45초      |
| HSTS 누락                | ✅        | ✅          | 38초      |
| ...                      |           |             |           |
"""

VULNERABLE_TARGETS = [
    "http://localhost:8081",  # tls11-server
    "http://localhost:8082",  # no-hsts-server
    # ...
]

NORMAL_TARGETS = [
    "http://localhost:9001",  # 정상 서버 1
    # ...
]

def run_kpi_test():
    detection_count = 0
    false_positive_count = 0
    # 각 서버 스캔 후 결과 집계
    # 탐지율, 오탐율, 소요 시간 출력
```

### 데모 시나리오

```
1. DevSecFix 소개 (1분)
   - 기존 툴의 한계 → DevSecFix의 차별점

2. 라이브 데모 (3분)
   - 취약한 테스트 서버 URL 입력
   - 소유권 인증 (파일 업로드 방식)
   - 스캔 실행 → Progress Bar 실시간 확인
   - 결과 대시보드: 등급 D, 취약점 5종 탐지
   - 코드 스니펫 복사 버튼 시연
   - PDF 리포트 다운로드

3. KPI 결과 발표 (1분)
   - 탐지율 X/10, 오탐율 X/5, 평균 소요 시간 X초
```

---

## 동작 확인 명령어

```bash
# 취약 서버 10종 실행
cd tests/vulnerable_servers && docker-compose up -d

# KPI 테스트 실행
docker exec -it devsecfix-backend python tests/test_kpi.py

# PDF 생성 테스트
curl http://localhost:8000/scan/{task_id}/pdf --output report.pdf
open report.pdf
```

---

## 최종 제출 체크리스트

- [ ] GitHub README.md 작성 (실행 방법, 팀원, KPI 결과 포함)
- [ ] `.env.example` 최신화
- [ ] 불필요한 `print`, `console.log` 제거
- [ ] 모든 API 키 `.env`에서만 로드 확인
- [ ] `docker-compose up --build` 한 번에 전체 실행 확인

---

## 🎉 완료

모든 체크리스트 완료 시 `CLAUDE.md`의 모든 Step을 `[x]`로 변경.
