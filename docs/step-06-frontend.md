# Step 6 — UI/UX 개발

## 목표
React로 스캔 요청, 실시간 진행상황, 취약점 결과 대시보드, 상세 리포트 화면을 구현한다.

## 완료 기준 체크리스트

- [ ] ScanPage — URL 입력 및 소유권 인증 버튼 동작 확인
- [ ] ScanPage — 스캔 진행 중 Progress Bar 실시간 업데이트 확인
- [ ] DashboardPage — 보안 등급(A~F) 및 취약점 통계 차트 표시 확인
- [ ] ReportPage — 취약점별 코드 스니펫 복사 버튼 동작 확인
- [ ] 미인증 도메인 스캔 시도 시 안내 메시지 표시 확인
- [ ] PDF 다운로드 버튼 동작 확인

---

## 만들어야 할 파일 목록

```
frontend/src/
├── pages/
│   ├── ScanPage.jsx          ← URL 입력 + 인증 + 진행상황
│   ├── DashboardPage.jsx     ← 보안 등급 + 통계 차트
│   └── ReportPage.jsx        ← 취약점 목록 + 스니펫
├── components/
│   ├── ProgressBar.jsx       ← 실시간 진행 상태
│   ├── GradeCard.jsx         ← A~F 등급 표시 카드
│   ├── VulnCard.jsx          ← 취약점 카드 (severity 색상 구분)
│   ├── SnippetBlock.jsx      ← 코드 스니펫 + 복사 버튼
│   └── SeverityBadge.jsx     ← critical/high/medium/low 배지
├── api/
│   └── client.js             ← axios 기반 API 클라이언트
└── App.jsx                   ← 라우팅 설정
```

---

## 상세 구현 가이드

### 화면 흐름

```
① ScanPage
   URL 입력 → 소유권 인증 → 스캔 시작 → Progress Bar
        ↓ 완료
② DashboardPage
   보안 등급 카드 + 취약점 분포 차트 + PDF 다운로드
        ↓ 상세보기
③ ReportPage
   취약점 카드 목록 + 코드 스니펫 + 복사 버튼
```

### API 폴링 방식 (Progress Bar)

```javascript
// 스캔 상태를 3초마다 polling
const pollScanStatus = async (taskId) => {
  const interval = setInterval(async () => {
    const res = await api.get(`/scan/${taskId}`)
    setStatus(res.data.status)
    if (res.data.status === 'done' || res.data.status === 'failed') {
      clearInterval(interval)
    }
  }, 3000)
}
```

### 보안 등급별 색상

```
A — #22c55e (초록)
B — #84cc16 (연두)
C — #eab308 (노랑)
D — #f97316 (주황)
F — #ef4444 (빨강)
```

### severity별 색상

```
critical — #7c3aed (보라)
high     — #ef4444 (빨강)
medium   — #f97316 (주황)
low      — #eab308 (노랑)
info     — #6b7280 (회색)
```

### SnippetBlock.jsx 핵심 기능

```jsx
// 코드 복사 버튼
const handleCopy = () => {
  navigator.clipboard.writeText(code)
  setCopied(true)
  setTimeout(() => setCopied(false), 2000)
}

// LLM 생성 스니펫일 경우 경고 배너 표시
{warning && <div className="warning-banner">{warning}</div>}
```

### api/client.js

```javascript
import axios from 'axios'

const api = axios.create({
  baseURL: process.env.REACT_APP_API_URL || 'http://localhost:8000',
  timeout: 10000,
})

export default api
```

---

## 동작 확인 체크

```bash
# React 개발 서버 실행
cd frontend && npm start

# 빌드 확인
cd frontend && npm run build

# 접속
open http://localhost:3000
```

---

## 주의사항

- API URL은 환경변수(`REACT_APP_API_URL`)로 관리, 하드코딩 금지
- 코드 스니펫 표시 시 `<pre>` + `<code>` 태그 사용 (monospace 폰트)
- LLM 생성 스니펫에는 반드시 경고 배너 표시
- 스캔 중 페이지 이탈 시 polling 정리 (`useEffect` cleanup)

---

## 완료 후 다음 단계

체크리스트 전부 완료 시:
1. `CLAUDE.md`의 `Step 6` 체크박스를 `[x]`로 변경
2. `@docs/step-07-async-infra.md` 참조하여 다음 단계 시작
