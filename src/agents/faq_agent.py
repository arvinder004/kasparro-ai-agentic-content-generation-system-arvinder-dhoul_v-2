# src/agents/faq_specialist.py
import os
from langchain_google_genai import ChatGoogleGenerativeAI
from src.state.state import AgentState
from src.schemas.models import FAQOutputSchema
from src.tools.logic import validate_faq_logic
from src.logger.logger import setup_logger, monitor_node

logger = setup_logger(__name__)

@monitor_node
def faq_specialist_node(state: AgentState):
    run_id = state.get("run_id")

    print("[FAQ Agent] Generating exactly 15 Q&A pairs...")
    
    product = state['product']

    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash-lite",
        temperature=0.7,
        api_key=os.environ["GEMINI_API_KEY"],
        max_retries=2
    )
    
    structured_llm = llm.with_structured_output(FAQOutputSchema)
    
    base_prompt = f"""
    CONTEXT: {product.model_dump_json()}
    
    GOAL: Generate exactly 15 Q&A pairs.
    
    STRATEGY (Think before generating):
    1. PLAN: Identify 3 distinct topics for EACH category below.
    2. DRAFT: Write the questions based on the plan.
    3. REVIEW: Ensure total count is 15.
    
    CATEGORIES:
    [Informational, Safety, Usage, Purchase, Comparison]
    
    RESPONSE FORMAT:
    Return ONLY the list of 15 objects.
    """
    
    max_retries = 3
    current_prompt = base_prompt
    
    for i in range(max_retries):
        try:
            result = structured_llm.invoke(current_prompt)
            validation_msg = validate_faq_logic(result.questions)
            
            if validation_msg == "VALID":
                logger.info(
                    "FAQ Generation Successful", 
                    extra={"run_id": run_id, "question_count": len(result.questions)}
                )
                print(f"[FAQ Specialist] Validation Passed: 15 Unique Questions (3/category).")
                return {"questions": result.questions}
            else:
                logger.warning(
                    f"Attempt {i+1} Failed Validation",
                    extra={"run_id": run_id, "error": validation_msg}
                )
                print(f"[FAQ Specialist] Attempt {i+1} Failed Validation:\n{validation_msg}")
                current_prompt = base_prompt + f"\n\n[SYSTEM ERROR - FIX REQUIRED]:\n{validation_msg}\n\nPlease regenerate the ENTIRE list to fix these specific errors."
                
        except Exception as e:
            print(f"[FAQ Specialist] Attempt {i+1} Exception: {str(e)}")
            current_prompt += f"\n\n[ERROR]: {str(e)}"
            
    raise ValueError("Failed to generate 15 valid questions after 3 attempts.")