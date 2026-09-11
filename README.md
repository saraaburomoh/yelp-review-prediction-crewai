# Yelp Review Prediction with CrewAI

A multi-agent AI system built with CrewAI that predicts Yelp star ratings and generates simulated review text. Given a user and a business, a crew of specialized agents retrieves behavioral and business data from a curated Yelp dataset and produces a prediction of the form `{"stars": float, "review": str}`.

The system is fully integrated with the **AgentSociety Challenge** simulator and was evaluated on 35 real inference tasks, achieving an overall quality score of **0.797**.

---

## Evaluation Results (Official Test Run)

| Metric | Score |
|---|---|
| Preference Estimation (star rating accuracy) | 0.777 |
| Review Generation (text quality) | 0.818 |
| **Overall Quality** | **0.797** |

- **35 tasks** completed with **0 errors**
- Average inference time: **279 seconds per task**
- Total inference time: **~2.7 hours** (sequential mode, real LLM)

---

## Repository Structure

This repository contains two complementary components:

```
Rag_Crew_Profiler/
│
├── src/first_crew/                          # Prototype crew (standalone RAG profiler)
│   ├── crew.py                              # Agents, deterministic lookup tools, RAG setup
│   ├── main.py                              # Entry point: loads test data, runs crew
│   ├── config/
│   │   ├── agents.yaml                      # Agent definitions (role, goal, backstory)
│   │   └── tasks.yaml                       # Task descriptions and output format constraints
│   ├── tools/custom_tool.py                 # Utility tools
│   ├── benchmark_indexing.py                # ChromaDB indexing benchmarks
│   └── benchmark_rag.py                     # RAG retrieval accuracy benchmarks
│
├── AgentSocietyChallenge_w_CrewAI/          # Official simulator integration
│   ├── crewai_simulation_agent.py           # Adapter connecting the simulator to the CrewAI Flow
│   ├── run_pipeline.py                      # Full pipeline runner (mock, threading, timeout support)
│   ├── run_simulator_test.py                # Lightweight local test runner
│   ├── evaluate_with_training_data.py       # Evaluation against the training sub-graph
│   ├── src/
│   │   ├── flows/serving_flow.py            # CrewAI Flow: wraps the crew, parses output
│   │   ├── crews/simulation_crew.py         # Production 4-agent crew assembly
│   │   ├── crews/simulation_crew_hierarchical.py  # Hierarchical process variant
│   │   └── tools/interaction_tool_wrapper.py      # Bridges simulator's InteractionTool to CrewAI
│   ├── config/
│   │   ├── agents.yaml                      # Shared agent definitions
│   │   └── tasks.yaml                       # Shared task definitions
│   ├── data/                                # Yelp subset JSON files
│   ├── docs/                                # Architecture docs and onboarding guides
│   ├── scripts/check_compatibility.py       # Pre-test 5-point compatibility checker
│   └── websocietysimulator/simulator.py     # AgentSociety simulator core
│
├── data/                                    # Shared Yelp subset data (user, item, review)
├── docs/                                    # Yelp schema translation and EDA findings
├── pyproject.toml                           # Dependencies and CLI entry points
└── .env                                     # API keys (not committed)
```

---

## System Architecture

### The Four-Agent Pipeline

The production crew (`simulation_crew.py`) runs four agents in sequential order:

| Agent | Role | Tools | Max Iterations |
|---|---|---|---|
| `user_analyst` | Yelp User Profiler | `Interaction Tool Wrapper` | 6 |
| `item_analyst` | Yelp Restaurant Analyst | `Interaction Tool Wrapper` | 6 |
| `web_researcher` | Senior Research Analyst | `serper_search_tool` (internet search) | 3 |
| `prediction_modeler` | Review Prediction Expert | None (synthesis only) | 6 |

Each task passes its context forward: the `predict_review_task` explicitly receives the outputs of all three preceding tasks as context before generating the final prediction.

### The Three-Layer Retrieval Strategy

A core discovery during development was that **RAG semantic search alone fails for Yelp ID lookups**. Yelp user and business IDs (e.g., `_BcWyKQL16ndpBdggh2kNA`) are random strings with no semantic meaning. A vector similarity search on such strings returns completely unrelated records.

The solution is a three-layer hierarchy:

| Layer | Mechanism | Purpose |
|---|---|---|
| Layer 1 — Deterministic | `interaction_tool_wrapper`: exact API call to simulator | 100% precise user profile, item profile, and review history retrieval by ID |
| Layer 2 — Semantic RAG | `JSONSearchTool` with ChromaDB + HuggingFace embeddings | Thematic discovery (e.g., "salty food", "Vietnamese restaurants", sentiment patterns) |
| Layer 3 — Knowledge Base | `StringKnowledgeSource` from `docs/Yelp Data Translation.md` | Global schema context — field names, data types, and what each Yelp metadata field means |

**Empirical validation:** During a hierarchical test run, the Knowledge Base returned hallucinated stats (review_count: 100, average_stars: 4.2). The `interaction_tool_wrapper` immediately returned the ground truth (review_count: 4,274, average_stars: 3.69), correcting the hallucination before it reached the prediction agent.

### The Interaction Tool Wrapper

The `interaction_tool_wrapper` is the critical bridge between the AgentSociety simulator's data API and the CrewAI agents. It wraps the simulator's `InteractionTool` as a standard CrewAI `@tool` and supports four query types:

