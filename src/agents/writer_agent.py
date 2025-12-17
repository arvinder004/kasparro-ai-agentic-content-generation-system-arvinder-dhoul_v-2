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

        block_interface = """
            VALID BLOCK TYPES (JSON Snippets):
                - Paragraph: {"type": "text", "html_content": "<p>...</p>"}
                - List:      {"type": "list", "items": ["..."], "ordered": true/false}
                - FAQ:       {"type": "faq", "qa_pairs": [{"question_text": "...", "answer_text": "..."}]}
                - Table:     {"type": "table", "headers": ["..."], "rows": [["..."]]}
        """

        prompt = f"""
            ROLE: CMS Content Architect.
            TARGET: {template['page_type']}
            SECTIONS: {template['sections']}
    
            DATA CONTEXT:
                {context}
    
            {block_interface}
    
            INSTRUCTIONS:
                Map the Data Context to the Required Sections using ONLY the Valid Block Types above.
                - FAQ Page? -> Must use 'FAQ' block with all 15 questions.
                - Comparison? -> Must use 'Table' block.
                - Intro? -> Use 'Paragraph'.
    
            SEO:
                - Generate optimized Title & Slug.
        """
        
        result = structured_llm.invoke(prompt)
        print(f"✅ [Writer] Finished {page_key}.")
        
        return {"generated_pages": [{page_key: result.model_dump()}]}
        
    return write_page