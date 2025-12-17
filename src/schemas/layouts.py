from typing import List, Optional, Literal
from pydantic import BaseModel, Field

BlockTypeLiteral = Literal["text", "list", "faq", "table"]

class SectionBlueprint(BaseModel):
    """
    Defines the structural requirements for a single section of a page.
    """
    section_id: str = Field(..., description="Unique internal ID (e.g., 'hero_section')")
    heading_default: str = Field(..., description="Default H2 heading")
    
    allowed_blocks: List[BlockTypeLiteral] 
    
    instructions: str = Field(..., description="Specific goal for this section")
    data_sources: List[str] = Field(..., description="Hints on which data fields to use (e.g. 'product.benefits')")

class PageLayout(BaseModel):
    """
    Defines the composition of a full page.
    """
    layout_id: str
    page_type_name: str
    description: str
    structure: List[SectionBlueprint]