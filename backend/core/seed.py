from core.database_sync import SessionLocal
from models.snippet import Snippet


SEED_SNIPPETS = [
    {
        "vuln_type": "missing_hsts",
        "server_type": "nginx",
        "title": "HSTS 헤더 추가 (Nginx)",
        "code": 'add_header Strict-Transport-Security "max-age=31536000; includeSubDomains; preload" always;',
    },
    {
        "vuln_type": "missing_hsts",
        "server_type": "apache",
        "title": "HSTS 헤더 추가 (Apache)",
        "code": 'Header always set Strict-Transport-Security "max-age=31536000; includeSubDomains; preload"',
    },
    {
        "vuln_type": "missing_csp",
        "server_type": "nginx",
        "title": "CSP 헤더 추가 (Nginx)",
        "code": 'add_header Content-Security-Policy "default-src \'self\'" always;',
    },
    {
        "vuln_type": "missing_csp",
        "server_type": "apache",
        "title": "CSP 헤더 추가 (Apache)",
        "code": 'Header always set Content-Security-Policy "default-src \'self\'"',
    },
    {
        "vuln_type": "missing_x_frame_options",
        "server_type": "nginx",
        "title": "X-Frame-Options 헤더 추가 (Nginx)",
        "code": 'add_header X-Frame-Options "SAMEORIGIN" always;',
    },
    {
        "vuln_type": "missing_x_frame_options",
        "server_type": "apache",
        "title": "X-Frame-Options 헤더 추가 (Apache)",
        "code": 'Header always set X-Frame-Options "SAMEORIGIN"',
    },
    {
        "vuln_type": "missing_x_content_type",
        "server_type": "nginx",
        "title": "X-Content-Type-Options 헤더 추가 (Nginx)",
        "code": 'add_header X-Content-Type-Options "nosniff" always;',
    },
    {
        "vuln_type": "missing_x_content_type",
        "server_type": "apache",
        "title": "X-Content-Type-Options 헤더 추가 (Apache)",
        "code": 'Header always set X-Content-Type-Options "nosniff"',
    },
    {
        "vuln_type": "weak_tls_protocol",
        "server_type": "nginx",
        "title": "TLS 1.0/1.1 비활성화 (Nginx)",
        "code": "ssl_protocols TLSv1.2 TLSv1.3;",
    },
    {
        "vuln_type": "weak_tls_protocol",
        "server_type": "apache",
        "title": "TLS 1.0/1.1 비활성화 (Apache)",
        "code": "SSLProtocol all -SSLv3 -TLSv1 -TLSv1.1",
    },
    {
        "vuln_type": "server_info_leaked",
        "server_type": "nginx",
        "title": "서버 버전 정보 숨기기 (Nginx)",
        "code": "server_tokens off;",
    },
    {
        "vuln_type": "server_info_leaked",
        "server_type": "apache",
        "title": "서버 버전 정보 숨기기 (Apache)",
        "code": "ServerTokens Prod\nServerSignature Off",
    },
]


def run_seed() -> None:
    db = SessionLocal()
    try:
        inserted = 0
        updated = 0
        for data in SEED_SNIPPETS:
            snippet = (
                db.query(Snippet)
                .filter(
                    Snippet.vuln_type == data["vuln_type"],
                    Snippet.server_type == data["server_type"],
                )
                .first()
            )
            if snippet is None:
                db.add(Snippet(**data))
                inserted += 1
            else:
                snippet.title = data["title"]
                snippet.code = data["code"]
                updated += 1

        db.commit()
        print(f"seed complete: inserted={inserted}, updated={updated}")
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    run_seed()
