from typing import List, Optional, Union, Literal, Dict
from pydantic import BaseModel, Field, conlist


class ProductData(BaseModel):
    name: str
    concentration: Optional[str] = None
    skin_type: List[str]
    key_ingredients: List[str]
    benefits: List[str]
    how_to_use: str
    side_effects: Optional[str] = None
    price: float

class CompetitorProduct(BaseModel):
    name: str
    key_ingredients: List[str]
    benefits: List[str]
    price: float

class UserQuestion(BaseModel):
    category: Literal["Informational", "Safety", "Usage", "Purchase", "Comparison"]
    question_text: str
    answer_text: str


class FAQOutputSchema(BaseModel):
    questions: List[UserQuestion] = Field(min_length=15)

class CompetitorOutputSchema(BaseModel):
    competitor: CompetitorProduct


class PageSection(BaseModel):
    heading: str
    content: Union[str, List[UserQuestion], List[Dict]]

class PageOutput(BaseModel):
    page_type: str
    meta_title: str
    meta_description: str
    sections: List[PageSection]