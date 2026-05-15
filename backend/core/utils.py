from urllib.parse import urlparse


def extract_domain(url: str) -> str:
    if not url.startswith(("http://", "https://")):
        url = "https://" + url

    parsed = urlparse(url)
    domain = parsed.netloc.lower()

    if "@" in domain:
        domain = domain.rsplit("@", 1)[1]

    if ":" in domain:
        domain = domain.split(":", 1)[0]

    if domain.startswith("www."):
        domain = domain[4:]

    return domain.rstrip(".")
