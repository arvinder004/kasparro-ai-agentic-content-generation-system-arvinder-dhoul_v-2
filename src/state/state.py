import operator
from typing import TypedDict, List, Dict, Annotated
from src.schemas.models import ProductData, CompetitorProduct, UserQuestion

class AgentState(TypedDict, total=False):
    """
    The Single Source of Truth for the Graph.
    total=False allows fields to be None initially.
    """
    raw_input: Dict
    
    product: ProductData
    competitor: CompetitorProduct
    questions: List[UserQuestion]
    
    generated_pages: Annotated[List[Dict], operator.add]