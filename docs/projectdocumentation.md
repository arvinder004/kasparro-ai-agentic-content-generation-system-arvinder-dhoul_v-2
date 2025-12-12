# Kasparro Agentic System Architecture

## 1. Solution Overview
This solution is built on **LangGraph**, a stateful agent orchestration framework. It moves away from rigid scripting to a Directed Acyclic Graph (DAG) where independent agents process data, share a common state, and utilize deterministic tools.

## 2. Technical Stack
- **Orchestration**: LangGraph (StateGraph) for managing the workflow DAG.
- **LLM Interface**: LangChain (Google Gemini).
- **Validation**: Pydantic for strict input/output schema enforcement.
- **Tooling**: LangChain `@tool` decorator for logic blocks.

## 3. Agent Design
The system uses a shared `AgentState` object containing the unified data models.

### Nodes:
1.  **Analyst Agent**:
    - **Responsibility**: Ingestion, Cleaning, and Data Enrichment.
    - **Method**: Uses `with_structured_output` to produce strictly typed `CompetitorProduct` and `UserQuestion` objects.
    - **Tools**: `clean_price_string` (Regex) for data normalization.

2.  **Writer Agents (Factory Pattern)**:
    - **Responsibility**: Assembling final pages based on specific templates.
    - **Method**: A reusable node factory that binds specific page templates (FAQ, Product, Comparison).
    - **Tools**: 
        - `compare_prices_logic`: Deterministic math for price comparison.
        - `format_benefits_html`: Logic for HTML formatting.

## 4. Key Improvements over Scripting
- **Modularity**: New pages can be added by simply adding a Template config and a node to the Graph.
- **Reliability**: LangChain's `bind_tools` and `with_structured_output` reduce hallucination significantly compared to manual prompting.
- **Observability**: The State object allows inspecting the data flow at every step of the pipeline.