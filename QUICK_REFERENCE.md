# Quick Reference - Interview Prep

## Project in 30 Seconds
**LangGraph-based agentic system that generates 3 web pages (FAQ, Product, Comparison) from raw product data using AI agents orchestrated through a stateful graph workflow.**

---

## Architecture Flow
```
RAW_DATA → [analyst] → {product, competitor, questions} 
         → [write_faq] → [write_product] → [write_comparison] → JSON files
```

---

## Key Files & Their Purpose

| File | Purpose |
|------|---------|
| `main.py` | Entry point, invokes graph, saves outputs |
| `src/graph.py` | Defines workflow, nodes, state, LLM config |
| `src/models.py` | Pydantic models for data validation |
| `src/tools.py` | Deterministic tools agents can call |

---

## Core Concepts

### 1. **AgentState (TypedDict)**
- Shared state flowing through nodes
- `generated_pages` uses `operator.add` to accumulate pages
- `total=False` makes all fields optional

### 2. **Nodes**
- **analyst**: Ingests data, generates competitor & questions
- **write_faq/product/comparison**: Generate pages using factory pattern

### 3. **Tools**
- `format_benefits_html`: List → HTML `<ul>`
- `compare_prices_logic`: Price comparison math
- `clean_price_string`: "₹699" → 699.0

### 4. **Structured Output**
- `with_structured_output()` forces LLM to return valid Pydantic models
- Reduces hallucination, ensures type safety

---

## Key Design Decisions

| Decision | Why |
|----------|-----|
| LangGraph | Modularity, state management, observability |
| Factory Pattern | Reusable writer nodes, easy to extend |
| Pydantic | Type validation, schema enforcement |
| Tools | Deterministic logic, no LLM math errors |
| Sequential Flow | Simple, predictable execution |

---

## Common Interview Questions

**Q: Why LangGraph over scripting?**  
A: Modularity, state management, observability, easy to extend

**Q: What is `operator.add` annotation?**  
A: Tells LangGraph to append to list instead of replacing it

**Q: Why factory pattern?**  
A: Reusable nodes, reduces duplication, easy to add new page types

**Q: What is `with_structured_output()`?**  
A: Forces LLM to return valid Pydantic models, reduces hallucination

**Q: How to add new page type?**  
A: Add template in `tools.py`, add node via factory, add edge in graph

---

## Data Models (Quick)

- **ProductData**: Primary product (name, price, ingredients, etc.)
- **CompetitorProduct**: Generated competitor
- **UserQuestion**: Q&A with category (Safety, Usage, etc.)
- **PageOutput**: Final page structure (meta, sections)
- **AnalystOutput**: Analyst's output (competitor + questions)

---

## Workflow Execution

1. **main.py** creates initial state with `raw_input`
2. **analyst node** parses data, generates competitor & questions
3. **writer nodes** (3x) generate pages sequentially
4. **Pages accumulate** in `generated_pages` list
5. **main.py** saves each page as JSON file

---

## Error Handling

- **Price cleaning**: Try/except, defaults to 0.0
- **LLM calls**: Try/except with error context
- **Main function**: Catches all, prints traceback
- **LLM retries**: `max_retries=2` for transient failures

---

## Improvements (If Asked)

1. Add checkpointing for resumability
2. Parallel page generation
3. Content validation node
4. Externalize templates to config
5. Add caching for identical inputs
6. Better error recovery with exponential backoff

---

## Key Takeaways

✅ **Stateful graph** with sequential agent nodes  
✅ **Factory pattern** for node creation  
✅ **Structured outputs** for reliability  
✅ **Tools** for deterministic logic  
✅ **Pydantic** for type safety  
✅ **Easy to extend** with new page types  

---

**Remember**: The system transforms unstructured product data into structured, formatted web pages using AI agents orchestrated through a graph workflow.


