# src/graph.py
import os
import operator
from typing import Annotated, TypedDict, List, Dict
from dotenv import load_dotenv

from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph import StateGraph, END

from src.models import ProductData, CompetitorProduct, UserQuestion, PageOutput, AnalystOutput
from src.tools import PAGE_TEMPLATES, compare_prices_logic, format_benefits_html, clean_price_string

load_dotenv()


class AgentState(TypedDict, total=False):
    raw_input: Dict
    product: ProductData
    competitor: CompetitorProduct
    questions: List[UserQuestion]
    generated_pages: Annotated[List[Dict], operator.add] 


if not os.environ.get("GEMINI_API_KEY"):
    raise ValueError("GEMINI_API_KEY is missing from .env file!")

llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash-lite",
    temperature=0.5,
    api_key=os.environ["GEMINI_API_KEY"],
    max_retries=2,
)



def ingest_node(state: AgentState):
    print("[Analyst] Starting Ingestion...")
    raw = state['raw_input']
    
    try:
        price_float = clean_price_string.invoke(raw["Price"])
    except Exception as e:
        print(f"Price cleaning failed: {e}")
        price_float = 0.0
    
    product = ProductData(
        name=raw["Product Name"],
        concentration=raw.get("Concentration"),
        skin_type=[x.strip() for x in raw["Skin Type"].split(",")],
        key_ingredients=[x.strip() for x in raw["Key Ingredients"].split(",")],
        benefits=[x.strip() for x in raw["Benefits"].split(",")],
        how_to_use=raw["How to Use"],
        side_effects=raw["Side Effects"],
        price=price_float
    )

    print("[Analyst] Generating Strategy...")
    analyst_llm = llm.with_structured_output(AnalystOutput)
    
    prompt = f"""
    Analyze this product: {product.model_dump_json()}
    
    Tasks:
    1. Generate a fictional Competitor Product (Product B). Price must be a float.
    2. Generate 15 User Questions (Informational, Safety, Usage, Purchase, Comparison).
    """
    
    try:
        result = analyst_llm.invoke(prompt)
        print("[Analyst] Strategy Generated.")
    except Exception as e:
        print(f"[Analyst] LLM Failed: {e}")
        raise e
    
    return {
        "product": product,
        "competitor": result.competitor,
        "questions": result.questions
    }

def writer_node_factory(page_key: str):
    def write_page(state: AgentState):
        template = PAGE_TEMPLATES[page_key]
        print(f"[Writer] Writing {template['page_type']}...")
        
        writer_llm = llm.bind_tools([compare_prices_logic, format_benefits_html])
        structured_llm = writer_llm.with_structured_output(PageOutput)
        
        context = {
            "primary": state['product'].model_dump(),
            "competitor": state['competitor'].model_dump(),
            "questions": [q.model_dump() for q in state['questions']]
        }
        
        prompt = f"""
        Act as a Content Architect.
        Target: {template['page_type']}
        Instructions: {template['instructions']}
        Sections: {template['sections']}
        
        Context: {context}
        """
        
        try:
            page_obj = structured_llm.invoke(prompt)
            print(f"[Writer] Finished {template['page_type']}.")
        except Exception as e:
            print(f"[Writer] Failed on {page_key}: {e}")
            raise e
        
        return {"generated_pages": [{page_key: page_obj.model_dump()}]}

    return write_page


# build the graph
workflow = StateGraph(AgentState)

workflow.add_node("analyst", ingest_node)
workflow.add_node("write_faq", writer_node_factory("faq"))
workflow.add_node("write_product", writer_node_factory("product"))
workflow.add_node("write_comparison", writer_node_factory("comparison"))

workflow.set_entry_point("analyst")
workflow.add_edge("analyst", "write_faq")
workflow.add_edge("write_faq", "write_product")
workflow.add_edge("write_product", "write_comparison")
workflow.add_edge("write_comparison", END)

app = workflow.compile()