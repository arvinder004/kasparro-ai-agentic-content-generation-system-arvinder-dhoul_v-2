from langchain_core.tools import tool
from src.models import ProductData, CompetitorProduct

PAGE_TEMPLATES = {
    "faq": {
        "page_type": "FAQ Page",
        "instructions": "Focus on answering user doubts. Use the provided Questions list. Filter for Safety and Usage.",
        "sections": ["Header", "Safety Q&A", "Usage Q&A"]
    },
    "product": {
        "page_type": "Product Description Page",
        "instructions": "Write persuasive marketing copy. Use HTML formatting for lists.",
        "sections": ["Hero Section", "Key Benefits", "How to Use"]
    },
    "comparison": {
        "page_type": "Comparison Page",
        "instructions": "Compare the primary product vs the competitor strictly. Be objective but highlight our advantages.",
        "sections": ["Head-to-Head", "Price Analysis", "Verdict"]
    }
}

@tool
def format_benefits_html(benefits: list[str]) -> str:
    items = "".join([f"<li>{b}</li>" for b in benefits])
    return f"<ul>{items}</ul>"


@tool
def compare_prices_logic(price_a: float, price_b: float, name_a: str, name_b: str) -> str:
    diff = price_a - price_b
    if diff < 0:
        return f"{name_a} is cheaper by ₹{abs(diff):.2f}"
    elif diff > 0:
        return f"{name_b} is cheaper by ₹{abs(diff):.2f}"
    return "Both products are of same price"


@tool
def clean_price_string(price_str: str) -> float:
    import re
    clean = re.sub(r'[^\d.]', '', str(price_str))
    return float(clean) if clean else 0.0
