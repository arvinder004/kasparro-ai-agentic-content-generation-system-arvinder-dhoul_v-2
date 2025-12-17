# Kasparro Agentic System Architecture

## 1. Solution Overview
This solution is built on **LangGraph**, a stateful agent orchestration framework. Instead of a rigid, linear script, the system uses a **Directed Acyclic Graph (DAG)** where independent agents operate over a shared state and hand off enriched data to downstream nodes.

End‑to‑end, the system:
- Ingests a raw product record.
- Enriches it with a validated competitor profile.
- Generates a structured set of **15 FAQ Q&A pairs** in parallel.
- Renders three fully‑typed JSON pages (FAQ, Product, Comparison) under the `output/` directory.
- Captures detailed **JSON logs per run** in the `logs/` directory for observability.

## 2. Technical Stack
- **Orchestration**: `LangGraph.StateGraph` for building and running the DAG.
- **LLM Interface**: LangChain with **Google Gemini** models (`gemini-2.5-flash-lite`, `gemini-1.5-flash`).
- **Schemas & Validation**: Pydantic models in `src/schemas/models.py` (`ProductData`, `CompetitorProduct`, `UserQuestion`, `PageOutput`, etc.).
- **Tools / Deterministic Logic**: LangChain `@tool` utilities in `src/tools/logic.py` (e.g. `clean_price_string`, `compare_prices_logic`, `format_benefits_html`).
- **Configuration**: `python-dotenv` for environment variables (e.g. `GEMINI_API_KEY`).
- **Logging**: Python `logging` with a custom JSON formatter and **file‑only** handlers writing to `logs/`.

## 3. Execution Flow

### 3.1 Entry Point (`main.py`)
- Generates a per‑run `run_id` (UUID).
- Builds the initial `AgentState` with:
  - `run_id`
  - `raw_input` (the source product record)
  - `generated_pages` (initially empty)
- Invokes the compiled LangGraph app asynchronously via `app.ainvoke(initial_state)`.
- After graph execution, iterates over `generated_pages` and writes each page as `<page_key>.json` into the `output/` directory (e.g. `faq.json`, `product.json`, `comparison.json`).
- Performs a final quality check on the FAQ page (ensuring the expected number of questions) and logs the count.

### 3.2 Graph Topology (`src/graph.py`)
The DAG is defined using `StateGraph(AgentState)` with the following nodes:
- `analyst`
- `faq_specialist`
- `write_faq`
- `write_product`
- `write_comparison`

Edges:
- Entry point → `analyst`.
- `analyst` → `faq_specialist`.
- `faq_specialist` → `write_faq`.
- `faq_specialist` → `write_product`.
- Conditional from `faq_specialist`:
  - `write_comparison` if both primary and competitor prices are valid.
  - `END` (skip comparison) otherwise.
- `write_faq`, `write_product`, and `write_comparison` all terminate at `END`.

The conditional routing is implemented via `decide_comparison_feasibility`, which inspects the numeric prices from the shared `AgentState` and decides whether a comparison page is meaningful.

## 4. Agent & Node Design

### 4.1 Shared State (`AgentState`)
All nodes operate over a shared `AgentState` object (a typed dictionary) that gradually accumulates:
- `run_id`
- `raw_input`
- `product` (primary `ProductData`)
- `competitor` (`CompetitorProduct`)
- `questions` (`List[UserQuestion]`)
- `generated_pages` (list of rendered page payloads)

### 4.2 Analyst Agent (`analyst_node`)
- **Responsibility**: Ingests and cleans the raw product data, and generates a structured competitor profile.
- **Key steps**:
  - Normalizes price via the `clean_price_string` tool.
  - Instantiates a `ProductData` object from the raw record.
  - Calls Gemini (`gemini-2.5-flash-lite`) with `with_structured_output(CompetitorOutputSchema)` to obtain a strictly‑typed `CompetitorProduct`.
  - Validates the competitor using `validate_competitor_logic` (ensures name and price are meaningfully different from the primary product).
- On success, writes `product` and `competitor` into the `AgentState`.

