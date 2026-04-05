# Changelog

All significant changes to this project will be documented here.
## [Unreleased]

### CI/CD

- Narrow bandit scope and suppress safe SQL false positive (security)

- Restrict bandit scope and suppress safe SQL false positive (security)

- Restrict bandit scope and suppress safe SQL false positive (security)


### Corrections

- Restore PriceRepository implementation (storage)

- Restore PriceRepository implementation (storage)

- Improve tool result handling and clean CLI output (orchestrator)

- Normalize currency symbols before field length validation (parsing)


### Features

- Add CLI session, routing, planning, and tool execution (orchestrator)

- Add MCP scraping server and raw content persistence (scraping)

- Add parser MCP server with validation and LLM fallback extraction (parser)

- Add SQLite connection and repository layer (storage)

- Expose storage MCP tools for insert, retrieval, and comparison (storage)

- Improve routing, planning and per-provider execution context (orchestrator)

- Deterministic parser + LLM fallback + validation improvements (parsing)

- Normalize models and improve repository layer (storage)

- Add basic price comparison summary service (analytics)

- Let LLM decide whether tools are needed (orchestrator)


### Maintainance

- Initialize project structure and development tooling

- Add local testing and parser utilities (scripts)


### Refactoring

- Unify providers config and improve settings handling (core)

- Improve firecrawl service and metadata persistence (scraping)


### Tests

- Add step-by-step pipeline validation scripts

- Add unit tests for routing, planning, and storage repositories

- Add integration and unit tests for full pipeline



