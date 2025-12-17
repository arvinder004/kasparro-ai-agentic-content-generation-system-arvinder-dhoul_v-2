import os
from langchain_google_genai import ChatGoogleGenerativeAI
from src.state.state import AgentState
from src.schemas.models import PageOutput
from src.templates.registry import TEMPLATE_REGISTRY, PageLayout
from src.logger.logger import setup_logger, monitor_node

logger = setup_logger(__name__)

def render_layout_instructions(layout: PageLayout) -> str:
    """
    Dynamic Prompt Construction (The Composition Engine).
    Converts the Python Object Blueprint into strict LLM instructions.
    """
    instructions = [f"PAGE GOAL: {layout.page_type_name} - {layout.description}\n"]
    
    instructions.append("SECTION BLUEPRINT (You must adhere to this structure):")
    for idx, section in enumerate(layout.structure, 1):
        allowed = ", ".join([f"'{b}'" for b in section.allowed_blocks])
        
        block_instr = f"""
        {idx}. SECTION ID: {section.section_id}
           - Heading: "{section.heading_default}"
           - Data Sources: {section.data_sources}
           - Instructions: {section.instructions}
           - CONSTRAINT: You MUST use one of these Block Types: [{allowed}]
        """
        instructions.append(block_instr)
        
    return "\n".join(instructions)

def writer_node_factory(page_key: str):

    @monitor_node
    def write_page(state: AgentState):
        run_id = state.get("run_id")

        layout_obj = TEMPLATE_REGISTRY.get(page_key)
        if not layout_obj:
            raise ValueError(f"No layout found for {page_key}")

        logger.info(f"Rendering {page_key}...", extra={"run_id": run_id})   
        print(f"[Writer] Rendering Layout: {layout_obj.page_type_name}...")
        
        llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash-lite",
            temperature=0.5,
            api_key=os.environ["GEMINI_API_KEY"]
        )
        
        structured_llm = llm.with_structured_output(PageOutput)
        
        context = {
            "primary": state['product'].model_dump(),
            "competitor": state['competitor'].model_dump(),
            "questions": [q.model_dump() for q in state['questions']]
        }
        
        layout_instructions = render_layout_instructions(layout_obj)
        
        prompt = f"""
        ROLE: Headless CMS Renderer.
        
        {layout_instructions}
        
        DATA CONTEXT:
        {context}
        
        BLOCK DEFINITIONS:
        - 'text': HTML Paragraphs.
        - 'list': Bullet points (ordered/unordered).
        - 'faq': List of Question/Answer objects.
        - 'table': Headers and Rows.
        
        GLOBAL RULES:
        1. Follow the SECTION BLUEPRINT exactly. Do not add sections not listed.
        2. Adhere to the 'CONSTRAINT' for block types in each section.
        3. For SEO, generate a slug based on the primary product name.
        """
        
        result = structured_llm.invoke(prompt)
        print(f"[Writer] Rendered {page_key}.")
        
        return {"generated_pages": [{page_key: result.model_dump(mode='json')}]}
        
    return write_page