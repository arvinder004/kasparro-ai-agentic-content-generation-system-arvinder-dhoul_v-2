# main.py
import json
import os
import sys
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
    print("initializing System...")
  
    os.makedirs("output", exist_ok=True)
    
    try:
        print("Invoking Graph...")

        initial_state = {
            "raw_input": RAW_DATA, 
            "generated_pages": []
        }
        
        final_state = app.invoke(initial_state)
        
        print("Graph Execution Complete")
        
        # Save output
        if "generated_pages" in final_state and final_state["generated_pages"]:
            print(f"Found {len(final_state['generated_pages'])} pages generated.")
            for page_entry in final_state["generated_pages"]:
                for page_type, content in page_entry.items():
                    filename = f"output/{page_type}.json"
                    with open(filename, "w") as f:
                        json.dump(content, f, indent=2)
                    print(f"   - Saved {filename}")
        else:
            print("Warning: No pages were returned in the state.")
            
    except Exception as e:
        print("\n CRITICAL ERROR IN MAIN:")
        print(e)
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()