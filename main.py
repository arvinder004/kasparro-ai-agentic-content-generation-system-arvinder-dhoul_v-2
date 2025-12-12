import json
import os
from src.graph import app

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
    print("Starting...")
    
    final_state = app.invoke({"raw_input": RAW_DATA, "generated_pages": []})
    
    os.makedirs("output", exist_ok=True)

    debug_data = {
        "product": final_state["product"].model_dump(),
        "competitor": final_state["competitor"].model_dump(),
        "questions": [q.model_dump() for q in final_state["questions"]]
    }
    with open("output/internal_state.json", "w") as f:
        json.dump(debug_data, f, indent=2)
        

    for page_entry in final_state["generated_pages"]:
        for page_type, content in page_entry.items():
            filename = f"output/{page_type}.json"
            with open(filename, "w") as f:
                json.dump(content, f, indent=2)
            print(f"Saved {filename}")
