from dotenv import load_dotenv
from langgraph.graph import StateGraph, END

from src.state.state import AgentState
from src.agents.analyst_agent import analyst_node
from src.agents.faq_agent import faq_specialist_node
from src.agents.writer_agent import writer_node_factory

load_dotenv()

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
    workflow.add_edge("write_faq", "write_product")
    workflow.add_edge("write_product", "write_comparison")
    workflow.add_edge("write_comparison", END)

    return workflow.compile()

app = build_graph()