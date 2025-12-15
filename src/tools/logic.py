import re
from typing import List
from langchain_core.tools import tool


PAGE_TEMPLATES = {
    "faq": {
        "page_type": "FAQ Page",
        "instructions": "Format the provided questions into the correct sections. Do not generate new questions.",
        "sections": ["Informational", "Safety", "Usage", "Purchase", "Comparison"]
    },
    "product": {
        "page_type": "Product Description Page",
        "instructions": "Write persuasive marketing copy. Use HTML formatting for lists.",
        "sections": ["Hero Section", "Key Benefits", "How to Use"]
    },
    "comparison": {
        "page_type": "Comparison Page",
        "instructions": "Compare primary vs competitor. Be objective.",
        "sections": ["Head-to-Head", "Price Analysis", "Verdict"]
    }
}


@tool
def format_benefits_html(benefits: List[str]) -> str:
    """Converts a list of benefits strings into an HTML unordered list (<ul>)."""
    items = "".join([f"<li>{b}</li>" for b in benefits])
    return f"<ul>{items}</ul>"

@tool
def compare_prices_logic(price_a: float, price_b: float, name_a: str, name_b: str) -> str:
    """Calculates price difference between two products (a and b)."""
    try:
        pa, pb = float(price_a), float(price_b)
        diff = pa - pb
        if diff < 0: return f"{name_a} is cheaper by ₹{abs(diff):.2f}."
        if diff > 0: return f"{name_b} is cheaper by ₹{abs(diff):.2f}."
        return "Same price."
    except:
        return "Price comparison error."

@tool
def clean_price_string(price_str: str) -> float:
    """Extracts numeric float from string (e.g., '₹699' -> 699.0)."""
    try:
        clean = re.sub(r'[^\d.]', '', str(price_str))
        return float(clean) if clean else 0.0
    except:
        return 0.0