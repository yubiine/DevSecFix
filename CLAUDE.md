## AI 행동 지침 (MUST FOLLOW)

- 대화 시작 시 현재 진행 단계를 CLAUDE.md에서 확인할 것
- Step 작업 시작 전 해당 docs/step-XX.md 파일을 반드시 읽을 것
- 설명만 하지 말고 즉시 파일 생성 및 명령어 실행할 것
- 완료 기준 체크리스트를 하나씩 실행하며 체크할 것
- 질문하지 말고 문서에 명시된 대로 진행할 것
- 한국어로 답변할 것

# DevSecFix

보안 취약점 자동 탐지 및 해결책 제안 시스템.
배포된 서버 URL을 입력하면 취약점을 스캔하고, 즉시 적용 가능한 Nginx/Apache 설정 코드를 자동 생성한다.

- **팀:** EMPTY (이은빈, 김유빈)
- **전체 기획:** `@docs/project-overview.md`

---

## 기술 스택

```
Frontend  : React 18
Backend   : FastAPI (Python 3.11)
DB        : PostgreSQL 15
Queue     : Redis 7 + Celery 5
스캔 툴   : nmap, sslyze, requests
LLM       : Gemini API (기본) / OpenAI (대체)
인프라    : Docker Compose
```

---

## 디렉토리 구조

```
devsecfix/
├── CLAUDE.md
├── docker-compose.yml
├── .env
├── docs/
│   ├── project-overview.md
│   ├── step-01-env-setup.md
│   ├── step-02-api-skeleton.md
│   ├── step-03-scan-engine.md
│   ├── step-04-parsing-db.md
│   ├── step-05-mapping-llm.md
│   ├── step-06-frontend.md
│   ├── step-07-async-infra.md
│   └── step-08-final.md
├── frontend/
│   └── src/
│       ├── pages/
│       └── components/
├── backend/
│   ├── main.py
│   ├── routers/
│   ├── core/
│   │   ├── scanner/
│   │   ├── mapper.py
│   │   └── llm.py
│   ├── models/
│   ├── worker/
│   └── requirements.txt
├── db/
│   └── init.sql
└── tests/
    ├── vulnerable_servers/
    └── normal_servers/
```

---

## 코드 작성 규칙

- 파일명: `snake_case` (Python), `kebab-case` (React)
- 클래스명: `PascalCase`
- 함수/변수: `snake_case` (Python), `camelCase` (JS/React)
- 상수: `UPPER_SNAKE_CASE`
- 주석 및 커밋 메시지: **한국어**
- API 응답: 항상 JSON, 필드명 `camelCase`
- 브랜치명: `feature/설명` 또는 `fix/설명`

---

## 절대 하면 안 되는 것 (NEVER)

- 소유권 인증 우회하여 스캔 허용 — 미인증 대상은 무조건 403 반환
- LLM 생성 코드 스니펫을 검증 없이 DB에 저장
- `.env` 파일 커밋 — `.gitignore`에 반드시 포함
- `nmap --max-rate` 옵션 제거 — DoS 방지 필수
- API 키, DB 비밀번호 하드코딩

---

## 현재 진행 단계

> 작업 시작 전 반드시 현재 Step 문서를 @로 참조할 것
> 예시: `@docs/step-01-env-setup.md`

- [x] Step 1. 환경 세팅         → `@docs/step-01-env-setup.md`
- [ ] Step 2. API 뼈대 구축     → `@docs/step-02-api-skeleton.md`
- [ ] Step 3. 스캔 엔진 연동    → `@docs/step-03-scan-engine.md`
- [ ] Step 4. 파싱 및 DB 연동   → `@docs/step-04-parsing-db.md`
- [ ] Step 5. 매핑 로직 + LLM   → `@docs/step-05-mapping-llm.md`
- [ ] Step 6. UI/UX 개발        → `@docs/step-06-frontend.md`
- [ ] Step 7. 비동기 인프라     → `@docs/step-07-async-infra.md`
- [ ] Step 8. 최종 마무리       → `@docs/step-08-final.md`

---

## KPI

| 지표 | 목표 |
|---|---|
| 탐지율 | 90% 이상 (취약 서버 10종 중 9~10종) |
| 오탐율 | 10% 미만 (정상 서버 5종 중 0건 목표) |
| 처리속도 | 2분 이내 (스캔 + PDF 생성 포함) |