### 4.3 FAQ Specialist (`faq_specialist_node`)
- **Responsibility**: Generate a diverse, de‑duplicated set of user questions for the FAQ page.
- **Approach**:
  - Defines fixed FAQ categories: `Informational`, `Safety`, `Usage`, `Purchase`, `Comparison`.
  - Spawns **concurrent** async tasks (bounded by a semaphore) via `generate_category_batch` to call Gemini (`gemini-1.5-flash`) and produce `TARGET_PER_CATEGORY` questions per category.
  - Uses Pydantic model `BatchQuestionOutput` to keep the LLM output strictly typed.
  - Deduplicates questions by normalized text and enforces a target of **15 unique questions** across categories.
  - If any questions are missing, fills gaps with a small set of safe, generic fallback questions.
- Final output is stored in state as `questions`.

### 4.4 Writer Agents (Factory) (`writer_node_factory`)
- **Responsibility**: Render final pages (FAQ, Product, Comparison) into the `PageOutput` schema.
- Uses a factory that takes a `page_key` (`"faq"`, `"product"`, `"comparison"`) and returns a node function.
- Each writer node:
  - Looks up a `PageLayout` object from `TEMPLATE_REGISTRY` (page blueprint: sections, headings, allowed block types, etc.).
  - Builds a structured prompt from the layout via `render_layout_instructions`.
  - Constructs a rich `context` object from `product`, `competitor`, and `questions`.
  - Calls Gemini with `with_structured_output(PageOutput)` so the resulting page is strongly typed.
  - Returns a `{page_key: page_content}` mapping appended into `generated_pages`.

## 5. Deterministic Tools & Validation (`src/tools/logic.py`)
- **`clean_price_string`**: Extracts numeric price from strings like `"₹699"` and returns a `float`.
- **`compare_prices_logic`**: Compares two prices and returns a human‑readable sentence indicating which product is cheaper and by how much.
- **`format_benefits_html`**: Converts a list of benefits into an HTML `<ul>` list.
- **`validate_faq_logic`**: (Utility) Checks FAQ lists for total count, uniqueness, and per‑category distribution.
- **`validate_competitor_logic`**: Ensures the competitor is distinct in both name and price from the primary product.

These tools encapsulate all non‑LLM logic to keep prompts lean and behavior predictable.

## 6. Observability & Logging

### 6.1 JSON Log Format
Logging is centralized in `src/logger/logger.py` and uses a custom `JsonFormatter`. Each log entry is emitted as a single JSON line with fields such as:
- `timestamp` (UTC ISO‑8601)
- `level`
- `message`
- `module`
- `function`
- Optional: `run_id`, `node_name`, `duration_ms`, `event`

### 6.2 File‑Only Logging (No Terminal Noise)
- On process start, the logger module:
  - Creates a `logs/` directory at the project root (if missing).
  - Derives a run‑scoped log file name: `agent_langgraph-<YYYYMMDD_HHMMSS>.log`.
- `setup_logger(name)` attaches a **`FileHandler` only** (no `StreamHandler`), so logs are written exclusively to the log file and **not** printed to the terminal.
- All key components (`main`, agents, graph nodes) obtain loggers via `setup_logger` and write structured log lines tagged with `run_id`.

### 6.3 Node‑Level Monitoring (`monitor_node`)
- The `@monitor_node` decorator wraps critical graph nodes (e.g. `analyst_node`, writer nodes) and automatically logs:
  - `node_start` event when a node begins.
  - `node_complete` event with `duration_ms` when it finishes successfully.
  - `node_error` event with `duration_ms` and exception details on failure.
- This gives an execution trace per run that can be sliced by `run_id` and `node_name` for debugging and performance analysis.

## 7. Key Benefits
- **Modularity**: New pages can be added by registering a new template and wiring a new writer node into the graph.
- **Reliability**: Strict Pydantic schemas and validation functions (plus `with_structured_output`) reduce LLM hallucinations and enforce shape.
- **Scalability**: Parallel FAQ generation with concurrency limits makes efficient use of the LLM while respecting rate limits.
- **Observability**: End‑to‑end JSON logging and a shared `AgentState` provide a clear view of data flow, execution timing, and failures for each run.
