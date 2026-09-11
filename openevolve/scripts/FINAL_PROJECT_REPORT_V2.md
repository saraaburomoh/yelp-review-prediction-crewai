# Review DNA: Evolving a Dual-Axis Behavioral Taxonomy for Yelp Review Simulation
### LLM & APP Final Project — NDHU Master's Program, Spring 2026
**Course:** LLM & APP | **Instructor:** Yu-Chieh Jack Ho | **Students:** Sara & Vanshika 

*GitHub: [saraaburomoh/openevolve-and-Agent-Society-Final-Project](https://github.com/saraaburomoh/openevolve-and-Agent-Society-Final-Project/tree/main/AgentSocietyChallenge_OpenEvolve)*
---

## Table of Contents
1. [What We Were Trying To Do — And Why It Matters](#1-what-we-were-trying-to-do--and-why-it-matters)
2. [The Evolutionary LLM Search Paradigm — The Idea Behind OpenEvolve](#2-the-evolutionary-llm-search-paradigm--the-idea-behind-openevolve)
3. [How We Applied OpenEvolve — The Core Design Choice](#3-how-we-applied-openevolve--the-core-design-choice)
4. [System Architecture — Three Layers](#4-system-architecture--three-layers)
5. [Crew Design — Five Agents and Their Roles](#5-crew-design--five-agents-and-their-roles)
6. [Task Design](#6-task-design)
7. [The Core Innovation: Review DNA and the Dual-Axis Taxonomy](#7-the-core-innovation-review-dna-and-the-dual-axis-taxonomy)
8. [OpenEvolve Configuration and Setup](#8-openevolve-configuration-and-setup)
9. [Evolution Analysis — 50 Iterations, 47 Programs, 3 Islands](#9-evolution-analysis--50-iterations-47-programs-3-islands)
10. [What OpenEvolve Discovered — Key Findings](#10-what-openevolve-discovered--key-findings)
11. [Performance Results](#11-performance-results)
12. [Conclusion](#12-conclusion)

---

## 1. What We Were Trying To Do — And Why It Matters

### The Problem

The AgentSociety Challenge gives a Yelp user ID and a business ID, and asks: what star rating (1.0–5.0) would this user give this business, and what would their review say?

This sounds simple. It is not.

Consider this real example from the dataset (the "cold start" problem):
- The user's average rating across all their reviews is **N/A** (zero history, no database profile found)
- The business average rating is **4.0 stars** (Anthony's Coal Fired Pizza)
- The ground truth rating this user actually gave: **5.0 stars**

A naive prediction system that simply falls back to the business average would predict ~4.0 stars. That is **completely wrong** (off by a full star). The user had a specific behavioral profile (e.g., a soldier craving authentic pizza) that perfectly aligned with this business. **Generic averaging does not capture human behavioral nuance and fails completely when user history is missing.**

This is why the problem is hard, and this is why we needed something better.

### What We Were Trying To Do

Our goal was to build a multi-agent AI system that:
1. Retrieves all available data about a user and a business from the Yelp dataset
2. Classifies the user into a **behavioral archetype** with a **Review DNA** — a structured profile of their rating tendencies
3. Classifies the business into a **quality archetype** with numerical verdict thresholds
4. Uses these two classifications together (dual-axis) to make a calibrated prediction
5. Then — the key innovation — **uses OpenEvolve to automatically improve the taxonomy** that drives this classification

We did not just want to build a working agent crew. We wanted to discover, through automatic evolution, which user archetypes, business categories, and behavioral rules produce the most accurate predictions. We wanted the AI system to improve its own "theory of human review behavior."

---

## 2. Evolutionary LLM Search — The Idea Behind OpenEvolve

### The Core Concept

Evolutionary LLM Search is a paradigm that searches for better **programs or policies** rather than tuning weights or parameters. 

The three ingredients of this evolutionary search are:
- **An LLM** — to generate and mutate candidate programs
- **An automated evaluator** — to measure how good each candidate is with a numerical score
- **An evolutionary search loop** — to keep the best candidates and use them as parents for the next generation

Formally, the evolutionary search tries to find:

> **f* = argmax S(f)**

Where f is a candidate program (or policy) and S is the evaluator score. The LLM searches the space of all possible programs to find the one with the highest score.

### How We Used OpenEvolve

For our project, we used **OpenEvolve**, an open-source framework designed explicitly for this evolutionary methodology. Here is how the abstract concepts map to our concrete implementation:

| Evolutionary Concept | What It Is in Our Project |
|---------------------|--------------------------|
| Candidate function f | The YAML file containing the agent's taxonomy and rules |
| Evaluator S(f) | The simulation score: `(preference_estimation + review_generation) / 2` |
| LLM Mutator| `minimaxai/minimax-m2.7` via NVIDIA API |
| Evolutionary loop | OpenEvolve's island-based MAP-Elites population |

OpenEvolve also adds two advanced mechanisms to the search process:
- **Island Model**: 3 independent populations that evolve separately and occasionally share successful programs ("migration")
- **MAP-Elites**: Each island maintains a diversity map that keeps programs with different "complexity" and "diversity" characteristics, even if their scores are lower — this prevents the search from getting stuck in a local optimum.



---

## 3. How We Applied OpenEvolve — The Core Design Choice

### The Standard Approach (What Most People Do)

When students use OpenEvolve for agent prompt evolution, the typical approach is: put some agent backstory text inside an EVOLVE-BLOCK, let the LLM rewrite it however it wants, measure the score, repeat. The LLM produces vague variations like "You are an expert analyst who carefully considers all factors..." — mutations that are hard to interpret or learn from.

### Our Approach — Evolving a Symbolic Policy

We gave OpenEvolve something more structured to evolve: a **symbolic decision policy** written in natural language inside the agent's backstory.

Instead of asking "write a better agent persona," we asked OpenEvolve: "discover which behavioral archetypes, numerical thresholds, and interaction rules produce the most accurate star predictions."

Concretely, we hand-designed a **Gen 0 taxonomy** (the starting point) with:
- 4 user behavioral archetypes (TYPE_A through TYPE_D)
- 5 business quality archetypes
- 4 quality verdict thresholds with numerical ranges
- 3 basic cases for when user data is missing

Then we told OpenEvolve's LLM exactly what kinds of mutations to try (via the system prompt):
- Invent new user archetypes (e.g. TREND_FOLLOWER, VALUE_HUNTER)
- Add new DNA variables to the extraction schema
- Change the numerical threshold values
- Invent new interaction cases (e.g. what happens when a HARSH_CRITIC meets a POLARIZING_VENUE?)
- Introduce cognitive biases (Bandwagon Effect, Recency Bias)

This is analogous to evolutionary search algorithms like those used for the Traveling Salesman Problem — instead of searching a space of vague text, we searched a space of structured decision policies. The result was both higher performance AND interpretable findings we can actually learn from.

---

## 4. System Architecture — Three Layers

```
┌──────────────────────────────────────────────────────────────────────────┐
│  LAYER 1: OpenEvolve (Evolution Engine)                                  │
│                                                                          │
│  Every iteration:                                                        │
│  1. Sample a parent YAML from the MAP-Elites database                   │
│  2. LLM mutates the EVOLVE-BLOCK → produces a new YAML                  │
│  3. Write mutated YAML to temporary file                                 │
│  4. Call evaluate(yaml_path) → get combined_score                        │
│  5. Store result in MAP-Elites database across 3 islands                 │
│  6. High-scoring programs become parents for future iterations           │
└──────────────────────────────────────────────────────────────────────────┘
                              │ passes mutated agent config downward
                              ▼
┌──────────────────────────────────────────────────────────────────────────┐
│  LAYER 2: CrewAI Multi-Agent System                                      │
│                                                                          │
│  agents_evolving.yaml ← EVOLVE-BLOCK wraps persona_classifier and        │
│                          prediction_modeler                              │
│  tasks.yaml           ← Fixed task descriptions (not evolved)           │
│  simulation_crew.py   ← Assembles 5-agent crew, sequential process      │
│  serving_flow.py      ← Parses JSON output from final agent             │
└──────────────────────────────────────────────────────────────────────────┘
                              │ outputs {stars, review}
                              ▼
┌──────────────────────────────────────────────────────────────────────────┐
│  LAYER 3: Competition Simulator (Fixed — we cannot change this)          │
│                                                                          │
│  - CacheInteractionTool (LMDB): get_user, get_item, get_reviews         │
│  - Computes: preference_estimation = 1 - (star_error / 5)               │
│  - Computes: review_generation (sentiment + emotion + topic match)      │
│  - combined_score = (preference_estimation + review_generation) / 2     │
└──────────────────────────────────────────────────────────────────────────┘
```

**Key engineering note:** The evaluator runs with `parallel_evaluations: 1` (serial). This was intentional — our 5-agent crew shares an API rate limit of 5 RPM. Running two evaluations simultaneously would cause rate-limit failures and wasted iterations. Serial evaluation is slower but reliable.

---

## 5. Crew Design — Five Agents and Their Roles

```
[Task Input: user_id + item_id]
        │
        ├──────────────────────────────────┐
        ▼                                  ▼
┌───────────────┐                ┌─────────────────┐
│ user_analyst  │                │  item_analyst   │
│ TOOL: DB      │                │  TOOL: DB       │
│ Gets user     │                │  Gets business  │
│ profile +     │                │  profile +      │
│ review history│                │  review history │
└───────┬───────┘                └────────┬────────┘
        │                                 │
        │                    ┌────────────┘
        │                    │
        │                    ▼
        │           ┌────────────────┐
        │           │ web_researcher │
        │           │ TOOL: Search   │
        │           │ Finds external │
        │           │ context online │
        │           └───────┬────────┘
        │                   │
        └──────────┬─────────┘
                   │ (all three outputs combined)
                   ▼
        ┌───────────────────────┐
        │  persona_classifier   │  ← INSIDE EVOLVE-BLOCK (evolved by OpenEvolve)
        │  NO TOOLS             │
        │  Classifies:          │
        │  • USER archetype     │
        │  • Review DNA profile │
        │  • ITEM archetype     │
        │  • Quality verdict    │
        └───────────┬───────────┘
                    │
                    ▼
        ┌───────────────────────┐
        │  prediction_modeler   │  ← INSIDE EVOLVE-BLOCK (evolved by OpenEvolve)
        │  NO TOOLS             │
        │  Outputs:             │
        │  {"stars": X.X,       │
        │   "review": "..."}    │
        └───────────────────────┘
```

### Why Tool-Using Agents Are Protected from Evolution

The `user_analyst` and `item_analyst` both use the **Interaction Tool Wrapper** — a custom tool that queries the Yelp LMDB database. These agents must follow a very specific format to call the tool correctly (the ReAct format: Thought → Action → Observation). If OpenEvolve rewrites their prompts, it might break the tool-calling syntax and make them unable to retrieve data at all.

The `web_researcher` uses the **Serper Search API**. Same reason — tool-calling syntax must be preserved.

Only `persona_classifier` and `prediction_modeler` have **no tools**. They just think and write. These are the safe targets for evolution.

### Key Engineering: Interaction Tool Wrapper

One important design in `interaction_tool_wrapper.py`:

```python
# Limit to top 15 reviews per query
limited_res = raw_res[:15]

# Truncate each review text to 500 characters
for r in limited_res:
    if 'text' in r and len(r['text']) > 500:
        r['text'] = r['text'][:500] + "... [TRUNCATED]"

# Always remove the 'friends' field from user data
res.pop("friends", None)
```

The `friends` field in Yelp user data can contain thousands of user IDs — it would consume the entire LLM context window. Removing it, capping reviews at 15, and truncating text to 500 characters keeps the pipeline fast and prevents 504 timeout errors during the 50-iteration run.

---

## 6. Task Design

The five tasks run in sequence. Each task passes its output as context to the next:

| Task | Agent | Key Design Decision |
|------|-------|---------------------|
| `analyze_user_task` | user_analyst | Always queries both `user` AND `review_by_user` even if profile is missing — handles cold-start |
| `analyze_item_task` | item_analyst | Always queries both `item` AND `review_by_item` even if business is missing |
| `web_research_task` | web_researcher | Uses business name from previous task; falls back to raw ID search if name unknown |
| `classify_persona_task` | persona_classifier | Receives all three above as context; outputs dual-axis classification + Review DNA |
| `predict_review_task` | prediction_modeler | Receives persona + user + item analysis; outputs `{"stars": X.X, "review": "..."}` |

The output format uses double-brace escaping `{{"stars": X.X}}` — this prevents CrewAI's Jinja templating engine from consuming the format string as a template variable.

The `serving_flow.py` implements a 4-strategy JSON extraction fallback, so even if the LLM outputs malformed JSON, the system extracts what it can rather than crashing.

---

## 7. The Core Innovation: Review DNA and the Dual-Axis Taxonomy

### The Problem with Generic Prediction

The simplest approach would be: predict a star rating = average of (user's average_stars + business average_stars) / 2.

This fails on cases like the one mentioned earlier (high-average user, high-average business, but low actual rating). It also fails on cold-start cases where either the user or the business has no data.

We needed a system that could reason about **why** a specific user would rate a specific business in a specific way — not just what the averages say.

### Review DNA — What It Is

**Review DNA** is a structured behavioral fingerprint extracted from a user's review history. Think of it like a medical DNA profile, but for rating behavior. It includes:

| DNA Field | What It Means | Example |
|-----------|---------------|---------|
| `rating_bias` | How much this user's ratings tend to be above or below the Yelp average | +0.55 means "generous rater" |
| `complaint_triggers` | Specific things that historically make this user lower their rating | "slow service", "salty food" |
| `writing_style` | Tone, length, vocabulary pattern | "casual, detailed, uses exclamation marks" |
| `negative_review_risk` | How likely THIS business is to trigger a below-average rating from THIS user | LOW / MEDIUM / HIGH |
| `recency_weight` | How much the most recent experience dominates over older history | 0.9 = very dominated by recency |
| `sentiment_velocity` | Whether this user's ratings are trending up or down over time | Positive = getting more generous |

### Dual-Axis Classification

Instead of just classifying the user, we classify **both** the user and the business, then combine them:

**USER AXIS** — behavioral archetypes:
- TYPE_A (HARSH_CRITIC): drops stars sharply when any complaint trigger appears
- TYPE_B (GENEROUS_RATER): defaults to 4-5 stars unless severely disappointed
- TYPE_C (BALANCED_REVIEWER): calibrates proportionally across food, service, value
- TYPE_D (ELITE_CONNOISSEUR): applies stricter standards, penalizes mediocrity
- *[evolved by OpenEvolve: TYPE_E TREND_FOLLOWER, TYPE_F RECENCY_BOOSTER, etc.]*

**ITEM AXIS** — business quality archetypes:
- CONSISTENT_FAVORITE: >65% 4-5★ reviews, reliably good
- POLARIZING_VENUE: high 5★ AND high 1-2★ counts — love-it-or-hate-it
- DECLINING_QUALITY: recent reviews trending lower than older ones
- NICHE_SPECIALIST: high stars but from a specific audience subset
- AVERAGE_PERFORMER: mostly 3-4★, no strong signal
- *[evolved by OpenEvolve: EMERGING_TREND, MOMENTUM_LEADER, etc.]*

**The intersection creates CASE-based rules:**

```
HARSH_CRITIC × POLARIZING_VENUE → CASE E → predict 2.5-3.5 (critic focuses on flaws)
TREND_FOLLOWER × CONSISTENT_FAVORITE → CASE G → boost +0.3 (social proof amplified)
GENEROUS_RATER × DECLINING_QUALITY → CASE D → reduce -0.35 (generosity has limits)
user MISSING × EXCELLENT item → CASE A → predict 4.5-5.0 (item signal is primary)
```

This is not a neural network. There are no learned weights. The LLM agent reads this taxonomy and executes it as a decision policy. **OpenEvolve's job is to find the best version of this policy.**

---

## 8. OpenEvolve Configuration and Setup

### What We Configured and Why

```yaml
max_iterations: 50          # Required by assignment
diff_based_evolution: false  # CRITICAL: diff mode corrupts YAML structure
language: "text"             # We're evolving YAML text, not Python code
max_code_length: 20000       # Large enough for the growing taxonomy

database:
  num_islands: 3             # 3 independent evolution lineages
  population_size: 50        # Up to 50 programs stored per checkpoint
  elite_selection_ratio: 0.2 # Top 20% are preferred as parents
  exploitation_ratio: 0.7    # 70% of time: refine good programs; 30%: explore new ones
  migration_interval: 10     # Every 10 iterations, share best programs between islands
  feature_dimensions:
    - "complexity"           # MAP-Elites tracks program complexity
    - "diversity"            # MAP-Elites tracks program diversity

evaluator:
  parallel_evaluations: 1   # Serial — avoids rate limit contention
  timeout: 900              # 15 minutes max per evaluation
```

### The System Prompt — Directing the Search

The OpenEvolve configuration includes a **system prompt for the LLM mutator**. This is different from the agent backstories — it tells the LLM *how* to mutate. Key directives we included:

```
MUTATION DIRECTIVES:
- Invent entirely new behavioral profiles (e.g., "TREND_FOLLOWER")
- Add new variables to the Review DNA extraction schema
- Alter the mathematical formulas for quality verdict thresholds
- Invent new CASES for complex edge conditions
- Introduce cognitive biases (Recency Bias, Bandwagon Effect)
- Design decision trees to weigh User DNA vs. Item Sentiment

HARD RULES:
- Do NOT change the YAML keys (persona_classifier, prediction_modeler)
- Do NOT use markdown code blocks — return raw YAML only
- Do NOT remove the EVOLVE-BLOCK markers
```

The mutation directives gave OpenEvolve a **structured search direction**: don't just paraphrase, actually discover new concepts. The hard rules prevented format corruption that would waste iterations.

---

## 9. Evolution Analysis — 50 Iterations, 47 Programs, 3 Islands

### Overview

The 50-iteration run produced:
- **47 evaluated programs** (3 were removed due to population size limit)
- **7 generations** of evolution
- **3 independent island lineages**
- **6 catastrophic failures** (score: 0.2763)
- **Best score: 0.9128** (found at iteration 48)

Final island status:
```
Island 0: 16 programs, best=0.8988, avg=0.7868
Island 1: 18 programs, best=0.8988, avg=0.8003
Island 2: 13 programs, best=0.9128, avg=0.7705  ← produced the best overall
```

### Phase 1 — Generation 0: The Seed (Score: 0.8614)

**Program: `95465d89`** (Gen 0, Island 0, the starting point)

This is the hand-designed taxonomy we created before running OpenEvolve. It contained:
- 4 user archetypes (HARSH_CRITIC, GENEROUS_RATER, BALANCED_REVIEWER, ELITE_CONNOISSEUR)
- 5 business archetypes
- 4 quality verdict thresholds (EXCELLENT/GOOD/MIXED/POOR)
- 3 prediction cases (A/B/C)

**Score: 0.8614** — this became the baseline that all future mutations tried to beat.

This is the "f₀" (initial function) in the FunSearch formulation. Everything that follows is the LLM searching for f* — the version that maximizes the evaluator score.

---

### Phase 2 — Generation 1: The Taxonomy Explosion (Scores: 0.8879–0.8931)

**Key programs: `5953d050` (0.8931), `379fb80f` (0.8890), `d52204c4` (0.8879)**

All three islands produced Gen 1 mutations from the same parent. The LLM made three simultaneous structural changes that significantly improved performance:

**Change 1: User Taxonomy Expansion (4 → 8 types)**

The original 4 archetypes were not enough to capture behavioral diversity. OpenEvolve invented four new types with explicit DNA parameters:

```yaml
- TYPE_E (TREND_FOLLOWER): A user who gravitates toward popular/high-rated venues
  DNA: social_proof_weight (0.4), popularity_correlation
- TYPE_F (VALUE_HUNTER): Weights price-to-quality ratio heavily
  DNA: value_sensitivity (0.5), price_awareness_high
- TYPE_G (RECENCY_BIASED): Most recent experience dominates rating
  DNA: recency_weight (0.6-0.8), temporal_focus
- TYPE_H (EMOTIONAL_RATER): Peak emotional moment overrides logic
  DNA: emotional_peak_dominance (0.7), swing_potential_high
```

Notice that the LLM didn't just add names — it added **numerical DNA parameters** for each type. This is important: when `prediction_modeler` reads `social_proof_weight (0.4)`, it can use that number to calibrate its prediction.

**Change 2: Item Taxonomy Expansion (5 → 8 types)**

New archetypes for business situations not covered by the original 5:
- `UNDERPERFORMER`: Low average but hidden strengths in attributes — potential hidden gem
- `INFLATED_HYPE`: Many reviews clustering at 4-5★ despite recent decline
- `NEW_ARRIVAL`: Fewer than 10 reviews — high uncertainty

**Change 3: Cognitive Bias Calibration Layer Added**

This was the most significant structural invention. The best Gen 1 program (`5953d050`) added a completely new section to `prediction_modeler`'s backstory:

```yaml
COGNITIVE BIAS CALIBRATION:
- BANDWAGON EFFECT: TREND_FOLLOWER + CONSISTENT_FAVORITE → add +0.2 to +0.4 stars
- ANCHORING: User with stable average_stars → cluster tightly around that anchor
- RECENCY BIAS: RECENCY_BIASED users → weight last review at 50%+ of prediction
- NEGATIVITY_BIAS: HARSH_CRITIC → multiply complaint triggers by 1.5x

PREDICTION HEURISTIC (apply in order):
1. Start with item_quality_verdict baseline
2. Apply user archetype adjustment
3. Apply CASE-specific adjustments
4. Apply cognitive bias calibrations
5. Clamp to [1.0, 5.0]
6. Round to nearest 0.5
```

The 6-step ordered heuristic converted the prediction from "reason about everything at once" to a deterministic algorithm. This was a key discovery — **explicit procedural reasoning outperforms implicit reasoning** for this task.

**Insight from Phase 2:** A jump from 0.8614 to 0.8931 (+3.7%) in the first generation shows the initial taxonomy had significant room for improvement. The most valuable addition was the structured prediction heuristic and the cognitive bias layer.

---

### Phase 3 — Generations 2–3: The Complexity Trap (Scores: 0.83–0.89)

**Key programs: `9e2ae1e7` (0.8908), `9e97cc6b` (0.8327)**

After the Gen 1 peak, the evolution entered a complexity accumulation phase. The LLM kept adding:
- More user types (8 → 9)
- More item types (8 → 9 → 10)
- More prediction cases (10 → 14 → 18)
- More DNA variables

The Gen 3 program `9e97cc6b` (Island 2) reached maximum complexity with 18 prediction cases including CASE O through CASE R — all dealing with a TYPE_I (NOVICE_REVIEWER) combined with a NEW_ARRIVAL business. This program scored only **0.8327** — worse than the Gen 1 peak.

**What happened:** Overfitting to the taxonomy structure. With only 1 evaluation task, very specific case combinations were never actually triggered, so the extra rules added noise rather than signal. More rules did not mean better predictions.

**Insight from Phase 3:** There is a complexity-accuracy tradeoff. The optimal complexity level for this task is not the maximum possible.

---

### Phase 4 — Generation 4: Catastrophic Failures and the Breakthrough

This was the most analytically interesting phase of the entire evolution.

#### The Catastrophic Failures (Score: 0.2763)

**Programs: `54633490`, `bac7dfb3`, `689cc760`, `df67f755`, `e7cfd961`, `7d66ab0f`** — six programs all scoring exactly 0.2763

All six failed for the **same reason**: the LLM mutator wrote its reasoning as prose commentary **before** the YAML content, making the file invalid.

Example from program `54633490` (the first failure):
```
Looking at the evolution history, I can see a clear pattern: the current program 
(0.8327) has the MOST complexity but the LOWEST score. The best performer (Program 1 
at 0.8542) is actually simpler with 8 user types, 9 item types, and 14 prediction cases.

Key observations:
- Adding TYPE_I (NOVICE_REVIEWER) and NEW_ARRIVAL item type hurt performance
...

My strategy: Simplify back toward the best-performing architecture...

# === Phase 1: Agents Integrated from FirstCrew ===
```

The YAML parser failed at line 1 because it encountered prose text, not YAML. The crew received no valid agent configuration, `preference_estimation` collapsed to 0.0, and the final score was `(0.0 + 0.5526) / 2 = 0.2763` (the review generation component produced a minimal score from the fallback behavior).

**What makes this remarkable:** The LLM's analysis was *correct*. It correctly identified:
- That complexity had hurt performance (the Gen 3 overfitting problem)
- That simpler Gen 1 programs outperformed complex Gen 3 programs
- That TYPE_I NOVICE_REVIEWER and NEW_ARRIVAL were the problematic additions

The LLM was doing **meta-reasoning about the evolution history** — reading past scores and forming a strategy. It just failed to output valid YAML. This is emergent behavior that the FunSearch paradigm produces: the search process became self-aware of its own trajectory.

The reason this happened 6 times (instead of being corrected after the first failure) is that each island evolves independently. Islands 0, 1, and 2 all independently reached the "let me analyze history" behavior, and each time the same format failure occurred.

**Error from the terminal log:**
```
Task 0 failed with error: while scanning a simple key
  in ".../tmp_63rx2gm.yaml", line 4, column 1
could not find expected ':'
```

#### The Breakthrough — Program `2dd64847` (Score: 0.9128)

**Program: `2dd64847`** (Gen 4, Island 2, parent: `9e97cc6b`)

This is the best program in the entire run. Its parent (`9e97cc6b`) scored only **0.8327** — one of the worst programs outside the catastrophic failures. This is a striking finding: **the best solution came from a failing parent.**

How? The MAP-Elites island model preserves "diverse" programs even when their scores are lower. `9e97cc6b` was the most complex program in Island 2, sitting in a unique cell of the diversity map. When sampled as a parent, the LLM correctly identified that it was too complex and performed a radical simplification:

**What changed from parent (0.8327) to best program (0.9128):**

```diff
- USER TAXONOMY (9 TYPES → 6 TYPES)
  Removed: TYPE_G (SKEPTICAL_USER), TYPE_H (LOYAL_REGULAR), TYPE_I (NOVICE_REVIEWER)
  Added: TYPE_F (RECENCY_BOOSTER) — a NEW concept not in the original

- ITEM TAXONOMY (10 TYPES → 6 TYPES)  
  Removed: HIDDEN_GEM, ESTABLISHED_CLASSIC, RISING_STAR, BUDGET_FRIENDLY, NEW_ARRIVAL
  Added: EMERGING_TREND — a NEW concept (business with recent review surge)

- ITEM QUALITY VERDICT changed:
  EXCELLENT threshold: >75% AND ≥4.2 → >72% AND ≥4.1 (slightly relaxed)
  Removed the SOLID tier
  Removed VARIANCE ADJUSTMENT and complex WEIGHTED SCORING FORMULA

- PREDICTION CASES reduced: 18 → 12
  Removed all NOVICE_REVIEWER and NEW_ARRIVAL-related cases

- DNA representation changed from numeric weights:
  (recency_weight=0.75, rating_bias=-0.45)
  to capability descriptions:
  (complaint_trigger_sensitivity: 1.5x multiplier, tolerance_threshold: 0.3)
```

The key insight the LLM found: **capability-based DNA descriptions outperform numeric DNA weights**. Telling an LLM "complaint triggers are amplified 1.5×" gives it actionable calibration. Telling it "recency_weight=0.75" gives it a number it has no way to actually apply.

The two **new archetypes** invented in this program are also interesting:

- **TYPE_F (RECENCY_BOOSTER)**: "A user whose recent reviews trend higher than their historical average, showing a positivity drift over time." This is different from RECENCY_BIASED — it's not just that recent reviews dominate, it's that they're systematically more positive. A user who is becoming *more generous* over time.

- **EMERGING_TREND**: "A business with recent review activity surge (>50% of reviews in last 3 months) and improving ratings." This captures a business that is currently being discovered by the public — its future trajectory matters more than its historical average.

**Why did simplification help so much?**

With only 1 task in the evaluation, the LLM executing the policy has to read and apply ALL the rules in one pass. A simpler, cleaner taxonomy means the executing LLM can apply it more accurately. A 12-case taxonomy is easier to reason through than an 18-case one, especially when some of the 18 cases involve rare edge conditions (NOVICE_REVIEWER + NEW_ARRIVAL) that may not be present in the evaluation task.

---

### The Island Competition — Three Independent Searches

One of OpenEvolve's key features is the **Island Model**: three populations that evolve independently. Here is what each island found:

| Island | Best Score | Best Program | Strategy Discovered |
|--------|-----------|-------------|---------------------|
| Island 0 | 0.8988 | `640bf969` (Gen 4) | PRECISION-CALIBRATED taxonomy, 5 user types, clean thresholds |
| Island 1 | 0.8988 | `5b66783c` (Gen 4) | Added RECENCY_CRITIC + SERIAL_LOYALIST archetypes |
| Island 2 | **0.9128** | `2dd64847` (Gen 4) | Radical simplification + RECENCY_BOOSTER + EMERGING_TREND |

All three islands converged on a similar insight (simplification is better than complexity) but arrived at different specific solutions. Island 2 found the globally best solution by taking the most aggressive simplification step.

**Migration** (sharing programs between islands at iteration 10, 20, 30, 40) allowed the "PRECISION-CALIBRATED" label and DNA format discovered by Islands 0 and 1 to influence Island 2's evolution, even though Island 2 ultimately took a different path.

---

### The Full Score Trajectory

| Checkpoint | Top Score | Average | Notable Event |
|-----------|-----------|---------|---------------|
| Gen 0 (seed) | 0.8614 | 0.8614 | Hand-designed, 4 user types |
| Checkpoint 10 | 0.8931 | 0.8684 | Gen 1 peak: taxonomy explosion |
| Checkpoint 15 | 0.8931 | 0.8251 | Plateau + first catastrophic failure (0.2763) |
| Checkpoint 50 (final) | **0.9128** | 0.7874 | Simplification breakthrough at iteration 48 |

The average dropped from 0.8684 to 0.7874 due to the 6 catastrophic failures pulling the mean down. But the **best score improved substantially** from 0.8931 to 0.9128. This is exactly what island-based MAP-Elites is designed to produce: find the global best even if the average fluctuates.

---

## 10. What OpenEvolve Discovered — Key Findings

### Finding 1: Capability-Based DNA Beats Numeric Weights

Gen 0 and early Gen 1 programs used numeric DNA parameters:
```
TYPE_A: DNA: recency_weight=0.75, social_proof_sensitivity=0.25, rating_bias=-0.45
```

The best program (`2dd64847`) uses capability descriptions instead:
```
TYPE_A: DNA: complaint_trigger_sensitivity (1.5x multiplier), tolerance_threshold (0.3)
```

When `prediction_modeler` reads "rating_bias=-0.45," it has to decide what that means. When it reads "complaint triggers are amplified by 1.5×," it has direct, actionable instructions. The evolution discovered that **LLM agents execute natural-language instructions better than they interpret abstract numbers.**

### Finding 2: The Optimal Taxonomy Size for 1-Task Evaluation

The evolution explored taxonomies ranging from 4 user types (Gen 0) to 11 user types (Gen 3 overfit). The final best program settled on **6 user types and 6 item types**. The sweet spot appears to be: enough archetypes to cover the main behavioral patterns without creating rare edge cases that are hard to reason about.

### Finding 3: Cold-Start Requires Its Own Strategy

The task for this evaluation (user `PZ47ZU2aXZNd9SKm-Ua7JA`) had **no data in the database** — both the user profile and the user's reviews returned "not found." This is the hardest possible case. The system had to rely entirely on the business data (Anthony's Coal Fired Pizza, Tampa FL, 4.0★ average).

The evolved CASE A rule handled this correctly:
```
CASE A (user missing): use item_quality_verdict thresholds → EXCELLENT → predict 4.5-5.0
```

The system predicted **4.5 stars**, and the business was rated EXCELLENT (79.9% positive reviews). The ground truth was **5.0 stars**. The star error was 0.5, giving `preference_estimation = 0.9000`. This is an excellent result for a complete cold-start case.

### Finding 4: The LLM Can Reason About Its Own Evolution (With Format Risks)

Six programs failed because the LLM mutator wrote analytical prose before the YAML output. This was not random garbage — it was coherent analysis of the evolution trajectory. The LLM had read the population history and formed correct conclusions. The failure was purely in output formatting.

This has a practical implication: in future runs, the system prompt should explicitly say "Output ONLY valid YAML. Do not write any analysis or commentary before or after the YAML content." A one-line addition would have prevented all 6 failures.

### Finding 5: High-Quality Results Can Come from Low-Quality Parents

The best program (`2dd64847`, score 0.9128) came from one of the lowest-scoring non-failure programs (`9e97cc6b`, score 0.8327). This is possible because of the MAP-Elites diversity mechanism — the parent was preserved not because of its score, but because it occupied a unique position in the diversity map (most complex program in Island 2). Its complexity made it a useful "parent" for a radical simplification mutation.

---

## 11. Performance Results

### Final Metrics (Best Evolved Program — `2dd64847`)

```
preference_estimation  = 0.9000   (star rating accuracy)
review_generation      = 0.9256   (review text quality: sentiment + emotion + topic)
overall_quality        = 0.9128   ← combined_score (primary metric)
```

### Breakdown of Combined Score

The `combined_score = (preference_estimation + review_generation) / 2`

- `preference_estimation = 1 - (|predicted_stars - actual_stars| / 5)` — measures how close our star prediction was to the ground truth. Score of 0.9 means our error was `0.5/5 = 0.1` — we predicted 4.5, ground truth was 5.0.
- `review_generation` measures how similar our generated review text is to the real review — using sentiment analysis, emotion classification (Twitter-RoBERTa model), and topic similarity (sentence embeddings). Score of 0.9256 is very high — the generated review matched the emotional tone and topic of the real review closely.

### Comparison Table

| Version | Program ID | Score | Description |
|---------|-----------|-------|-------------|
| Gen 0 seed | `95465d89` | 0.8614 | Hand-designed, 4 user types, 5 item types, 3 cases |
| Gen 1 best | `5953d050` | 0.8931 | LLM adds 4 new archetypes + cognitive bias layer |
| Gen 3 worst (valid) | `9e97cc6b` | 0.8327 | 9 user types, 10 item types, 18 cases — overfit |
| Catastrophic failures | multiple | 0.2763 | Invalid YAML due to prose prefix |
| **Gen 4 best** | **`2dd64847`** | **0.9128** | **Radical simplification: 6 user types, 12 cases** |
| **Total improvement** | | **+5.14%** | 0.8614 → 0.9128 |

*Evaluated on: 1 task (TASKS=1) as required. Single-task evaluation means scores reflect some variance from LLM stochasticity.*

---

## 12. Conclusion

### What We Built

A 5-agent CrewAI crew for Yelp review simulation, where the two reasoning agents (`persona_classifier` and `prediction_modeler`) execute an **evolvable symbolic decision policy** — the Dual-Axis Taxonomy and Review DNA framework — rather than relying on unconstrained free-form reasoning.

### What OpenEvolve Did

Over 50 iterations across 3 independent island populations:
- Explored 47 distinct taxonomy configurations
- Found that **capability-based DNA descriptions** outperform numeric weight parameters
- Discovered that **6 archetypes per axis** is better than 4 (too few) or 11 (too many) for 1-task evaluation
- Invented two new behavioral concepts not in the original design: **RECENCY_BOOSTER** (user whose generosity increases over time) and **EMERGING_TREND** (business currently being discovered)
- Produced a **6-step ordered Prediction Heuristic** as an emergent algorithmic policy
- Demonstrated **emergent meta-reasoning**: the LLM analyzing its own evolution history to propose simplification strategies (with a format failure that itself became a finding)
- Achieved a final combined_score of **0.9128** — a +5.14% improvement over the hand-designed baseline

### Why This Approach Matters

The standard approach to prompt engineering is manual iteration: a human writes a prompt, tests it, edits it, tests again. This is slow, biased by human assumptions, and limited to what the human can think to try.

By encoding the prediction logic as a structured, evolvable taxonomy inside agent backstories, we allowed the LLM to search the space of possible "theories of human review behavior" automatically. In 50 iterations, it explored archetypes, threshold values, interaction cases, and cognitive bias rules that we would not have thought to design by hand.

The result is a prediction system that is both **higher performance** (0.9128 combined score) and **interpretable** — every decision the system makes can be traced back to a named archetype, a DNA parameter, or a case rule that has a human-readable justification.

This is the promise of Evolutionary LLM Search applied to agent design: use AI to search the space of AI policies, and end up with something both better and more understandable than what a human would design alone.

---



