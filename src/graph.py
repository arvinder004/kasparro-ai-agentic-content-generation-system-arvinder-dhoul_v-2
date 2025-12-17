from dotenv import load_dotenv
from langgraph.graph import StateGraph, END
from typing import Literal, List    

from src.state.state import AgentState
from src.agents.analyst_agent import analyst_node
from src.agents.faq_agent import faq_specialist_node
from src.agents.writer_agent import writer_node_factory

load_dotenv()

def decide_comparison_feasibility(state: AgentState) -> Literal["write_comparison", "skip_comparison"]:
    """
    Conditional Logic:
    Only generate a comparison page if we have valid prices for BOTH
    the primary product and the competitor.
    """
    product_price = state.get("product").price
    competitor_price = state.get("competitor").price
    
    if product_price > 0 and competitor_price > 0:
        print("[Router] Prices valid. Proceeding to Comparison Page.")
        return "write_comparison"
    else:
        print("[Router] Missing prices. SKIPPING Comparison Page.")
        return "skip_comparison"


def build_graph():
    workflow = StateGraph(AgentState)

    workflow.add_node("analyst", analyst_node)
    workflow.add_node("faq_specialist", faq_specialist_node)

    workflow.add_node("write_faq", writer_node_factory("faq"))
    workflow.add_node("write_product", writer_node_factory("product"))
    workflow.add_node("write_comparison", writer_node_factory("comparison"))

    workflow.set_entry_point("analyst")
    
    workflow.add_edge("analyst", "faq_specialist")
    
    workflow.add_edge("faq_specialist", "write_faq")
    workflow.add_edge("faq_specialist", "write_product")

    workflow.add_conditional_edges(
        "faq_specialist",
        decide_comparison_feasibility,
        {
            "write_comparison": "write_comparison",
            "skip_comparison": END
        }
    )

    workflow.add_edge("write_faq", END)
    workflow.add_edge("write_product", END)
    workflow.add_edge("write_comparison", END)

    return workflow.compile()

app = build_graph()