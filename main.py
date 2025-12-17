import os
import json
import uuid        
import traceback
from src.graph import app
from src.logger.logger import setup_logger

logger = setup_logger("main")

RAW_DATA = {
    "Product Name": "GlowBoost Vitamin C Serum",
    "Concentration": "10% Vitamin C",
    "Skin Type": "Oily, Combination",
    "Key Ingredients": "Vitamin C, Hyaluronic Acid",
    "Benefits": "Brightening, Fades dark spots",
    "How to Use": "Apply 2–3 drops in the morning before sunscreen",
    "Side Effects": "Mild tingling for sensitive skin",
    "Price": "₹699"
}

def main():
    run_id = str(uuid.uuid4())
    
    logger.info("Starting System Execution", extra={"run_id": run_id})

    print("Starting Multi-Agent System...")
    os.makedirs("output", exist_ok=True)

    try:
        initial_state = {
            "run_id": run_id, 
            "raw_input": RAW_DATA, 
            "generated_pages": []
        }

        final_state = app.invoke(initial_state)

        logger.info("Execution Complete. Saving files...", extra={"run_id": run_id})
        
        if "generated_pages" in final_state:
            for page in final_state["generated_pages"]:
                for key, content in page.items():
                    filename = f"output/{key}.json"
                    with open(filename, "w") as f:
                        json.dump(content, f, indent=2)
                    print(f"Saved: {filename}")
                    
            fq = [p for p in final_state["generated_pages"] if "faq" in p]
            if fq:
                faq_content = fq[0]["faq"]
                count = sum(len(sec['content']) for sec in faq_content['sections'] if isinstance(sec['content'], list))
                print(f"Final Check: FAQ Page contains {count} questions.")

    except Exception as e:
        logger.error(f"Execution Crashed: {e}", extra={"run_id": run_id})
        print(f"Execution Failed: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    main()