# src/agents/faq_specialist.py
import os
from langchain_google_genai import ChatGoogleGenerativeAI
from src.state.state import AgentState
from src.schemas.models import FAQOutputSchema

def faq_specialist_node(state: AgentState):
    print("[FAQ Agent] Generating exactly 15 Q&A pairs...")
    
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash-lite",
        temperature=0.7,
        api_key=os.environ["GEMINI_API_KEY"],
        max_retries=2
    )
    
    structured_llm = llm.with_structured_output(FAQOutputSchema)
    
    product = state['product']
    
    base_prompt = f"""
    Context: {product.model_dump_json()}
    
    Task: Generate exactly 15 User Questions with concise Answers.
    
    Required Distribution (3 per category):
    1. Informational, 2. Safety, 3. Usage, 4. Purchase, 5. Comparison
    """
    
    max_retries = 3
    for i in range(max_retries):
        try:
            result = structured_llm.invoke(base_prompt)
            print(f"[FAQ Specialist] Generated {len(result.questions)} questions.")
            return {"questions": result.questions}
            
        except Exception as e:
            print(f"[FAQ Specialist] Attempt {i+1} Failed: {str(e)}")
            base_prompt += f"\n\n[ERROR]: Previous attempt failed validation. {str(e)}. Ensure exactly 15 items."
            
    raise ValueError("Failed to generate 15 valid questions.")