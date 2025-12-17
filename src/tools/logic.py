import re
from typing import List
from langchain_core.tools import tool
from collections import Counter
from src.schemas.models import ProductData, CompetitorProduct, UserQuestion


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


def validate_faq_logic(questions: List[UserQuestion]) -> str:
    """
    Validates FAQ list for Count (15), Uniqueness, and Category Distribution (3 each).
    Returns 'VALID' or a specific error message.
    """
    errors = []
    
    # 1. Count Constraint
    if len(questions) != 15:
        errors.append(f"COUNT ERROR: Expected 15 questions, got {len(questions)}.")
        
    # 2. Uniqueness Constraint
    seen_texts = set()
    duplicates = []
    for q in questions:
        clean_text = q.question_text.strip().lower()
        if clean_text in seen_texts:
            duplicates.append(q.question_text)
        seen_texts.add(clean_text)
    
    if duplicates:
        errors.append(f"UNIQUENESS ERROR: Found duplicate questions: {duplicates[:3]}...")

    # 3. Category Coverage Constraint
    required_cats = ["Informational", "Safety", "Usage", "Purchase", "Comparison"]
    counts = Counter(q.category for q in questions)
    
    for cat in required_cats:
        if counts[cat] != 3:
            errors.append(f"DISTRIBUTION ERROR: Category '{cat}' has {counts[cat]} items. Expected exactly 3.")
    
    if not errors:
        return "VALID"
    
    return "\n".join(errors)

def validate_competitor_logic(primary: ProductData, competitor: CompetitorProduct) -> str:
    """
    Enforces that the competitor is distinct from the primary product.
    """
    if competitor.name.lower() == primary.name.lower():
        return "Competitor name cannot be the same as Primary Product name."
    
    # Check for identical price
    if competitor.price_info.amount == primary.price_info.amount:
        return "Competitor price cannot be identical. Make it higher or lower."
        
    return "VALID"


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