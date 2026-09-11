# 🚀 AgentSociety Yelp Multi-Agent Prediction System

This directory contains the finalized, production-stable CrewAI pipeline for the **AgentSociety Challenge (Track 1: Recommendation)**. The system predicts Yelp review ratings and generates authentic review text using a 4-agent sequential workflow.

---

## 📊 Final Performance Metrics (2026-05-06)

Evaluated against the official 183-task real-data subset:

| Metric | Score | Status |
| :--- | :--- | :--- |
| **Preference Estimation** | **84.4%** | ✅ Excellent |
| **Review Generation** | **76.1%** | ✅ Stable |
| **Overall Quality** | **80.3%** | ✅ **Pass** |

---

## 🏛️ System Architecture

The pipeline follows a **Sequential Process** to minimize LLM reasoning overhead and maximize stability against API rate limits.

### 1. The Bridge (`crewai_simulation_agent.py`)
Connects the official AgentSociety `Simulator` to our CrewAI `Flow`.
- Injects the official `InteractionTool` into our custom wrapper.
- Implements mandatory 30-second inter-task cooling.

### 2. The Flow (`src/flows/serving_flow.py`)
Manages the orchestration and state.
- **JSON Sanitization**: 4-layer regex fallback to handle messy LLM outputs.
- **Error Handling**: Graceful fallback to 4.0 stars on API crashes.

### 3. The Crew (`src/crews/simulation_crew.py`)
A sequential team of 4 specialized agents:
- **Yelp User Profiler**: Analyzes historical behavior and "Elite" status.
- **Yelp Restaurant Analyst**: Deep-dives into attributes and price ranges.
- **External Trend Researcher**: Fetches real-time context via Google Search (Serper).
- **Review Prediction Expert**: Synthesizes all data into the final JSON output.

---

## 🛠️ Setup & Execution

### Prerequisites
- Python 3.12+
- [Astral `uv`](https://docs.astral.sh/uv/)
- NVIDIA NIM API Key (`meta/llama-3.3-70b-instruct`)
- Serper.dev API Key (for web research)

### Environment Variables
Create a `.env` file or export:
```bash
NVIDIA_API_KEY=nvapi-xxxx
NVIDIA_API_BASE=https://integrate.api.nvidia.com/v1
SERPER_API_KEY=xxxx
```

### Running the Pipeline

**1. Structural Validation (Free)**
Test the full wiring without using API tokens:
```bash
uv run python run_simulator_test.py --mock
```

**2. Sample Real Evaluation**
Run the first 5 tasks of the 183-task subset:
```bash
uv run python run_real_test.py
```

**3. Official Full Evaluation**
```bash
uv run python evaluate_with_training_data.py
```

---

## ✨ Technical Highlights
- **Rate-Limit Armoring**: `max_rpm=10` + `max_workers=1` ensures stability on free-tier NIM accounts.
- **Token Diet**: Automatically strips the `friends` field and truncates reviews to 500 chars to fit 128K context windows.
- **YAML-First**: Strictly complies with `crewai-strict-separation.md`. No hardcoded prompts in Python.
- **Determinism**: Sequential execution ensures consistent context passing across agents.

---

## 📁 Key Files
- `config/agents.yaml`: Personas and LLM configuration.
- `config/tasks.yaml`: Task descriptions and expected outputs.
- `presentation.pdf`: Final 23-page academic presentation deck.
- `pipeline_report_final.md`: Exhaustive technical audit and data verification.
