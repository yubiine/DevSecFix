# Step 5 — 매핑 로직 + LLM 연동

## 목표
취약점 유형에 맞는 코드 스니펫을 자동으로 연결(Rule-based)하고,
DB에 없는 취약점은 Gemini API로 동적 생성(LLM-based)한다.
두 방식을 결합한 하이브리드 해결책 생성 로직을 완성한다.

## 완료 기준 체크리스트

- [ ] `mapper.py` — vuln_type으로 snippets 테이블 조회 및 매핑 확인
- [ ] DB에 스니펫 있는 취약점 → Rule-based 즉시 반환 확인
- [ ] DB에 스니펫 없는 취약점 → Gemini API 호출하여 동적 생성 확인
- [ ] LLM 응답 신뢰도 낮을 시 "전문가 확인 권장" 경고 포함 확인
- [ ] `GET /scan/{task_id}/report` 응답에 스니펫 포함 확인
- [ ] Gemini API 키 없을 시 OpenAI fallback 동작 확인

---

## 만들어야 할 파일 목록

```
backend/
├── core/
│   ├── mapper.py       ← Rule-based 매핑 로직
│   └── llm.py          ← Gemini/OpenAI 추상화 레이어
└── routers/
    └── report.py       ← GET /scan/{task_id}/report
```

---

## 상세 구현 가이드

### mapper.py — 하이브리드 매핑 로직

```python
async def get_snippet_for_vulnerability(
    vuln_type: str,
    server_type: str = "nginx",
    context: dict = {}
) -> dict:
    """
    처리 흐름:
    1. snippets 테이블에서 vuln_type으로 조회
    2. 있으면 → Rule-based 즉시 반환 (source: "db")
    3. 없으면 → LLM 동적 생성 (source: "llm")

    반환 형식:
    {
      "vuln_type": "missing_hsts",
      "source": "db" | "llm",
      "server_type": "nginx",
      "title": "HSTS 헤더 추가",
      "code": "add_header Strict-Transport-Security ...",
      "warning": null | "전문가 확인 권장: LLM 생성 코드입니다."
    }
    """
```

### llm.py — Gemini/OpenAI 추상화 레이어

```python
class LLMClient:
    """
    Gemini 우선, 실패 시 OpenAI로 자동 fallback
    """
    def __init__(self):
        self.gemini_key = settings.GEMINI_API_KEY
        self.openai_key = settings.OPENAI_API_KEY

    async def generate_snippet(
        self,
        vuln_type: str,
        vuln_detail: str,
        server_type: str,
        server_version: str = ""
    ) -> dict:
        prompt = self._build_prompt(vuln_type, vuln_detail, server_type, server_version)
        # Gemini 시도 → 실패 시 OpenAI fallback
```

### LLM 프롬프트 설계 (Hallucination 방지)

```
[시스템 프롬프트]
당신은 서버 보안 설정 전문가입니다.
반드시 JSON 형식으로만 응답하세요. 다른 설명은 포함하지 마세요.

[유저 프롬프트]
다음 보안 취약점에 대한 {server_type} 서버 설정 코드를 생성하세요.

취약점 유형: {vuln_type}
취약점 설명: {vuln_detail}
서버 종류: {server_type}
서버 버전: {server_version} (없으면 최신 안정 버전 기준)

응답 형식:
{
  "title": "설정 제목",
  "code": "실제 설정 코드만",
  "description": "이 설정이 하는 일 한 줄 설명",
  "confidence": 0.0 ~ 1.0  // 0.8 미만이면 전문가 확인 권장
}

주의: 코드는 즉시 붙여넣기 가능한 형태로, 주석 최소화.
```

### 신뢰도 기준

```python
CONFIDENCE_THRESHOLD = 0.8

if response["confidence"] < CONFIDENCE_THRESHOLD:
    warning = "전문가 확인 권장: LLM 생성 코드입니다. 적용 전 반드시 검토하세요."
else:
    warning = None
```

### GET /scan/{task_id}/report 응답 형식

```json
{
  "taskId": "uuid",
  "target": "https://example.com",
  "securityGrade": "D",
  "scannedAt": "2025-01-01T00:00:00",
  "vulnerabilities": [
    {
      "type": "missing_hsts",
      "title": "HSTS 헤더 누락",
      "severity": "high",
      "cvssScore": 7.5,
      "snippet": {
        "source": "db",
        "serverType": "nginx",
        "title": "HSTS 헤더 추가 (Nginx)",
        "code": "add_header Strict-Transport-Security ...",
        "warning": null
      }
    }
  ]
}
```

---

## 동작 확인 명령어

```bash
# Rule-based 매핑 테스트
docker exec -it devsecfix-backend python -c "
import asyncio
from core.mapper import get_snippet_for_vulnerability
result = asyncio.run(get_snippet_for_vulnerability('missing_hsts', 'nginx'))
print(result)
"

# LLM 생성 테스트 (DB에 없는 유형)
docker exec -it devsecfix-backend python -c "
import asyncio
from core.mapper import get_snippet_for_vulnerability
result = asyncio.run(get_snippet_for_vulnerability('unknown_vuln_type', 'nginx'))
print(result)
"

# 리포트 엔드포인트 테스트
curl http://localhost:8000/scan/{task_id}/report
```

---

## 주의사항

- LLM 생성 스니펫은 DB에 자동 저장하지 말 것 (검증 전 저장 금지)
- Gemini API 호출 실패 시 에러가 아닌 OpenAI로 자동 전환
- 두 API 모두 실패 시: `{"error": "해결책 자동 생성 실패, 전문가 확인 필요"}`
- API 키는 반드시 `.env`에서 로드, 코드에 하드코딩 금지

---

## 완료 후 다음 단계

체크리스트 전부 완료 시:
1. `CLAUDE.md`의 `Step 5` 체크박스를 `[x]`로 변경
2. `@docs/step-06-frontend.md` 참조하여 다음 단계 시작
