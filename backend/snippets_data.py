"""
스니펫 초기 데이터 삽입 스크립트
실행 방법: python snippets_data.py
"""
import asyncio

from core.database import AsyncSessionLocal
from models.snippet import Snippet

SNIPPETS = [
    # =====================
    # 헤더 취약점 스니펫
    # =====================

    # HSTS 없음
    {
        "vuln_type": "missing_hsts",
        "severity": "high",
        "cvss_score": 7.4,
        "server_type": "nginx",
        "title": "HSTS 헤더 추가 (Nginx)",
        "code": """# nginx.conf 또는 사이트 설정 파일에 추가
server {
    listen 443 ssl;
    
    # HSTS 설정 (1년, 서브도메인 포함)
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains; preload" always;
}""",
        "description": "HSTS(HTTP Strict Transport Security)는 브라우저가 항상 HTTPS로 접속하도록 강제합니다.",
        "reference_url": "https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Strict-Transport-Security",
    },
    {
        "vuln_type": "missing_hsts",
        "severity": "high",
        "cvss_score": 7.4,
        "server_type": "apache",
        "title": "HSTS 헤더 추가 (Apache)",
        "code": """# .htaccess 또는 httpd.conf에 추가
# mod_headers 모듈 활성화 필요
<IfModule mod_headers.c>
    Header always set Strict-Transport-Security "max-age=31536000; includeSubDomains; preload"
</IfModule>""",
        "description": "HSTS(HTTP Strict Transport Security)는 브라우저가 항상 HTTPS로 접속하도록 강제합니다.",
        "reference_url": "https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Strict-Transport-Security",
    },

    # CSP 없음
    {
        "vuln_type": "missing_csp",
        "severity": "high",
        "cvss_score": 6.1,
        "server_type": "nginx",
        "title": "CSP 헤더 추가 (Nginx)",
        "code": """# nginx.conf에 추가
server {
    # 기본 CSP 설정 (필요에 따라 수정)
    add_header Content-Security-Policy "default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; img-src 'self' data:; font-src 'self';" always;
}""",
        "description": "CSP(Content Security Policy)는 XSS 공격을 방지하기 위해 허용된 리소스 출처를 제한합니다.",
        "reference_url": "https://developer.mozilla.org/en-US/docs/Web/HTTP/CSP",
    },
    {
        "vuln_type": "missing_csp",
        "severity": "high",
        "cvss_score": 6.1,
        "server_type": "apache",
        "title": "CSP 헤더 추가 (Apache)",
        "code": """# .htaccess 또는 httpd.conf에 추가
<IfModule mod_headers.c>
    Header always set Content-Security-Policy "default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; img-src 'self' data:; font-src 'self';"
</IfModule>""",
        "description": "CSP(Content Security Policy)는 XSS 공격을 방지하기 위해 허용된 리소스 출처를 제한합니다.",
        "reference_url": "https://developer.mozilla.org/en-US/docs/Web/HTTP/CSP",
    },

    # X-Frame-Options 없음
    {
        "vuln_type": "missing_x_frame_options",
        "severity": "medium",
        "cvss_score": 4.3,
        "server_type": "nginx",
        "title": "X-Frame-Options 헤더 추가 (Nginx)",
        "code": """# nginx.conf에 추가
server {
    add_header X-Frame-Options "DENY" always;
    # 같은 도메인은 허용하려면: add_header X-Frame-Options "SAMEORIGIN" always;
}""",
        "description": "X-Frame-Options는 클릭재킹 공격을 방지하기 위해 iframe 삽입을 제한합니다.",
        "reference_url": "https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/X-Frame-Options",
    },
    {
        "vuln_type": "missing_x_frame_options",
        "severity": "medium",
        "cvss_score": 4.3,
        "server_type": "apache",
        "title": "X-Frame-Options 헤더 추가 (Apache)",
        "code": """# .htaccess 또는 httpd.conf에 추가
<IfModule mod_headers.c>
    Header always set X-Frame-Options "DENY"
    # 같은 도메인은 허용하려면: Header always set X-Frame-Options "SAMEORIGIN"
</IfModule>""",
        "description": "X-Frame-Options는 클릭재킹 공격을 방지하기 위해 iframe 삽입을 제한합니다.",
        "reference_url": "https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/X-Frame-Options",
    },

    # X-Content-Type-Options 없음
    {
        "vuln_type": "missing_x_content_type_options",
        "severity": "medium",
        "cvss_score": 4.3,
        "server_type": "nginx",
        "title": "X-Content-Type-Options 헤더 추가 (Nginx)",
        "code": """# nginx.conf에 추가
server {
    add_header X-Content-Type-Options "nosniff" always;
}""",
        "description": "X-Content-Type-Options는 브라우저가 MIME 타입을 추측하지 못하도록 방지합니다.",
        "reference_url": "https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/X-Content-Type-Options",
    },
    {
        "vuln_type": "missing_x_content_type_options",
        "severity": "medium",
        "cvss_score": 4.3,
        "server_type": "apache",
        "title": "X-Content-Type-Options 헤더 추가 (Apache)",
        "code": """# .htaccess 또는 httpd.conf에 추가
<IfModule mod_headers.c>
    Header always set X-Content-Type-Options "nosniff"
</IfModule>""",
        "description": "X-Content-Type-Options는 브라우저가 MIME 타입을 추측하지 못하도록 방지합니다.",
        "reference_url": "https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/X-Content-Type-Options",
    },

    # Referrer-Policy 없음
    {
        "vuln_type": "missing_referrer_policy",
        "severity": "low",
        "cvss_score": 3.1,
        "server_type": "nginx",
        "title": "Referrer-Policy 헤더 추가 (Nginx)",
        "code": """# nginx.conf에 추가
server {
    add_header Referrer-Policy "strict-origin-when-cross-origin" always;
}""",
        "description": "Referrer-Policy는 외부 사이트로 리퍼러 정보가 유출되는 것을 방지합니다.",
        "reference_url": "https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Referrer-Policy",
    },
    {
        "vuln_type": "missing_referrer_policy",
        "severity": "low",
        "cvss_score": 3.1,
        "server_type": "apache",
        "title": "Referrer-Policy 헤더 추가 (Apache)",
        "code": """# .htaccess 또는 httpd.conf에 추가
<IfModule mod_headers.c>
    Header always set Referrer-Policy "strict-origin-when-cross-origin"
</IfModule>""",
        "description": "Referrer-Policy는 외부 사이트로 리퍼러 정보가 유출되는 것을 방지합니다.",
        "reference_url": "https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Referrer-Policy",
    },

    # Permissions-Policy 없음
    {
        "vuln_type": "missing_permissions_policy",
        "severity": "low",
        "cvss_score": 3.1,
        "server_type": "nginx",
        "title": "Permissions-Policy 헤더 추가 (Nginx)",
        "code": """# nginx.conf에 추가
server {
    add_header Permissions-Policy "camera=(), microphone=(), geolocation=(), payment=()" always;
}""",
        "description": "Permissions-Policy는 브라우저 기능(카메라, 마이크 등)에 대한 접근을 제한합니다.",
        "reference_url": "https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Permissions-Policy",
    },
    {
        "vuln_type": "missing_permissions_policy",
        "severity": "low",
        "cvss_score": 3.1,
        "server_type": "apache",
        "title": "Permissions-Policy 헤더 추가 (Apache)",
        "code": """# .htaccess 또는 httpd.conf에 추가
<IfModule mod_headers.c>
    Header always set Permissions-Policy "camera=(), microphone=(), geolocation=(), payment=()"
</IfModule>""",
        "description": "Permissions-Policy는 브라우저 기능(카메라, 마이크 등)에 대한 접근을 제한합니다.",
        "reference_url": "https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Permissions-Policy",
    },

    # X-XSS-Protection 없음
    {
        "vuln_type": "missing_x_xss_protection",
        "severity": "low",
        "cvss_score": 3.1,
        "server_type": "nginx",
        "title": "X-XSS-Protection 헤더 추가 (Nginx)",
        "code": """# nginx.conf에 추가
server {
    add_header X-XSS-Protection "1; mode=block" always;
}""",
        "description": "X-XSS-Protection은 구형 브라우저에서 XSS 필터를 활성화합니다.",
        "reference_url": "https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/X-XSS-Protection",
    },
    {
        "vuln_type": "missing_x_xss_protection",
        "severity": "low",
        "cvss_score": 3.1,
        "server_type": "apache",
        "title": "X-XSS-Protection 헤더 추가 (Apache)",
        "code": """# .htaccess 또는 httpd.conf에 추가
<IfModule mod_headers.c>
    Header always set X-XSS-Protection "1; mode=block"
</IfModule>""",
        "description": "X-XSS-Protection은 구형 브라우저에서 XSS 필터를 활성화합니다.",
        "reference_url": "https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/X-XSS-Protection",
    },

    # COOP 없음
    {
        "vuln_type": "missing_coop",
        "severity": "medium",
        "cvss_score": 4.3,
        "server_type": "nginx",
        "title": "Cross-Origin-Opener-Policy 헤더 추가 (Nginx)",
        "code": """# nginx.conf에 추가
server {
    add_header Cross-Origin-Opener-Policy "same-origin" always;
}""",
        "description": "COOP는 탭 간 정보 유출 공격을 방지합니다.",
        "reference_url": "https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Cross-Origin-Opener-Policy",
    },
    {
        "vuln_type": "missing_coop",
        "severity": "medium",
        "cvss_score": 4.3,
        "server_type": "apache",
        "title": "Cross-Origin-Opener-Policy 헤더 추가 (Apache)",
        "code": """# .htaccess 또는 httpd.conf에 추가
<IfModule mod_headers.c>
    Header always set Cross-Origin-Opener-Policy "same-origin"
</IfModule>""",
        "description": "COOP는 탭 간 정보 유출 공격을 방지합니다.",
        "reference_url": "https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Cross-Origin-Opener-Policy",
    },

    # CORP 없음
    {
        "vuln_type": "missing_corp",
        "severity": "medium",
        "cvss_score": 4.3,
        "server_type": "nginx",
        "title": "Cross-Origin-Resource-Policy 헤더 추가 (Nginx)",
        "code": """# nginx.conf에 추가
server {
    add_header Cross-Origin-Resource-Policy "same-origin" always;
}""",
        "description": "CORP는 리소스가 다른 출처에서 무단으로 접근되는 것을 방지합니다.",
        "reference_url": "https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Cross-Origin-Resource-Policy",
    },
    {
        "vuln_type": "missing_corp",
        "severity": "medium",
        "cvss_score": 4.3,
        "server_type": "apache",
        "title": "Cross-Origin-Resource-Policy 헤더 추가 (Apache)",
        "code": """# .htaccess 또는 httpd.conf에 추가
<IfModule mod_headers.c>
    Header always set Cross-Origin-Resource-Policy "same-origin"
</IfModule>""",
        "description": "CORP는 리소스가 다른 출처에서 무단으로 접근되는 것을 방지합니다.",
        "reference_url": "https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Cross-Origin-Resource-Policy",
    },

    # Cache-Control 없음
    {
        "vuln_type": "missing_cache_control",
        "severity": "low",
        "cvss_score": 3.1,
        "server_type": "nginx",
        "title": "Cache-Control 헤더 추가 (Nginx)",
        "code": """# nginx.conf에 추가
server {
    # 민감한 페이지에 적용
    add_header Cache-Control "no-store, no-cache, must-revalidate, proxy-revalidate" always;
}""",
        "description": "Cache-Control은 민감한 정보가 브라우저나 프록시에 캐시되는 것을 방지합니다.",
        "reference_url": "https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Cache-Control",
    },
    {
        "vuln_type": "missing_cache_control",
        "severity": "low",
        "cvss_score": 3.1,
        "server_type": "apache",
        "title": "Cache-Control 헤더 추가 (Apache)",
        "code": """# .htaccess 또는 httpd.conf에 추가
<IfModule mod_headers.c>
    Header always set Cache-Control "no-store, no-cache, must-revalidate, proxy-revalidate"
</IfModule>""",
        "description": "Cache-Control은 민감한 정보가 브라우저나 프록시에 캐시되는 것을 방지합니다.",
        "reference_url": "https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Cache-Control",
    },

    # Server 헤더 노출
    {
        "vuln_type": "exposed_server",
        "severity": "low",
        "cvss_score": 3.1,
        "server_type": "nginx",
        "title": "Server 헤더 숨기기 (Nginx)",
        "code": """# nginx.conf에 추가
http {
    server_tokens off;  # 버전 정보 숨기기
}""",
        "description": "Server 헤더에 서버 소프트웨어 정보가 노출되면 공격자가 취약점을 찾는데 활용할 수 있습니다.",
        "reference_url": "https://nginx.org/en/docs/http/ngx_http_core_module.html#server_tokens",
    },
    {
        "vuln_type": "exposed_server",
        "severity": "low",
        "cvss_score": 3.1,
        "server_type": "apache",
        "title": "Server 헤더 숨기기 (Apache)",
        "code": """# httpd.conf에 추가
ServerTokens Prod
ServerSignature Off""",
        "description": "Server 헤더에 서버 소프트웨어 정보가 노출되면 공격자가 취약점을 찾는데 활용할 수 있습니다.",
        "reference_url": "https://httpd.apache.org/docs/current/mod/core.html#servertokens",
    },

    # X-Powered-By 노출
    {
        "vuln_type": "exposed_x_powered_by",
        "severity": "low",
        "cvss_score": 3.1,
        "server_type": "nginx",
        "title": "X-Powered-By 헤더 숨기기 (Nginx)",
        "code": """# nginx.conf에 추가
server {
    # X-Powered-By 헤더 제거
    more_clear_headers 'X-Powered-By';
    # 또는 proxy_hide_header X-Powered-By; (프록시 사용 시)
}""",
        "description": "X-Powered-By 헤더는 사용 중인 기술 스택을 노출하여 공격자에게 정보를 제공합니다.",
        "reference_url": "https://owasp.org/www-project-secure-headers/",
    },
    {
        "vuln_type": "exposed_x_powered_by",
        "severity": "low",
        "cvss_score": 3.1,
        "server_type": "apache",
        "title": "X-Powered-By 헤더 숨기기 (Apache)",
        "code": """# .htaccess 또는 httpd.conf에 추가
<IfModule mod_headers.c>
    Header unset X-Powered-By
    Header always unset X-Powered-By
</IfModule>""",
        "description": "X-Powered-By 헤더는 사용 중인 기술 스택을 노출하여 공격자에게 정보를 제공합니다.",
        "reference_url": "https://owasp.org/www-project-secure-headers/",
    },

    # CORS 과도하게 열림
    {
        "vuln_type": "exposed_cors",
        "severity": "high",
        "cvss_score": 7.4,
        "server_type": "nginx",
        "title": "CORS 설정 수정 (Nginx)",
        "code": """# nginx.conf에 추가
server {
    # * 대신 특정 도메인만 허용
    add_header Access-Control-Allow-Origin "https://yourdomain.com" always;
    add_header Access-Control-Allow-Methods "GET, POST, OPTIONS" always;
    add_header Access-Control-Allow-Headers "Authorization, Content-Type" always;
}""",
        "description": "CORS를 모든 출처(*)에 열면 다른 사이트에서 API를 무단으로 호출할 수 있습니다.",
        "reference_url": "https://developer.mozilla.org/en-US/docs/Web/HTTP/CORS",
    },
    {
        "vuln_type": "exposed_cors",
        "severity": "high",
        "cvss_score": 7.4,
        "server_type": "apache",
        "title": "CORS 설정 수정 (Apache)",
        "code": """# .htaccess 또는 httpd.conf에 추가
<IfModule mod_headers.c>
    # * 대신 특정 도메인만 허용
    Header always set Access-Control-Allow-Origin "https://yourdomain.com"
    Header always set Access-Control-Allow-Methods "GET, POST, OPTIONS"
    Header always set Access-Control-Allow-Headers "Authorization, Content-Type"
</IfModule>""",
        "description": "CORS를 모든 출처(*)에 열면 다른 사이트에서 API를 무단으로 호출할 수 있습니다.",
        "reference_url": "https://developer.mozilla.org/en-US/docs/Web/HTTP/CORS",
    },
]


async def insert_snippets():
    async with AsyncSessionLocal() as db:
        for data in SNIPPETS:
            snippet = Snippet(**data)
            db.add(snippet)
        await db.commit()
        print(f"총 {len(SNIPPETS)}개 스니펫 삽입 완료!")


if __name__ == "__main__":
    asyncio.run(insert_snippets())