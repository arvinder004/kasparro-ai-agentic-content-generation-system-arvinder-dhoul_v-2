import os
import asyncio
import random
from typing import List
from langchain_google_genai import ChatGoogleGenerativeAI
from pydantic import BaseModel, Field
from src.state.state import AgentState
from src.schemas.models import UserQuestion
from src.logger.logger import setup_logger

logger = setup_logger(__name__)

CATEGORIES = ["Informational", "Safety", "Usage", "Purchase", "Comparison"]
TARGET_PER_CATEGORY = 3

CONCURRENCY_LIMIT = 3 

class BatchQuestionOutput(BaseModel):
    questions: List[UserQuestion] = Field(
        description=f"List of exactly {TARGET_PER_CATEGORY} questions for the specific category."
    )

async def generate_category_batch(
    semaphore: asyncio.Semaphore,
    llm: ChatGoogleGenerativeAI, 
    category: str, 
    context_str: str, 
    run_id: str
) -> List[UserQuestion]:
    """
    Generates questions for a single category. 
    Uses a Semaphore to prevent hitting API Rate Limits.
    """
    async with semaphore:

        await asyncio.sleep(random.uniform(0.1, 1.0))
        
        logger.info(f"Triggering Batch: {category}", extra={"run_id": run_id})
        
        structured_llm = llm.with_structured_output(BatchQuestionOutput)
        
        prompt = f"""
        CONTEXT: {context_str}
        
        TASK: Generate exactly {TARGET_PER_CATEGORY} User Questions + Answers for the category: '{category}'.
        
        RULES:
        1. Category field in JSON must be '{category}'.
        2. Answers must be concise and helpful.
        3. Questions should be distinct and specific to the product ingredients/usage.
        
        OUTPUT: JSON Object with a list of questions.
        """
        
        for attempt in range(3):
            try:
                result = await structured_llm.ainvoke(prompt)
                
                if len(result.questions) >= TARGET_PER_CATEGORY:
                    valid_qs = result.questions[:TARGET_PER_CATEGORY]
                    for q in valid_qs:
                        q.category = category
                    return valid_qs
                
            except Exception as e:
                logger.warning(
                    f"Batch {category} Attempt {attempt+1} failed: {e}", 
                    extra={"run_id": run_id}
                )
                await asyncio.sleep(1)
        
        logger.error(f"Batch {category} Failed completely.", extra={"run_id": run_id})
        return []

async def faq_specialist_node(state: AgentState):
    run_id = state.get("run_id", "unknown")
    logger.info("Starting Parallel FAQ Generation...", extra={"run_id": run_id})
    
    product = state['product']
    slim_context = f"Product: {product.name}, Ingredients: {product.key_ingredients}, Benefits: {product.benefits}"
    
    # Initialize LLM
    llm = ChatGoogleGenerativeAI(
        model="gemini-1.5-flash",
        temperature=0.7,
        api_key=os.environ["GEMINI_API_KEY"],
        max_retries=1
    )
    
    sem = asyncio.Semaphore(CONCURRENCY_LIMIT)
    
    tasks = [
        generate_category_batch(sem, llm, cat, slim_context, run_id) 
        for cat in CATEGORIES
    ]
    
    results = await asyncio.gather(*tasks)
    
    all_questions = [q for batch in results for q in batch]
    
    unique_questions = []
    seen_texts = set()
    
    for q in all_questions:
        clean_text = q.question_text.lower().strip().replace("?", "")
        if clean_text not in seen_texts:
            unique_questions.append(q)
            seen_texts.add(clean_text)
    
    final_count = len(unique_questions)
    logger.info(f"Generated {final_count}/15 unique questions.", extra={"run_id": run_id})
    
    if final_count < 15:
        missing = 15 - final_count
        logger.warning(f"Missing {missing} questions. Filling with generic safety net.", extra={"run_id": run_id})
        
        generic_fillers = [
            UserQuestion(category="Purchase", question_text="What is the return policy?", answer_text="Please check our website for the 30-day return policy."),
            UserQuestion(category="Safety", question_text="Is this safe for sensitive skin?", answer_text="Yes, but patch testing is always recommended."),
            UserQuestion(category="Usage", question_text="Can I use this daily?", answer_text="Yes, it is formulated for daily use."),
            UserQuestion(category="Informational", question_text="Is the packaging recyclable?", answer_text="Yes, we use eco-friendly materials."),
            UserQuestion(category="Comparison", question_text="How does this compare to basic serums?", answer_text="It contains higher quality actives.")
        ]
        
        for filler in generic_fillers:
            if len(unique_questions) >= 15:
                break

            clean_filler = filler.question_text.lower().strip().replace("?", "")
            if clean_filler not in seen_texts:
                unique_questions.append(filler)
                seen_texts.add(clean_filler)

    final_output = unique_questions[:15]
    
    return {"questions": final_output}