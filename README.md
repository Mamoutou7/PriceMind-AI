# PriceMind AI  
**A modular, tool-driven AI system built on top of MCP, where MCP acts as the interoperability layer between specialized services in a data-first pipeline**



## Overview

PriceMind AI is a modular AI system designed to **collect, structure, store, and analyze LLM pricing data** from multiple providers.

It combines:
- Web scraping
- Structured data extraction
- Validation
- Persistence
- Query & comparison

All orchestrated through a **deterministic pipeline augmented with LLM capabilities using MCP (Model Context Protocol)**.

## Architecture
```text
User Query
   ↓
Orchestrator (CLI Agent)
   ↓
Planner → Execution Pipeline
   ↓
┌───────────────┬────────────────────────────┬───────────────┐
│ Scraping MCP  │ Parser MCP                │ Storage MCP   │
│               │                           │               │
│ Scrape pages  │ Deterministic parsing     │ Persist data  │
│ Save raw data │ (regex / rules)           │ Query data    │
│               │           ↓               │               │
│               │     LLM Fallback          │               │
│               │     (Anthropic API)       │               │
└───────────────┴────────────────────────────┴───────────────┘
   ↓
Response Builder (CLI Output)
```

## Core Components

### LLM Agent (Anthropic)
- Orchestrates actions  
- Decides when to call tools  
- Generates final responses  

### MCP (Model Context Protocol)
- Exposes Python functions as callable tools  
- Enables dynamic interaction between the LLM and the system  

### Firecrawl
- LLM-friendly web scraping  
- Cleans and structures webpage content  

### Data Extraction Pipeline
- Converts raw text into structured JSON using the LLM  
- Extracts pricing details from scraped content  

### SQLite Database
- Stores structured pricing data  
- Enables querying and reuse of extracted information  

---

## Workflow

1. The user submits a query  
2. The LLM determines whether a tool is needed  
3. Relevant websites are scraped  
4. Data is extracted into structured JSON  
5. The data is stored in the database  
6. The LLM generates a response based on the data  

---

## Key Features

- LLM tool-calling via MCP  
- Autonomous agent loop  
- Structured data extraction  
- End-to-end data pipeline  
- Persistent storage  

---

## Limitations

- JSON extraction depends on LLM reliability  
- SQLite is not suitable for large-scale production  
- Limited error handling for scraping failures  

---

## Future Improvements

- Add schema validation (Pydantic / JSON Schema)  
- Migrate to PostgreSQL  
- Implement caching and retry mechanisms  
- Add monitoring for tool usage  
- Integrate Retrieval-Augmented Generation (RAG)  

---

## Why This Project Matters

This project showcases how to turn a language model into a **fully functional AI agent** capable of interacting with external systems, collecting real-world data, and generating actionable insights.
---

## Tech Stack

- Python  
- Anthropic API (LLM)  
- MCP (Model Context Protocol)  
- Firecrawl (Web Scraping)  
- SQLite  

---

## Getting Started

### 1. Clone the repository
```bash
git clone https://github.com/your-username/pricemind-ai.git
cd pricemind-ai
```


### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Set environment variables
```bash
ANTHROPIC_API_KEY=your_api_key
FIRECRAWL_API_KEY=your_api_key
```

### 3. 4. Run the project
```bash
python main.py
```