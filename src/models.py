from pydantic import BaseModel, Field
from typing import List, Optional, Union, Dict, Literal

class ProductData(BaseModel):
    name: str = Field(description="Name of the product")
    concentration: Optional[str] = None
    skin_type: List[str]
    key_ingredients: List[str]
    benefits: List[str]
    how_to_use: str
    side_effects: Optional[str] = None
    price: float = Field(description="Price as a float number")


class CompetitorProduct(BaseModel):
    name: str
    key_ingredients: List[str]
    benefits: List[str]
    price: float


class UserQuestion(BaseModel):
    category: Literal["Informational", "Safety", "Usage", "Purchase", "Comparison"]
    question_text: str
    answer_text: Optional[str] = None


class PageSection(BaseModel):
    heading: str
    content: Union[str, List[UserQuestion]] 


class PageOutput(BaseModel):
    page_type: str
    meta_title: str
    meta_description: str
    sections: List[PageSection]


class AnalystOutput(BaseModel):
    questions: List[UserQuestion]
    competitor: CompetitorProduct