# DevSecFix

허가된 도메인의 포트, TLS, 보안 헤더를 점검하고 취약점별 해결 방법을 제공하는 웹 보안 점검 서비스입니다.

## 주요 기능

- DNS TXT 또는 파일을 이용한 도메인 소유권 인증
- 포트, TLS, 보안 헤더 자동 점검
- 보안 등급과 CVSS 기반 취약점 리포트
- 매일·매주 자동 스캔 일정 관리
- 이메일, Slack, 카카오워크 알림 설정 및 발송 기록

## 실행 방법

Docker Desktop을 실행한 뒤 프로젝트 루트에서 실행합니다.

```bash
docker compose up --build
```

- 프론트엔드: `http://localhost:3000`
- 백엔드 API 문서: `http://localhost:8000/docs`
- PostgreSQL: `localhost:5432`

백엔드 컨테이너 시작 시 `alembic upgrade head`가 자동 실행되어 DB 테이블을 생성합니다.

## 발표용 데모 흐름

1. 메인 화면에서 `example.com` 보안 점검 시작
2. 스캔 진행 화면 확인
3. 보안 등급, CVSS, 해결 코드가 포함된 리포트 확인
4. 로그인 후 대시보드, 자동 스캔, 알림 설정 확인

데모 로그인 화면에는 발표용 이메일과 비밀번호가 자동 입력되어 있습니다. 현재 로그인 UI는 프론트 데모이며 실제 인증 API 연결은 후속 범위입니다.

## DB 구조

- `users`: 사용자 계정
- `verifications`: 도메인 소유권 인증
- `scans`: 스캔 기록과 보안 점수
- `vulnerabilities`: 발견된 취약점
- `snippets`: 취약점 해결 코드
- `scan_schedules`: 자동 스캔 일정
- `notification_settings`: 알림 채널과 조건
- `notification_logs`: 알림 발송 결과
