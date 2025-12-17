## Kasparro Agentic System

This repository contains an agentic content generation system built on **LangGraph** and **LangChain**. It ingests a single product record and produces three structured JSON pages (FAQ, Product, Comparison), along with detailed JSON logs for observability.

### Features
- **Agentic Orchestration**: Directed Acyclic Graph (DAG) of nodes built with `LangGraph.StateGraph`.
- **Typed LLM I/O**: Uses Pydantic models and `with_structured_output` to strictly enforce response schemas.
- **Parallel FAQ Generation**: Asynchronously generates and deduplicates a diverse set of user questions.
- **Template‑Driven Rendering**: Writer agents render FAQ, Product, and Comparison pages from reusable layout templates.
- **Structured Logging**: JSON logs for each run, written to timestamped files in `logs/`.

### Project Structure (High Level)
- `main.py` – Entry point; runs the graph and writes JSON outputs.
- `src/graph.py` – LangGraph DAG definition and routing logic.
- `src/agents/` – Analyst, FAQ specialist, and writer nodes.
- `src/schemas/` – Pydantic models for all typed inputs/outputs.
- `src/tools/` – Deterministic helper tools used by the agents.
- `src/logger/` – JSON logger and node monitoring utilities.
- `docs/` – Additional project documentation.
- `output/` – Generated JSON pages (FAQ, Product, Comparison).
- `logs/` – JSON log files (git‑ignored).

### Prerequisites
- Python 3.11+
- A valid **Google Gemini API** key.

### Setup
1. **Install dependencies**:

```bash
pip install -r requirements.txt
```

2. **Configure environment variables** (e.g. in a `.env` file):

```bash
GEMINI_API_KEY=your_gemini_api_key_here
```

### Running the Pipeline
From the project root, run:

```bash
python main.py
```

On success, you should see:
- JSON content files in `output/` (e.g. `faq.json`, `product.json`, `comparison.json`).
- A new log file in `logs/` named like `agent_langgraph-YYYYMMDD_HHMMSS.log`.

### Logs & Observability
- Logs are **not printed to the terminal**; they are written as JSON lines to the timestamped log file.
- Each log entry includes fields like `timestamp`, `level`, `message`, `run_id`, `node_name`, and optional timings.

For a deeper architectural explanation, see `docs/projectdocumentation.md`.