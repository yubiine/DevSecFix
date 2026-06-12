def calculate_security_grade(vulnerabilities: list[dict]) -> tuple[str, float]:
    if not vulnerabilities:
        return "A", 0.0

    total_score = round(
        sum(float(vulnerability["cvss_score"]) for vulnerability in vulnerabilities),
        1,
    )
    max_score = max(float(vulnerability["cvss_score"]) for vulnerability in vulnerabilities)

    if max_score >= 9.0:
        grade = "F"
    elif max_score >= 7.0:
        grade = "D"
    elif max_score >= 4.0:
        grade = "C"
    elif max_score > 0:
        grade = "B"
    else:
        grade = "A"

    return grade, total_score
