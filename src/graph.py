import os
import operator
from typing import Annotated, TypedDict, List, Dict
from dotenv import load_dotenv

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import SystemMessage, HumanMessage
from langgraph.graph import StateGraph, END

from src.models import ProductData, CompetitorProduct, UserQuestion, PageOutput, AnalystOutput
from src.tools import PAGE_TEMPLATES, compare_prices_logic, format_benefits_html, clean_price_string

load_dotenv()


class AgentState(TypedDict):
    raw_input: Dict
    product: ProductData
    competitor: CompetitorProduct
    questions: List[UserQuestion]
    generated_pages: Annotated[List[Dict], operator.add] 


llm = ChatGoogleGenerativeAI(
    model="gemini-1.5-flash",
    temperature=0.5,
    api_key=os.environ["GEMINI_API_KEY"]
)


def ingest_node(state: AgentState):
    print("[Analyst Agent] Processing Data...")
    raw = state['raw_input']
    
    price_float = clean_price_string.invoke(raw["Price"])
    
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

    analyst_llm = llm.with_structured_output(AnalystOutput)
    
    prompt = f"""
    Analyze this product: {product.model_dump_json()}
    
    Tasks:
    1. Generate a fictional Competitor Product (Product B) with realistic specs.
       IMPORTANT: The competitor price must be a float number.
    2. Generate 15 User Questions categorized into: Informational, Safety, Usage, Purchase, Comparison.
    """
    
    result = analyst_llm.invoke(prompt)
    
    return {
        "product": product,
        "competitor": result.competitor,
        "questions": result.questions
    }

def writer_node_factory(page_key: str):

    def write_page(state: AgentState):
        template = PAGE_TEMPLATES[page_key]
        print(f"[Writer Agent] Building {template['page_type']}...")
        
        writer_llm = llm.bind_tools([compare_prices_logic, format_benefits_html])
        structured_llm = writer_llm.with_structured_output(PageOutput)
        
        context = {
            "primary": state['product'].model_dump(),
            "competitor": state['competitor'].model_dump(),
            "questions": [q.model_dump() for q in state['questions']]
        }
        
        prompt = f"""
        You are an expert Content Architect.
        
        Goal: Create a {template['page_type']}.
        Instructions: {template['instructions']}
        Required Sections: {template['sections']}
        
        Data Context: {context}
        
        Rules:
        1. Use 'compare_prices_logic' tool for price sections.
        2. Use 'format_benefits_html' tool for benefit lists.
        3. For Q&A sections, select relevant questions from the provided list and answer them.
        """
        
        page_obj = structured_llm.invoke(prompt)
        
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