# PriceMind AI  
**A modular, tool-driven AI system built on top of MCP, where MCP acts as the interoperability layer between specialized services in a data-first pipeline**

---

## Overview

PriceMind AI is a modular AI system designed to **collect, structure, store, and analyze LLM pricing data** from multiple providers.

Unlike typical LLM-first approaches, PriceMind follows a **data-first, deterministic pipeline**, where LLMs are only used as a fallback when rule-based parsing fails.

It combines:
- Web scraping
- Deterministic parsing (tables, patterns)
- LLM fallback extraction (OpenAI)
- Data validation (Pydantic)
- Persistent storage (SQLite)
- Query & comparison via CLI agent

All orchestrated through a **multi-step tool pipeline using MCP (Model Context Protocol)**.


## Architecture

```text
User Query
   ↓
Orchestrator (CLI Agent)
   ↓
Router → Planner → Execution Pipeline
   ↓
┌───────────────┬──────────────────────────────┬───────────────┐
│ Scraping MCP  │ Parsing MCP                 │ Storage MCP   │
│               │                             │               │
│ Scrape pages  │ Deterministic parsing       │ Persist data  │
│ Save raw data │ (tables / regex)            │ Query data    │
│               │              ↓              │               │
│               │     LLM fallback (OpenAI)   │               │
└───────────────┴──────────────────────────────┴───────────────┘
   ↓
Response Builder (CLI Output)
```


## Core Components
### Orchestrator (Agent Layer)

- Routes user intent (price lookup, compare, refresh, etc.)
- Builds execution plans
- Executes MCP tools step-by-step
- Maintains per-provider execution context

### MCP (Model Context Protocol)
- Exposes Python functions as tools
- Enables modular system composition
- Decouples scraping, parsing, storage

#### Scraping MCP
Uses Firecrawl for LLM-friendly scraping
Saves raw HTML + Markdown
Persists metadata (timestamp, source, files)

#### Parsing MCP
- Deterministic-first extraction
- Markdown tables
- Inline pricing patterns
- LLM fallback (OpenAI) when parsing fails
- Validation via Pydantic models
- Deduplication of extracted records

#### Storage MCP
- SQLite-based persistence
- Normalized schema:
- providers
- models (canonicalized)
- pricing records
- Supports:
- latest prices
- provider comparison

#### Analytics MCP 
- Computes summaries (cheapest provider, etc.)
- Optional layer for future extensions

## Workflow
1. The user submits a query  
2. Router extracts:
   - intent
   - providers
   - model name  
3. Planner builds execution steps
4. Executor runs tools sequentially:
   - scrape → raw content
   - parse → structured records
   - store → database
   - compare → result
5. ResponseBuilder formats output

## Key Features
- Deterministic + LLM hybrid pipeline
- Provider-isolated execution context
- Model name normalization (alias handling)
- Structured validation (Pydantic)
- End-to-end pipeline (scrape → parse → store → query)
- CLI agent loop
- Fully testable (unit + integration + e2e)

## Why This Project Matters
This project showcases how to turn a language model into a **fully functional AI agent** capable of interacting with external systems, collecting real-world data, and generating actionable insights.

## Tech Stack

- Python 3.11+
- OpenAI API (LLM fallback)
- MCP (Model Context Protocol)
- Firecrawl (scraping)
- SQLite
- Pydantic
- Pytest

## Getting Started

### Clone the repository
```bash
git clone https://github.com/your-username/pricemind-ai.git
cd pricemind-ai
```

### Install dependencies
```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

### Set environment variables
```bash
OPENAI_API_KEY=your_api_key
MODEL_NAME=gpt-4o-mini
FIRECRAWL_API_KEY=your_firecrawl_key
```
## Run

### Bootstrap the database:
```bash
python -m scripts.bootstrap_db
```

### Run the orchestrator:
```bash
python -m apps.orchestrator.main
```

### Quick Validation
```bash
python -m scripts.bootstrap_db && pytest
```

## Testing Strategy

### Run all tests
```bash
pytest
```

### Unit tests:
```bash
pytest -m unit
```

### Integration tests:
```bash
pytest -m integration
```

### E2E tests:
```bash
pytest -m e2e
```
### Example:
```bash
show data
price of llama 3.3 70b on groq
compare groq and fireworks for llama 3.3 70b
refresh groq
```

## Current Limitations
- Parsing still imperfect on complex pricing pages
- No true SQL upsert (duplicates possible)
- No snapshot/versioning of data
- SQLite limits scalability
- LLM fallback still heuristic-based

## Future Improvements
- True UPSERT with conflict resolution
- Snapshot-based data versioning
- Advanced model normalization (aliases, fuzzy match)
- HTML-aware parsing (DOM-based extraction)
- Retry & caching layer for scraping
- Observability (logs, metrics)
- PostgreSQL migration
- API layer (FastAPI)
- RAG for historical pricing
