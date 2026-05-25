import httpx


# 체크할 보안 헤더 13개 목록
# missing   → 헤더가 아예 없으면 취약
# exposed   → 헤더가 있으면 취약 (정보 노출)
SECURITY_HEADERS = [
    {
        "name": "Strict-Transport-Security",
        "type": "missing",
        "severity": "high",
        "description": "HTTPS를 강제하지 않아 중간자 공격에 취약합니다.",
    },
    {
        "name": "Content-Security-Policy",
        "type": "missing",
        "severity": "high",
        "description": "CSP가 없어 XSS 공격에 취약합니다.",
    },
    {
        "name": "X-Frame-Options",
        "type": "missing",
        "severity": "medium",
        "description": "클릭재킹 공격에 취약합니다.",
    },
    {
        "name": "X-Content-Type-Options",
        "type": "missing",
        "severity": "medium",
        "description": "MIME 타입 스니핑 공격에 취약합니다.",
    },
    {
        "name": "Referrer-Policy",
        "type": "missing",
        "severity": "low",
        "description": "리퍼러 정보가 외부에 노출될 수 있습니다.",
    },
    {
        "name": "Permissions-Policy",
        "type": "missing",
        "severity": "low",
        "description": "카메라, 마이크 등 브라우저 기능 접근이 제한되지 않습니다.",
    },
    {
        "name": "X-XSS-Protection",
        "type": "missing",
        "severity": "low",
        "description": "구형 브라우저에서 XSS 필터가 비활성화되어 있습니다.",
    },
    {
        "name": "Cross-Origin-Opener-Policy",
        "type": "missing",
        "severity": "medium",
        "description": "탭 간 정보 유출 공격에 취약합니다.",
    },
    {
        "name": "Cross-Origin-Resource-Policy",
        "type": "missing",
        "severity": "medium",
        "description": "리소스가 다른 출처에서 무단으로 접근될 수 있습니다.",
    },
    {
        "name": "Cache-Control",
        "type": "missing",
        "severity": "low",
        "description": "민감한 정보가 브라우저에 캐시될 수 있습니다.",
    },
    {
        "name": "Server",
        "type": "exposed",
        "severity": "low",
        "description": "서버 소프트웨어 및 버전 정보가 노출되어 있습니다.",
    },
    {
        "name": "X-Powered-By",
        "type": "exposed",
        "severity": "low",
        "description": "사용 중인 기술 스택 정보가 노출되어 있습니다.",
    },
    {
        "name": "Access-Control-Allow-Origin",
        "type": "exposed",
        "severity": "high",
        "description": "CORS가 모든 출처(*)에 열려있어 취약합니다.",
    },
]


def check_headers(headers: dict) -> list[dict]:
    """
    응답 헤더를 받아서 취약점 목록을 반환합니다.
    헤더 키는 대소문자 구분 없이 비교합니다.
    """
    # 헤더 키를 소문자로 통일
    lower_headers = {k.lower(): v for k, v in headers.items()}

    vulnerabilities = []

    for rule in SECURITY_HEADERS:
        header_name = rule["name"].lower()
        header_value = lower_headers.get(header_name)

        if rule["type"] == "missing":
            # 헤더가 없으면 취약
            if header_value is None:
                vulnerabilities.append({
                    "header": rule["name"],
                    "type": "missing",
                    "severity": rule["severity"],
                    "description": rule["description"],
                    "current_value": None,
                })

        elif rule["type"] == "exposed":
            # Access-Control-Allow-Origin은 * 일 때만 취약
            if header_name == "access-control-allow-origin":
                if header_value == "*":
                    vulnerabilities.append({
                        "header": rule["name"],
                        "type": "exposed",
                        "severity": rule["severity"],
                        "description": rule["description"],
                        "current_value": header_value,
                    })
            # Server, X-Powered-By는 존재 자체가 취약
            elif header_value is not None:
                vulnerabilities.append({
                    "header": rule["name"],
                    "type": "exposed",
                    "severity": rule["severity"],
                    "description": rule["description"],
                    "current_value": header_value,
                })

    return vulnerabilities


async def run_header_check(url: str) -> dict:
    """
    URL에 요청을 보내고 보안 헤더를 분석합니다.
    """
    # URL에 스킴이 없으면 https 붙이기
    if not url.startswith(("http://", "https://")):
        url = "https://" + url

    async with httpx.AsyncClient(follow_redirects=True, timeout=10) as client:
        try:
            response = await client.get(url)
        except httpx.ConnectError:
            return {
                "success": False,
                "error": "서버에 연결할 수 없습니다.",
                "vulnerabilities": [],
            }
        except httpx.TimeoutException:
            return {
                "success": False,
                "error": "요청 시간이 초과되었습니다.",
                "vulnerabilities": [],
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "vulnerabilities": [],
            }

    vulnerabilities = check_headers(dict(response.headers))
    # HSTS 값 검증
    hsts_value = dict(response.headers).get("strict-transport-security")
    if hsts_value:
        max_age = 0
        for part in hsts_value.split(";"):
            part = part.strip()
            if part.startswith("max-age="):
                try:
                    max_age = int(part.split("=")[1])
                except ValueError:
                    pass
        if max_age < 31536000:  # 1년 미만
            vulnerabilities.append({
                "header": "Strict-Transport-Security",
                "type": "invalid_value",
                "severity": "medium",
                "description": f"HSTS max-age가 너무 짧습니다({max_age}초). 최소 31536000(1년) 이상을 권장합니다.",
                "current_value": hsts_value,
            })
    # 심각도별 개수 집계
    summary = {"high": 0, "medium": 0, "low": 0}
    for v in vulnerabilities:
        summary[v["severity"]] += 1

    return {
        "success": True,
        "status_code": response.status_code,
        "vulnerabilities": vulnerabilities,
        "summary": summary,
        "total": len(vulnerabilities),
    }