| `query_type` | Data Retrieved |
|---|---|
| `"user"` | Full user profile (review count, average stars, yelping since, etc.) |
| `"item"` | Full business profile (name, category, location, hours, attributes) |
| `"review_by_user"` | Up to 15 historical reviews written by the user |
| `"review_by_item"` | Up to 15 reviews written about the business |

Reviews are truncated to 500 characters each to prevent context window overflow and simulator timeouts.

### The Serving Flow

`serving_flow.py` wraps the entire crew in a CrewAI Flow with two non-negotiable output state keys:

- `predicted_rating` — the float star prediction (1.0–5.0)
- `generated_review` — the simulated review string

These keys are the data contract with the AgentSociety simulator. Renaming them causes the system to fall back to default values (4.0 stars, "Good.").

The flow includes a multi-strategy JSON parser (`extract_json_from_output`) that handles all common LLM output format failures:
1. Extract from a `json` markdown code block
2. Extract via regex for a raw `{...}` object
3. Parse the full text as JSON directly
4. Fall back to extracting a star number from free text

---

## Dataset

The system operates on a curated sub-graph of the **Yelp Academic Dataset**:

| File | Records | Description |
|---|---|---|
| `data/user_subset.json` | 38 | Core hyper-active users (top 50 filtered to 38 after intersection) |
| `data/item_subset.json` | 432 | Businesses reviewed by these users (sub-graph nodes) |
| `data/review_subset.json` | 4,164 | Historical reviews (training sub-graph edges) |
| `data/test_review_subset.json` | 198 | Ground-truth future reviews (golden validation set) |

The full parent dataset uses an 80/20 temporal cutoff. The subset was generated by extracting the top hyper-active users and their local business graph, then applying strict intersection filtering to ensure every user and item appears in both training and test splits — eliminating the cold-start problem.

---

## Installation

This project uses `uv` for environment management.

```bash
pip install uv
uv sync
```

### Environment Variables

Create a `.env` file in the project root:

```env
# NVIDIA NIM (used for evaluation)
OPENAI_API_KEY=your_nvidia_nim_key
OPENAI_API_BASE=https://integrate.api.nvidia.com/v1
OPENAI_MODEL_NAME=meta/llama-3.3-70b-instruct

# Optional: Internet search (for web_researcher agent)
SERPER_API_KEY=your_serper_api_key
```

---

## How to Run

### Compatibility Check (Run Before the Official Test)

```bash
cd AgentSocietyChallenge_w_CrewAI
uv run python scripts/check_compatibility.py
```

All 5 checks must pass:

| Check | Validates |
|---|---|
| 1 | All package imports succeed |
| 2 | `CrewAISimulationAgent` has all required methods |
| 3 | Constructor signature `__init__(self, llm=None, *args, **kwargs)` |
| 4 | `workflow()` returns `{"stars": float, "review": str}` |
| 5 | API key, model name, and network connectivity |

### Mock Mode (Free — No API Calls)

```bash
cd AgentSocietyChallenge_w_CrewAI
uv run python run_pipeline.py --mock
```

### Real LLM Inference (Full Pipeline)

```bash
cd AgentSocietyChallenge_w_CrewAI
uv run python run_pipeline.py
```

Optional flags:

| Flag | Default | Description |
|---|---|---|
| `--mock` | off | Use mock LLM responses (no token cost) |
| `--threads N` | 1 | Number of parallel worker threads |
| `--timeout SEC` | 300 | Per-task timeout in seconds |
| `--tasks N` | all | Run only the first N tasks (smoke test) |

### Evaluate Against Training Data

```bash
cd AgentSocietyChallenge_w_CrewAI
uv run python evaluate_with_training_data.py
```

### Run the Standalone Prototype Crew

```bash
# From project root
uv run first_crew
```

---

## Key Technical Decisions

**Interaction Tool over RAG for ID lookup.** The simulator's `InteractionTool` provides exact, deterministic record access by ID. This is always called first. RAG semantic search is reserved for thematic queries where semantic meaning matters (e.g., finding reviews mentioning a specific cuisine or complaint).

**Web researcher agent.** An additional `web_researcher` agent with internet access (Serper API) supplements the static 2019–2021 Yelp dataset with current information about businesses — new ownership, closures, recent reviews, or changed menus that would not appear in the historical data.

**Rate limiting protection.** A 60-second sleep is inserted between tasks (when running with a real API key) to prevent hitting NVIDIA NIM rate limits. The pipeline automatically retries on 429 errors with exponential backoff.

**Strict JSON output enforcement.** The `predict_review_task` in `tasks.yaml` explicitly prohibits any text before or after the JSON object and provides an exact format example. The multi-strategy JSON parser in `serving_flow.py` acts as a fallback safety net for any malformed outputs that still slip through.

**max_rpm=5 on the crew.** This rate limit was tuned to balance throughput with the simulator's 300-second per-task timeout. Too low causes unnecessary delays; too high risks 429 errors that pause the entire pipeline.

---

## Dependencies

| Library | Purpose |
|---|---|
| CrewAI 1.9.3 | Multi-agent orchestration, flows, process types |
| LangChain + langchain-community | Tool utilities and chaining infrastructure |
| LangChain HuggingFace | Local embedding model integration |
| sentence-transformers | HuggingFace embedding model runner |
| LiteLLM | Unified LLM API routing (NVIDIA NIM, Ollama, etc.) |
| ChromaDB (via CrewAI Tools) | Persistent vector store for semantic RAG |
| requests | Serper API calls for the web researcher agent |
| Pydantic + pydantic-settings | State models and environment configuration |
