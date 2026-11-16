"""Transparent deterministic classifier; an AI agent will replace/augment this later."""

CATEGORY_KEYWORDS = {
    "policy_question": ("policy", "leave", "vacation", "benefits", "handbook"),
    "finance_request": ("invoice", "payment", "expense", "reimbursement", "budget"),
    "it_support": ("password", "laptop", "access", "login", "software", "network"),
}
HIGH_PRIORITY_TERMS = ("urgent", "outage", "security", "breach", "critical")


def classify_request(department: str, description: str) -> dict[str, str]:
    text = f"{department} {description}".lower()
    category = "general_request"
    for candidate, keywords in CATEGORY_KEYWORDS.items():
        if any(keyword in text for keyword in keywords):
            category = candidate
            break
    priority = "high" if any(term in text for term in HIGH_PRIORITY_TERMS) else "normal"
    return {"category": category, "priority": priority}
