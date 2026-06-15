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
        "vuln_type": "missing_x_content_type",
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
        "vuln_type": "missing_x_content_type",
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
        "vuln_type": "server_info_leaked",
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
        "vuln_type": "server_info_leaked",
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

# =====================
    # 포트 취약점 스니펫
    # =====================

    # FTP (21번 포트)
    {
        "vuln_type": "open_ftp",
        "severity": "high",
        "cvss_score": 7.4,
        "server_type": "linux",
        "title": "FTP 포트 차단 (iptables)",
        "code": """# 외부에서 FTP 접근 차단
iptables -A INPUT -p tcp --dport 21 -j DROP

# 특정 IP만 허용하려면
# iptables -A INPUT -p tcp --dport 21 -s 허용할IP -j ACCEPT
# iptables -A INPUT -p tcp --dport 21 -j DROP

# 설정 저장
service iptables save""",
        "description": "FTP는 암호화되지 않아 데이터가 평문으로 전송됩니다. SFTP 또는 FTPS로 대체하거나 외부 접근을 차단하세요.",
        "reference_url": "https://wiki.archlinux.org/title/iptables",
    },

    # SSH (22번 포트)
    {
        "vuln_type": "exposed_ssh_port",
        "severity": "medium",
        "cvss_score": 5.3,
        "server_type": "linux",
        "title": "SSH 접근 제한 (iptables)",
        "code": """# 특정 IP만 SSH 허용 (권장)
iptables -A INPUT -p tcp --dport 22 -s 허용할IP -j ACCEPT
iptables -A INPUT -p tcp --dport 22 -j DROP

# 또는 SSH 포트 변경 (/etc/ssh/sshd_config)
# Port 2222  ← 기본 22에서 변경
# service sshd restart""",
        "description": "SSH가 외부에 노출되면 무차별 대입 공격에 취약합니다. 특정 IP만 허용하거나 포트를 변경하세요.",
        "reference_url": "https://www.ssh.com/academy/ssh/port",
    },

    # Telnet (23번 포트)
    {
        "vuln_type": "open_telnet",
        "severity": "high",
        "cvss_score": 9.8,
        "server_type": "linux",
        "title": "Telnet 포트 차단 및 서비스 비활성화",
        "code": """# Telnet 서비스 비활성화
systemctl stop telnet
systemctl disable telnet

# 포트 차단
iptables -A INPUT -p tcp --dport 23 -j DROP

# 설정 저장
service iptables save""",
        "description": "Telnet은 암호화가 전혀 없어 매우 위험합니다. 즉시 비활성화하고 SSH로 대체하세요.",
        "reference_url": "https://www.ssh.com/academy/ssh/telnet",
    },

    # DB 포트 외부 노출 차단 (MySQL, PostgreSQL, Redis, MongoDB, Elasticsearch 등)
    {
        "vuln_type": "exposed_db_port",
        "severity": "critical",
        "cvss_score": 9.8,
        "server_type": "linux",
        "title": "데이터베이스 포트 외부 접근 차단 (iptables)",
        "code": """# 1. MySQL (3306) 외부 접근 차단
iptables -A INPUT -p tcp --dport 3306 -j DROP

# 2. PostgreSQL (5432) 외부 접근 차단
iptables -A INPUT -p tcp --dport 5432 -j DROP

# 3. Redis (6379) 외부 접근 차단
iptables -A INPUT -p tcp --dport 6379 -j DROP

# 4. MongoDB (27017) 외부 접근 차단
iptables -A INPUT -p tcp --dport 27017 -j DROP

# 5. Elasticsearch (9200) 외부 접근 차단
iptables -A INPUT -p tcp --dport 9200 -j DROP

# * 설정 저장 (CentOS/RHEL)
# service iptables save
# * 설정 저장 (Ubuntu)
# netfilter-persistent save""",
        "description": "데이터베이스 포트가 외부에 노출되면 무단 데이터 접근 및 탈취 위험이 있습니다. 즉시 차단하세요.",
        "reference_url": "https://dev.mysql.com/doc/refman/8.0/en/security-guidelines.html",
    },
