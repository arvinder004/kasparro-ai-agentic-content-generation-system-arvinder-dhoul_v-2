import os
from langchain_google_genai import ChatGoogleGenerativeAI
from src.state.state import AgentState
from src.schemas.models import PageOutput
from src.tools.logic import PAGE_TEMPLATES, compare_prices_logic, format_benefits_html

def writer_node_factory(page_key: str):
    
    def write_page(state: AgentState):
        template = PAGE_TEMPLATES[page_key]
        print(f"[Writer] Building {template['page_type']}...")
        
        llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash-lite",
            temperature=0.5,
            api_key=os.environ["GEMINI_API_KEY"],
            max_retries=2,
        )
    
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
        Required Sections: {template['sections']}
        
        Data Context: {context}
        
        Rules:
        1. Use 'compare_prices_logic' for price comparisons.
        2. Use 'format_benefits_html' for lists.
        3. IF this is the FAQ Page, you MUST include ALL 15 questions from the context.
        """
        
        result = structured_llm.invoke(prompt)
        print(f"✅ [Writer] Finished {page_key}.")
        
        return {"generated_pages": [{page_key: result.model_dump()}]}
        
    return write_page