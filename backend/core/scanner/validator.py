import re
from urllib.parse import urlparse


DOMAIN_PATTERN = re.compile(r"^[a-zA-Z0-9.-]+$")


def validate_target(target: str) -> str:
    if not target or not target.strip():
        raise ValueError("타겟이 비어 있습니다.")

    value = target.strip()
    if "://" in value:
        parsed = urlparse(value)
        domain = parsed.netloc
    else:
        domain = value

    if "@" in domain:
        domain = domain.rsplit("@", 1)[1]

    domain = domain.split(":", 1)[0].strip().lower().rstrip(".")
    if domain.startswith("www."):
        domain = domain[4:]

    if not domain:
        raise ValueError(f"유효하지 않은 타겟: '{target}'")

    if not DOMAIN_PATTERN.fullmatch(domain):
        raise ValueError(
            f"허용되지 않은 문자가 포함되어 있습니다: '{domain}'. "
            "영문, 숫자, '.', '-'만 허용됩니다."
        )

    return domain