# =====================
    # SSL/TLS 취약점 스니펫
    # =====================

    # HTTPS 없음
    {
        "vuln_type": "no_https",
        "severity": "high",
        "cvss_score": 7.4,
        "server_type": "nginx",
        "title": "HTTPS 설정 (Nginx)",
        "code": """# nginx.conf에 추가
server {
    listen 80;
    server_name yourdomain.com;
    # HTTP를 HTTPS로 리다이렉트
    return 301 https://$host$request_uri;
}

server {
    listen 443 ssl;
    server_name yourdomain.com;

    ssl_certificate /etc/ssl/certs/yourdomain.crt;
    ssl_certificate_key /etc/ssl/private/yourdomain.key;

    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
}""",
        "description": "HTTPS는 데이터를 암호화하여 전송합니다. Let's Encrypt를 사용하면 무료로 SSL 인증서를 발급받을 수 있습니다.",
        "reference_url": "https://letsencrypt.org/getting-started/",
    },
    {
        "vuln_type": "no_https",
        "severity": "high",
        "cvss_score": 7.4,
        "server_type": "apache",
        "title": "HTTPS 설정 (Apache)",
        "code": """# httpd.conf 또는 ssl.conf에 추가
<VirtualHost *:80>
    ServerName yourdomain.com
    # HTTP를 HTTPS로 리다이렉트
    Redirect permanent / https://yourdomain.com/
</VirtualHost>

<VirtualHost *:443>
    ServerName yourdomain.com

    SSLEngine on
    SSLCertificateFile /etc/ssl/certs/yourdomain.crt
    SSLCertificateKeyFile /etc/ssl/private/yourdomain.key

    SSLProtocol TLSv1.2 TLSv1.3
    SSLCipherSuite HIGH:!aNULL:!MD5
</VirtualHost>""",
        "description": "HTTPS는 데이터를 암호화하여 전송합니다. Let's Encrypt를 사용하면 무료로 SSL 인증서를 발급받을 수 있습니다.",
        "reference_url": "https://letsencrypt.org/getting-started/",
    },

    # 인증서 만료
    {
        "vuln_type": "expired_certificate",
        "severity": "high",
        "cvss_score": 7.4,
        "server_type": "nginx",
        "title": "SSL 인증서 갱신 (Let's Encrypt)",
        "code": """# Certbot으로 인증서 갱신
# Certbot 설치
apt-get install certbot python3-certbot-nginx

# 인증서 갱신
certbot renew

# 자동 갱신 설정 (crontab)
# 0 0 * * * certbot renew --quiet && systemctl reload nginx""",
        "description": "만료된 SSL 인증서는 브라우저에서 보안 경고를 표시합니다. 즉시 갱신하세요.",
        "reference_url": "https://certbot.eff.org/",
    },
    {
        "vuln_type": "expired_certificate",
        "severity": "high",
        "cvss_score": 7.4,
        "server_type": "apache",
        "title": "SSL 인증서 갱신 (Let's Encrypt - Apache)",
        "code": """# Certbot으로 인증서 갱신
# Certbot 설치
apt-get install certbot python3-certbot-apache

# 인증서 갱신
certbot renew

# 자동 갱신 설정 (crontab)
# 0 0 * * * certbot renew --quiet && systemctl reload apache2""",
        "description": "만료된 SSL 인증서는 브라우저에서 보안 경고를 표시합니다. 즉시 갱신하세요.",
        "reference_url": "https://certbot.eff.org/",
    },

    # 인증서 곧 만료
    {
        "vuln_type": "cert_expiring_soon",
        "severity": "medium",
        "cvss_score": 4.3,
        "server_type": "nginx",
        "title": "SSL 인증서 만료 임박 - 갱신 필요 (Nginx)",
        "code": """# 인증서 만료일 확인
openssl x509 -enddate -noout -in /etc/ssl/certs/yourdomain.crt

# Certbot으로 미리 갱신
certbot renew --force-renewal

# 자동 갱신 설정 (만료 30일 전 자동 갱신)
# crontab -e
# 0 0 * * * certbot renew --quiet && systemctl reload nginx""",
        "description": "인증서가 30일 이내에 만료됩니다. 미리 갱신하여 서비스 중단을 방지하세요.",
        "reference_url": "https://certbot.eff.org/docs/using.html#renewing-certificates",
    },
    {
        "vuln_type": "cert_expiring_soon",
        "severity": "medium",
        "cvss_score": 4.3,
        "server_type": "apache",
        "title": "SSL 인증서 만료 임박 - 갱신 필요 (Apache)",
        "code": """# 인증서 만료일 확인
openssl x509 -enddate -noout -in /etc/ssl/certs/yourdomain.crt

# Certbot으로 미리 갱신
certbot renew --force-renewal

# 자동 갱신 설정
# crontab -e
# 0 0 * * * certbot renew --quiet && systemctl reload apache2""",
        "description": "인증서가 30일 이내에 만료됩니다. 미리 갱신하여 서비스 중단을 방지하세요.",
        "reference_url": "https://certbot.eff.org/docs/using.html#renewing-certificates",
    },

    # 취약한 TLS 버전
    {
        "vuln_type": "weak_tls_protocol",
        "severity": "high",
        "cvss_score": 7.4,
        "server_type": "nginx",
        "title": "취약한 TLS 버전 비활성화 (Nginx)",
        "code": """# nginx.conf에 추가
server {
    listen 443 ssl;

    # TLS 1.2, 1.3만 허용 (1.0, 1.1 비활성화)
    ssl_protocols TLSv1.2 TLSv1.3;

    # 강력한 암호화 설정
    ssl_ciphers ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384;
    ssl_prefer_server_ciphers off;
}""",
        "description": "TLS 1.0, 1.1은 취약점이 발견되어 deprecated 되었습니다. TLS 1.2 이상만 허용하세요.",
        "reference_url": "https://nginx.org/en/docs/http/ngx_http_ssl_module.html",
    },
    {
        "vuln_type": "weak_tls_protocol",
        "severity": "high",
        "cvss_score": 7.4,
        "server_type": "apache",
        "title": "취약한 TLS 버전 비활성화 (Apache)",
        "code": """# httpd.conf 또는 ssl.conf에 추가
<VirtualHost *:443>
    # TLS 1.2, 1.3만 허용
    SSLProtocol -all +TLSv1.2 +TLSv1.3

    # 강력한 암호화 설정
    SSLCipherSuite ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256
    SSLHonorCipherOrder off
</VirtualHost>""",
        "description": "TLS 1.0, 1.1은 취약점이 발견되어 deprecated 되었습니다. TLS 1.2 이상만 허용하세요.",
        "reference_url": "https://httpd.apache.org/docs/current/ssl/ssl_howto.html",
    },

    # 취약한 암호화
    {
        "vuln_type": "weak_cipher",
        "severity": "high",
        "cvss_score": 7.4,
        "server_type": "nginx",
        "title": "취약한 암호화 방식 비활성화 (Nginx)",
        "code": """# nginx.conf에 추가
server {
    listen 443 ssl;

    # 강력한 암호화만 허용 (RC4, DES, MD5 제외)
    ssl_ciphers ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384:!RC4:!DES:!3DES:!MD5:!aNULL;
    ssl_prefer_server_ciphers off;
}""",
        "description": "RC4, DES, MD5 등 취약한 암호화 방식은 데이터 복호화 공격에 취약합니다.",
        "reference_url": "https://nginx.org/en/docs/http/ngx_http_ssl_module.html#ssl_ciphers",
    },
    {
        "vuln_type": "weak_cipher",
        "severity": "high",
        "cvss_score": 7.4,
        "server_type": "apache",
        "title": "취약한 암호화 방식 비활성화 (Apache)",
        "code": """# httpd.conf 또는 ssl.conf에 추가
<VirtualHost *:443>
    # 강력한 암호화만 허용
    SSLCipherSuite ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:!RC4:!DES:!3DES:!MD5:!aNULL
    SSLHonorCipherOrder off
</VirtualHost>""",
        "description": "RC4, DES, MD5 등 취약한 암호화 방식은 데이터 복호화 공격에 취약합니다.",
        "reference_url": "https://httpd.apache.org/docs/current/ssl/ssl_howto.html",
    },

    # 자체 서명 인증서
    {
        "vuln_type": "self_signed_certificate",
        "severity": "high",
        "cvss_score": 6.8,
        "server_type": "nginx",
        "title": "공인 SSL 인증서 발급 (Let's Encrypt)",
        "code": """# Let's Encrypt 무료 인증서 발급
# Certbot 설치
apt-get install certbot python3-certbot-nginx

# 인증서 발급 (도메인 입력)
certbot --nginx -d yourdomain.com -d www.yourdomain.com

# 자동 갱신 설정
echo "0 0 * * * certbot renew --quiet" | crontab -""",
        "description": "자체 서명 인증서는 신뢰할 수 없어 브라우저에서 경고를 표시합니다. Let's Encrypt로 무료 공인 인증서를 발급받으세요.",
        "reference_url": "https://certbot.eff.org/",
    },
    {
        "vuln_type": "self_signed_certificate",
        "severity": "high",
        "cvss_score": 6.8,
        "server_type": "apache",
        "title": "공인 SSL 인증서 발급 (Let's Encrypt - Apache)",
        "code": """# Let's Encrypt 무료 인증서 발급
# Certbot 설치
apt-get install certbot python3-certbot-apache

# 인증서 발급
certbot --apache -d yourdomain.com -d www.yourdomain.com

# 자동 갱신 설정
echo "0 0 * * * certbot renew --quiet" | crontab -""",
        "description": "자체 서명 인증서는 신뢰할 수 없어 브라우저에서 경고를 표시합니다. Let's Encrypt로 무료 공인 인증서를 발급받으세요.",
        "reference_url": "https://certbot.eff.org/",
    },

    # SHA-1 서명
    {
        "vuln_type": "sha1_signature",
        "severity": "high",
        "cvss_score": 5.9,
        "server_type": "nginx",
        "title": "SHA-256 인증서로 재발급",
        "code": """# SHA-256으로 새 인증서 생성
openssl req -new -sha256 -key yourdomain.key -out yourdomain.csr

# Let's Encrypt 사용 시 자동으로 SHA-256 적용
certbot --nginx -d yourdomain.com

# 현재 인증서 서명 알고리즘 확인
openssl x509 -noout -text -in yourdomain.crt | grep "Signature Algorithm" """,
        "description": "SHA-1은 충돌 공격에 취약합니다. SHA-256 이상의 인증서로 재발급받으세요.",
        "reference_url": "https://letsencrypt.org/docs/glossary/",
    },
    {
        "vuln_type": "sha1_signature",
        "severity": "high",
        "cvss_score": 5.9,
        "server_type": "apache",
        "title": "SHA-256 인증서로 재발급 (Apache)",
        "code": """# SHA-256으로 새 인증서 생성
openssl req -new -sha256 -key yourdomain.key -out yourdomain.csr

# Let's Encrypt 사용 시 자동으로 SHA-256 적용
certbot --apache -d yourdomain.com

# 현재 인증서 서명 알고리즘 확인
openssl x509 -noout -text -in yourdomain.crt | grep "Signature Algorithm" """,
        "description": "SHA-1은 충돌 공격에 취약합니다. SHA-256 이상의 인증서로 재발급받으세요.",
        "reference_url": "https://letsencrypt.org/docs/glossary/",
    },

    # RSA 키 길이 부족
    {
        "vuln_type": "weak_key_size",
        "severity": "high",
        "cvss_score": 5.9,
        "server_type": "nginx",
        "title": "RSA 키 길이 2048bit 이상으로 재발급",
        "code": """# 2048bit RSA 키 생성
openssl genrsa -out yourdomain.key 2048

# 또는 더 강력한 4096bit
openssl genrsa -out yourdomain.key 4096

# CSR 생성
openssl req -new -sha256 -key yourdomain.key -out yourdomain.csr

# Let's Encrypt 사용 시 자동으로 2048bit 적용
certbot --nginx -d yourdomain.com""",
        "description": "RSA 키 길이가 2048bit 미만이면 브루트포스 공격에 취약합니다. 2048bit 이상으로 재발급받으세요.",
        "reference_url": "https://www.keylength.com/en/4/",
    },
    {
        "vuln_type": "weak_key_size",
        "severity": "high",
        "cvss_score": 5.9,
        "server_type": "apache",
        "title": "RSA 키 길이 2048bit 이상으로 재발급 (Apache)",
        "code": """# 2048bit RSA 키 생성
openssl genrsa -out yourdomain.key 2048

# CSR 생성
openssl req -new -sha256 -key yourdomain.key -out yourdomain.csr

# Let's Encrypt 사용 시 자동으로 2048bit 적용
certbot --apache -d yourdomain.com""",
        "description": "RSA 키 길이가 2048bit 미만이면 브루트포스 공격에 취약합니다. 2048bit 이상으로 재발급받으세요.",
        "reference_url": "https://www.keylength.com/en/4/",
    },
]
async def insert_snippets():
    async with AsyncSessionLocal() as db:
        for data in SNIPPETS:
            snippet = Snippet(
                vuln_type=data["vuln_type"],
                server_type=data["server_type"],
                title=data["title"],
                code=data["code"],
            )
            db.add(snippet)
        await db.commit()
        print(f"총 {len(SNIPPETS)}개 스니펫 삽입 완료!")


if __name__ == "__main__":
    asyncio.run(insert_snippets())
