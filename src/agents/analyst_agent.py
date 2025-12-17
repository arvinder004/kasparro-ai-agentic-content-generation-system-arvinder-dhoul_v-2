# src/agents/analyst.py
import os
from langchain_google_genai import ChatGoogleGenerativeAI
from src.state.state import AgentState
from src.schemas.models import ProductData, CompetitorOutputSchema
from src.tools.logic import clean_price_string, validate_competitor_logic

def analyst_node(state: AgentState):
    print("[Analyst] Ingesting & Cleaning Data...")
    raw = state['raw_input']
    
    price_val = clean_price_string.invoke(raw["Price"])
    
    product = ProductData(
        name=raw["Product Name"],
        concentration=raw.get("Concentration"),
        skin_type=[x.strip() for x in raw["Skin Type"].split(",")],
        key_ingredients=[x.strip() for x in raw["Key Ingredients"].split(",")],
        benefits=[x.strip() for x in raw["Benefits"].split(",")],
        how_to_use=raw["How to Use"],
        side_effects=raw["Side Effects"],
        price=price_val
    )

    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash-lite",
        temperature=0.5,
        api_key=os.environ["GEMINI_API_KEY"],
        max_retries=2,
    )
    
    print("[Analyst] Generating Competitor Profile...")
    structured_llm = llm.with_structured_output(CompetitorOutputSchema)
    
    ingredient_rule = ""
    if product.key_ingredients:
        ingredient_rule = "- Ingredients: Must share 1 key ingredient, add 1 unique active."
    else:
        ingredient_rule = "- Specs: Compare material quality or durability instead of ingredients."

    prompt = f"""
        TASK: Generate a DIRECT COMPETITOR profile for: '{product.name}'.
    
        INPUT DATA:
            - Type: {product.skin_types}
            - Price: {product.price_info.amount} {product.price_info.currency}
            {f"- Ingredients: {product.key_ingredients}" if product.key_ingredients else ""}
    
        CONSTRAINTS:
            1. Name: Realistic brand (e.g., 'DermaPure'). NO 'Product B'.
            2. Pricing: Target 15-20% difference (Higher or Lower).
            3. Differentiation:
                {ingredient_rule}
    
        OUTPUT: Valid JSON 'CompetitorProduct'.
    """
    
    max_retries = 3
    current_prompt = prompt
    
    for i in range(max_retries):
        try:
            result = structured_llm.invoke(current_prompt)
            
            # --- USE IMPORTED VALIDATION LOGIC ---
            val_msg = validate_competitor_logic(product, result.competitor)
            
            if val_msg == "VALID":
                print("✅ [Analyst] Competitor Generated & Validated.")
                return {
                    "product": product,
                    "competitor": result.competitor
                }
            else:
                print(f"⚠️ [Analyst] Competitor Validation Failed: {val_msg}")
                current_prompt = prompt + f"\n\n[SYSTEM ERROR]: {val_msg}. Regenerate."
                
        except Exception as e:
            print(f"⚠️ [Analyst] Error: {e}")
            current_prompt += f"\n[ERROR]: {e}"

    raise ValueError("Failed to generate valid competitor.")