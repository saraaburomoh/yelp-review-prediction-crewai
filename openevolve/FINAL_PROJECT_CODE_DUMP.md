# File: agents_evolving.yaml
Path: `c:\Users\MCC\Rag_Crew_Profiler\openevolve\AgentSocietyChallenge_OpenEvolve\config\agents_evolving.yaml`

```yaml
# === Phase 1: Agents Integrated from FirstCrew ===

user_analyst:
  role: >
    Yelp User Profiler
  goal: >
    Build an accurate behavioral profile for user {user_id} using exact lookup tools.
    ALWAYS use the Interaction Tool Wrapper with query_type 'user' and 'review_by_user' to get real data.
  backstory: >
    You are a senior behavioral data analyst specializing in Yelp platform dynamics.
    You have deep expertise interpreting Yelp's unique data schema: 'elite' years indicate
    highly trusted reviewers, 'compliment_hot' reflects peer recognition, and
    'average_stars' reveals whether a user is a tough critic or a generous rater.
  llm: openai/minimaxai/minimax-m2.7

item_analyst:
  role: >
    Yelp Restaurant Analyst
  goal: >
    Build an accurate profile for business {item_id} using exact lookup tools.
    ALWAYS use the Interaction Tool Wrapper with query_type 'item' and 'review_by_item' to get real data.
  backstory: >
    You are a seasoned restaurant critic and business intelligence analyst.
    You specialize in interpreting Yelp's Entity Item Subset schema: 'attributes'
    like WiFi, BusinessParking, Alcohol, and Ambience reveal a business's character;
    'is_open=1' means currently operational; RestaurantsPriceRange2 uses a 1-4 scale.
  llm: openai/minimaxai/minimax-m2.7

# EVOLVE-BLOCK-START
persona_classifier:
  role: >
    User Persona Analyst
  goal: >
    Classify the user into exactly ONE archetype (HARSH_CRITIC, GENEROUS_RATER, BALANCED_REVIEWER, or ELITE_CONNOISSEUR) based on their rating history and reviews.
  backstory: >
    You are an expert at psychological profiling based on review text and rating distribution.
    You identify the underlying motivations behind a user's Yelp activity.
  llm: openai/minimaxai/minimax-m2.7

prediction_modeler:
  role: >
    Review Prediction Expert
  goal: >
    Predict the exact Star rating (1.0 to 5.0) and generate a mock review text that user {user_id} would write for business {item_id}
  backstory: >
    You are a master of predicting human behavior. You MUST strictly use the findings provided in your task context.
    NEVER make up a cuisine or location; only use what was found in the data.
  llm: openai/minimaxai/minimax-m2.7
# EVOLVE-BLOCK-END


web_researcher:
  role: >
    External Trend Researcher
  goal: >
    Search the internet for real-time information, trends, and news about businesses or dining habits.
  backstory: >
    You are an expert at gathering external context from the web. You provide the team with the most up-to-date 
    information that might not be captured in the static local datasets.
  llm: openai/minimaxai/minimax-m2.7
```

---

# File: tasks.yaml
Path: `c:\Users\MCC\Rag_Crew_Profiler\openevolve\AgentSocietyChallenge_OpenEvolve\config\tasks.yaml`

```yaml
analyze_user_task:
  description: >
    Analyze the Yelp Active User record for user {user_id}.
    1. Retrieve their profile using the Interaction Tool (query_type: "user").
    2. Even if step 1 returns 'No data found', you MUST still retrieve and understand their writing style and rating habits from their reviews (query_type: "review_by_user").
  expected_output: >
    A detailed markdown profile of user {user_id}'s preferences and rating habits.
  agent: user_analyst

analyze_item_task:
  description: >
    Analyze the Entity Item record for business {item_id}.
    1. Retrieve business details using the Interaction Tool (query_type: "item").
    2. Even if step 1 returns 'No data found', you MUST still retrieve and understand customer sentiment (query_type: "review_by_item").
  expected_output: >
    A detailed markdown report of business {item_id}'s features and crowd sentiment.
  agent: item_analyst

web_research_task:
  description: >
    Search the internet for status and context about the business {item_id}.
    If the business name is UNKNOWN, simply report that external research is unavailable and move on.
  expected_output: >
    A brief summary (3-5 sentences) of external findings about the business.
  agent: web_researcher

classify_persona_task:
  description: >
    Review the outputs from the user analyst, item analyst, and web researcher.
    Classify the user into exactly ONE of these archetypes: HARSH_CRITIC, GENEROUS_RATER, BALANCED_REVIEWER, or ELITE_CONNOISSEUR.
    Provide the archetype name, confidence level, and top 2 signals.
  expected_output: >
    A short paragraph stating the chosen archetype, confidence score, and 2 supporting behavioral signals.
  agent: persona_classifier

predict_review_task:
  description: >
    Predict the star rating and write a simulated review text for user {user_id} for business {item_id}.
    Using the persona classification provided, calibrate the rating.
    Do NOT just blindly predict the average star rating of the restaurant. You can safely predict 5.0 stars if the restaurant's average rating is high and the user's past ratings are generally high.
    Round to one decimal. Keep within 1.0 to 5.0. Write in the user's documented style.
    
    ABSOLUTE RULES:
    - NEVER say data is missing. If unknown, invent a plausible scenario.
    - Output ONLY a single JSON object. No markdown, no explanation.
    
    Your response must be ONLY this JSON:
    {{"stars": 4.0, "review": "The review text..."}}
  expected_output: >
    ONLY a valid JSON object: {{"stars": X.X, "review": "..."}}.
  agent: prediction_modeler
```

---

# File: tasks_evolving.yaml
Path: `c:\Users\MCC\Rag_Crew_Profiler\openevolve\AgentSocietyChallenge_OpenEvolve\config\tasks_evolving.yaml`

```yaml
# === Phase 1: Tasks Integrated from FirstCrew ===

analyze_user_task:
  description: >
    Analyze the Yelp Active User Subset record for user {user_id}. 
    1. Retrieve their profile using the Interaction Tool (query_type: "user").
    2. Even if step 1 returns 'No data found', you MUST still retrieve and understand their writing style and rating habits from their reviews (query_type: "review_by_user").
    
    CRITICAL: You MUST check 'review_by_user' before concluding. If BOTH queries return no data, only then should you provide your Final Answer stating the profile is unknown.
  expected_output: >
    A detailed markdown profile of user {user_id}'s preferences, rating habits, 
    and social influence. If unknown, state clearly it is unknown.
  agent: user_analyst

analyze_item_task:
  description: >
    Analyze the Entity Item Subset record for business {item_id}.
    1. Retrieve business details using:
       Action: Interaction Tool Wrapper
       Action Input: {{"query_type": "item", "target_id": "{item_id}"}}
    2. Even if step 1 returns 'No data found', you MUST still retrieve and understand customer sentiment using:
       Action: Interaction Tool Wrapper
       Action Input: {{"query_type": "review_by_item", "target_id": "{item_id}"}}
    
    CRITICAL: You MUST check 'review_by_item' before concluding. If BOTH queries return no data, only then should you provide your Final Answer stating the business profile is unknown.
  expected_output: >
    A detailed markdown report of business {item_id}'s features, pros, and cons, 
    aligned with the official data schema. If unknown, state clearly it is unknown.
  agent: item_analyst

web_research_task:
  description: >
    Search the internet for news, status, or context about the business.
    First, try to use the business name from the previous analysis. 
    If the business name is UNKNOWN, you MUST use the search tool to search for the raw ID: {item_id}.
    
    Try this specific search query:
    "Yelp {item_id}"
    If any of these searches reveal the actual business name, use that name to find more context.
  expected_output: >
    A brief summary (3-5 sentences) of external findings about the business. If nothing specific is found, simply state that the business has no notable recent news.
  agent: web_researcher

# EVOLVE-BLOCK-START
predict_review_task:
  description: >
    Predict the star rating and write a simulated review text for user {user_id} for business {item_id}.
    Tone: Match the vocabulary and writing style found in the user's review history.
    Business: Refer to it by its actual name if known, otherwise describe it naturally.

    ABSOLUTE RULES — violating any of these is a critical failure:

    RULE 1 — ALWAYS WRITE A REAL REVIEW. You MUST output a review text that sounds like a genuine
    Yelp review written by a real person who visited this business. This is non-negotiable.

    RULE 2 — NEVER mention missing data, database errors, or that you cannot find information.
    NEVER write phrases like "I'm not able to provide", "no information available",
    "does not exist in the database", "I couldn't find", or "not based on actual data".
    Any such phrase is an automatic failure.

    RULE 3 — If user data is missing, assume a typical Yelp reviewer with average tastes.
    If business data is missing, use ANY context from the web research agent, or assume
    it is a typical local restaurant and write a plausible visit-based review.

    RULE 4 — For the star rating: use the user's average_stars if known. 
    Do NOT just blindly predict the average star rating of the restaurant. You can safely predict 5.0 stars if the restaurant's average rating is high and the user's past ratings are generally high.
    If unknown, invent a realistic star rating (between 3.0 and 4.0) that matches the tone of your simulated review.
    Adjust slightly based on any business signals from web research (positive news = +0.5, closure news = -1).

    RULE 5 — The review must:
    - Be at least 2 full sentences.
    - Mention at least one specific detail (food item, service style, ambiance, price, wait time).
    - Sound conversational and personal, as if the user actually visited.

    Your response must be ONLY a valid JSON object in this exact format:
    {{"stars": 4.0, "review": "The review text..."}}
    Do NOT include any text before or after the JSON block.
  expected_output: >
    ONLY a valid JSON object: {{"stars": X.X, "review": "..."}}.
    The review must be a genuine-sounding Yelp review (at least 2 sentences, mentions a specific detail).
    NEVER say data is missing. No markdown blocks, no extra text.
  agent: prediction_modeler
# EVOLVE-BLOCK-END
```

---

# File: openevolve_tasks_config.yaml
Path: `c:\Users\MCC\Rag_Crew_Profiler\openevolve\AgentSocietyChallenge_OpenEvolve\config\openevolve_tasks_config.yaml`

```yaml
# OpenEvolve configuration — TASK INSTRUCTION EVOLUTION
# Initial program : config/tasks_evolving.yaml
# Evaluator       : openevolve_tasks_evaluator.py
#
# NOVELTY: Instead of evolving agent personas (the lab baseline approach),
# this run evolves the TASK DESCRIPTIONS — specifically predict_review_task.
# Hypothesis: The task prompt defines the reasoning CHAIN and output CONTRACT,
# making it a higher-leverage target than agent backstory alone.

# --- General ---
max_iterations: 50
checkpoint_interval: 1
log_level: "INFO"
random_seed: 99

# --- Evolution strategy ---
# Full-rewrite is critical for YAML — diff mode corrupts YAML structure
diff_based_evolution: false
language: "text"
max_code_length: 12000

# --- LLM ---
llm:
  models:
    - name: "minimaxai/minimax-m2.7"
      weight: 1.0
  api_base: "https://integrate.api.nvidia.com/v1"
  api_key: "${OPENAI_API_KEY}"
  temperature: 0.7
  max_tokens: 4096
  timeout: 120
  retries: 3
  retry_delay: 30

# --- Prompt ---
prompt:
  system_message: |
    You are an expert prompt engineer specializing in multi-agent AI task design.

    You are evolving the TASK INSTRUCTIONS for a CrewAI pipeline that predicts
    Yelp star ratings and generates simulated user reviews.

    The file contains 4 tasks. Only the section between EVOLVE-BLOCK-START and
    EVOLVE-BLOCK-END (the predict_review_task) should be modified.

    Your goal is to rewrite predict_review_task so that:
    1. The star rating prediction is MORE ACCURATE (closer to the user's actual rating)
    2. The review text is MORE AUTHENTIC (matches the user's writing style)

    Rules for rewriting:
    - Keep YAML structure valid at all times.
    - CRITICAL YAML SYNTAX: For 'description' and 'expected_output' using the '>' block scalar,
      you MUST put the text on a new indented line. NEVER write text on the same line as '>'.
    - Keep the 'agent: prediction_modeler' field unchanged.
    - Do NOT modify the analyze_user_task, analyze_item_task, or web_research_task.
    - Do NOT reference tools (prediction_modeler has no tools).
    - Feel free to restructure the reasoning steps, add chain-of-thought instructions,
      change the output format requirements, or tighten/loosen the rules.
    - The output JSON format MUST still be: {"stars": X.X, "review": "..."}
    - Return the COMPLETE YAML file with EVOLVE-BLOCK-START and EVOLVE-BLOCK-END preserved.

    Key insight: The task DESCRIPTION is the actual reasoning prompt the agent receives.
    Better structured reasoning steps → better predictions.
  num_top_programs: 3
  num_diverse_programs: 2
  include_artifacts: false

# --- Database ---
database:
  population_size: 50
  archive_size: 20
  num_islands: 3
  elite_selection_ratio: 0.2
  exploitation_ratio: 0.7
  migration_interval: 10
  migration_rate: 0.1
  feature_dimensions:
    - "complexity"
    - "diversity"

# --- Evaluator ---
evaluator:
  timeout: 900
  max_retries: 2
  parallel_evaluations: 1
  cascade_evaluation: false
```

---

# File: serving_flow.py
Path: `c:\Users\MCC\Rag_Crew_Profiler\openevolve\AgentSocietyChallenge_OpenEvolve\src\flows\serving_flow.py`

```py
import json
import re
from pydantic import BaseModel
from crewai.flow.flow import Flow, listen, start
from src.crews.simulation_crew import SimulationCrew


def extract_json_from_output(raw_output: str) -> dict:
    """Extract and sanitize JSON from LLM raw output with regex fallback."""
    text = str(raw_output).strip()
    
    # Fix double curly braces {{ }} -> { }
    text = text.replace('{{', '{').replace('}}', '}')
    
    # Strategy 1: Try to find a JSON object containing "stars" and "review"
    match = re.search(r'\{[^{}]*"stars"[^{}]*"review"[^{}]*\}', text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group())
        except json.JSONDecodeError:
            pass
    
    # Strategy 2: Try to find a JSON with "predicted_rating" and "generated_review"
    match = re.search(r'\{[^{}]*"predicted_rating"[^{}]*"generated_review"[^{}]*\}', text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group())
        except json.JSONDecodeError:
            pass

    # Strategy 3: Try parsing the entire text as JSON
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    # Strategy 4: Try to extract a star rating number from free text
    star_match = re.search(r'(\d+\.?\d*)\s*(?:stars?|分|顆星)', text, re.IGNORECASE)
    rating = float(star_match.group(1)) if star_match else 4.0

    return {"stars": rating, "review": text}


class InferenceState(BaseModel):
    user_id: str = ""
    item_id: str = ""
    predicted_rating: float = 0.0
    generated_review: str = ""

class AgentSocietyServingFlow(Flow[InferenceState]):
    def __init__(self, agents_config_path: str = None, *args, **kwargs):
        # super().__init__ MUST come first — CrewAI's Flow base class is
        # Pydantic-backed and resets the instance __dict__ during init.
        # Setting custom attributes beforehand causes them to disappear.
        super().__init__(*args, **kwargs)
        self.agents_config_path = agents_config_path

    @start()
    def init_request(self):
        # 初始化階段，紀錄收到的 user_id 和 item_id
        pass

    @listen(init_request)
    def trigger_crew_inference(self):
        # 定義傳遞到任務 {user_id} 與 {item_id} 變數的值
        inputs = {
            'user_id': self.state.user_id,
            'item_id': self.state.item_id
        }
        
        # 啟動並執行 Crew AI 團隊
        crew_instance = SimulationCrew()
        if self.agents_config_path:
            import yaml
            with open(self.agents_config_path, "r", encoding='utf-8') as f:
                new_config = yaml.safe_load(f)
                crew_instance.agents_config.update(new_config)

        result = crew_instance.crew().kickoff(inputs=inputs)
        
        # 使用多層 Regex 容錯解析 LLM 的回傳結果
        try:
            if result.pydantic:
                data = result.pydantic.model_dump()
            else:
                data = extract_json_from_output(result.raw)

            self.state.predicted_rating = float(data.get('stars', data.get('predicted_rating', 4.0)))
            self.state.generated_review = str(data.get('review', data.get('generated_review', 'Good.')))
        except Exception:
            # 最終備援：把整段 raw output 當 review 用
            self.state.predicted_rating = 4.0
            self.state.generated_review = str(result.raw)

        return self.state.model_dump()
```

---

# File: simulation_crew.py
Path: `c:\Users\MCC\Rag_Crew_Profiler\openevolve\AgentSocietyChallenge_OpenEvolve\src\crews\simulation_crew.py`

```py
import os
import requests
from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai.knowledge.knowledge import Knowledge
from crewai.knowledge.source.string_knowledge_source import StringKnowledgeSource
from crewai.tools import tool
from langchain_huggingface import HuggingFaceEmbeddings

# 根據目錄結構加載自訂的工具層
from src.tools.interaction_tool_wrapper import get_interaction_tool

from crewai import LLM

def get_simulation_llm():
    model_name = os.environ.get("NVIDIA_MODEL_NAME", "minimaxai/minimax-m2.7")
    return LLM(
        model=f"openai/{model_name}",
        api_key=os.environ.get("NVIDIA_API_KEY", os.environ.get("OPENAI_API_KEY")),
        base_url=os.environ.get("NVIDIA_API_BASE", os.environ.get("OPENAI_API_BASE")),
        timeout=120
    )

# === Custom Search Tool to avoid crewai_tools dependency issues ===
@tool("serper_search_tool")
def serper_search_tool(query: str) -> str:
    """Search the internet for information using the Serper API."""
    url = "https://google.serper.dev/search"
    payload = {"q": query}
    headers = {
        'X-API-KEY': os.environ.get("SERPER_API_KEY", ""),
        'Content-Type': 'application/json'
    }
    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        results = response.json()
        
        # Format the results into a readable string
        snippets = []
        if "organic" in results:
            for result in results["organic"][:3]: # Get top 3 results
                snippets.append(f"Title: {result.get('title')}\nSnippet: {result.get('snippet')}\n")
        return "\n".join(snippets) if snippets else "No results found."
    except Exception as e:
        return f"Error performing search: {str(e)}"

# === Step 2: Inject Global Background Knowledge ===
def load_knowledge():
    translation_path = os.path.join(os.path.dirname(__file__), '../../docs/Yelp Data Translation.md')
    if os.path.exists(translation_path):
        with open(translation_path, 'r', encoding='utf-8') as f:
            return f.read()
    return ""

from typing import Any

# (Background knowledge tool removed - schema rules are now in agents.yaml backstory)

@CrewBase
class SimulationCrew():
    """Simulation Crew for generating user review simulation"""
    
    agents_config = '../../config/agents.yaml'
    tasks_config = '../../config/tasks.yaml'

    def _get_agent_config(self, key):
        import os, yaml
        env_path = os.environ.get("OPENEVOLVE_AGENTS_YAML")
        if env_path and os.path.exists(env_path):
            with open(env_path, 'r', encoding='utf-8') as f:
                cfg = yaml.safe_load(f)
                if key in cfg:
                    return cfg[key]
        return self.agents_config[key]


    @agent
    def user_analyst(self) -> Agent:
        return Agent(
            config=self._get_agent_config('user_analyst'),
            verbose=True,
            tools=[get_interaction_tool()],
            llm=get_simulation_llm(),
            max_iter=6
        )

    @agent
    def item_analyst(self) -> Agent:
        return Agent(
            config=self._get_agent_config('item_analyst'),
            verbose=True,
            tools=[get_interaction_tool()],
            llm=get_simulation_llm(),
            max_iter=6
        )

    @agent
    def web_researcher(self) -> Agent:
        return Agent(
            config=self._get_agent_config('web_researcher'),
            tools=[serper_search_tool],
            verbose=True,
            llm=get_simulation_llm(),
            max_iter=3
        )

    @agent
    def persona_classifier(self) -> Agent:
        return Agent(
            config=self._get_agent_config('persona_classifier'),
            tools=[],
            verbose=True,
            llm=get_simulation_llm(),
            max_iter=4
        )

    @agent
    def prediction_modeler(self) -> Agent:
        return Agent(
            config=self._get_agent_config('prediction_modeler'),
            tools=[],
            verbose=True,
            llm=get_simulation_llm(),
            max_iter=6
        )

    @task
    def analyze_user_task(self) -> Task:
        return Task(
            config=self.tasks_config['analyze_user_task']
        )

    @task
    def analyze_item_task(self) -> Task:
        return Task(
            config=self.tasks_config['analyze_item_task']
        )

    @task
    def web_research_task(self) -> Task:
        return Task(
            config=self.tasks_config['web_research_task'],
            context=[self.analyze_item_task()]
        )

    @task
    def classify_persona_task(self) -> Task:
        return Task(
            config=self.tasks_config['classify_persona_task'],
            context=[self.analyze_user_task(), self.analyze_item_task(), self.web_research_task()]
        )

    @task
    def predict_review_task(self) -> Task:
        return Task(
            config=self.tasks_config['predict_review_task'],
            context=[self.classify_persona_task(), self.analyze_user_task(), self.analyze_item_task()]
        )

    @crew
    def crew(self) -> Crew:
        return Crew(
            agents=[
                self.user_analyst(), 
                self.item_analyst(), 
                self.web_researcher(), 
                self.persona_classifier(),
                self.prediction_modeler()
            ],
            tasks=[
                self.analyze_user_task(), 
                self.analyze_item_task(), 
                self.web_research_task(), 
                self.classify_persona_task(),
                self.predict_review_task()
            ],
            process=Process.sequential,
            # knowledge=Knowledge(
            #     collection_name="simulator_knowledge_v1",
            #     sources=load_knowledge(),
            #     embedder={
            #         "provider": "huggingface",
            #         "config": {"model": "BAAI/bge-small-en-v1.5"}
            #     }
            # ),
            # embedder={
            #     "provider": "huggingface",
            #     "config": {"model": "BAAI/bge-small-en-v1.5"}
            # },
            max_rpm=5, # Increased to 5 to avoid the 300s simulator timeout while still being safe
            verbose=True
        )
```

---

# File: interaction_tool_wrapper.py
Path: `c:\Users\MCC\Rag_Crew_Profiler\openevolve\AgentSocietyChallenge_OpenEvolve\src\tools\interaction_tool_wrapper.py`

```py
from crewai.tools import tool
import json

# 單例全域變數：負責盛裝執行期 Simulator.py 動態配給的 interaction_tool
_GLOBAL_INTERACTION_TOOL = None

def inject_simulator_tool(tool_instance):
    global _GLOBAL_INTERACTION_TOOL
    _GLOBAL_INTERACTION_TOOL = tool_instance

@tool("Interaction Tool Wrapper")
def interaction_tool_wrapper(query_type: str, target_id: str) -> str:
    """
    能調用 AgentSociety 提供的本地檢索工具查詢歷史數據。
    query_type 必須是下列之一："user", "item", "review_by_user", "review_by_item"。
    target_id 是對應的 user_id 或 item_id。
    """
    if _GLOBAL_INTERACTION_TOOL is None:
        return "Error: InteractionTool has not been injected by the Simulator."
        
    try:
        if query_type == "user":
            res = _GLOBAL_INTERACTION_TOOL.get_user(user_id=target_id)
            if isinstance(res, dict):
                res.pop("friends", None) # Massive field, useless for prediction
        elif query_type == "item":
            res = _GLOBAL_INTERACTION_TOOL.get_item(item_id=target_id)
        elif query_type in ["review_by_user", "review_by_item"]:
            # Handle large review sets safely
            raw_res = _GLOBAL_INTERACTION_TOOL.get_reviews(
                user_id=target_id if query_type == "review_by_user" else None,
                item_id=target_id if query_type == "review_by_item" else None
            )
            
            if not raw_res:
                return f"No reviews found for {query_type} with ID '{target_id}'."
                
            # Limit to top 15 reviews to prevent 504 Timeout
            limited_res = raw_res[:15]
            
            # Truncate review text for each entry
            for r in limited_res:
                if 'text' in r and len(r['text']) > 500:
                    r['text'] = r['text'][:500] + "... [TRUNCATED]"
            
            res = limited_res
        else:
            return "Error: Unknown query_type. Use exactly 'user', 'item', 'review_by_user' or 'review_by_item'."
            
        if not res:
            return f"CRITICAL: No data found for this {query_type} with ID '{target_id}'. This ID is NOT in the database. DO NOT try to query this ID again. Proceed immediately using the information you already have (or treat as an unknown entity)."
            
        # Return as pretty-printed JSON for better LLM readability
        return json.dumps(res, indent=2, ensure_ascii=False)
    except Exception as e:
        return f"Error occurred during interaction_tool query: {str(e)}"

def get_interaction_tool():
    """回傳工具實例供 Crew Agent 使用"""
    return interaction_tool_wrapper
```

---

# File: simulator.py
Path: `c:\Users\MCC\Rag_Crew_Profiler\openevolve\AgentSocietyChallenge_OpenEvolve\websocietysimulator\simulator.py`

```py
import logging
import os
import json
from typing import List, Type, Dict, Any, Union
from .tools import InteractionTool, CacheInteractionTool
from .tools.evaluation_tool import RecommendationEvaluator, SimulationEvaluator
from .agent.simulation_agent import SimulationAgent
from .llm import LLMBase
from .agent.recommendation_agent import RecommendationAgent
from .tasks.simulation_task import SimulationTask
from .tasks.recommendation_task import RecommendationTask

logger = logging.getLogger("websocietysimulator")

class Simulator:
    def __init__(self, data_dir: str = None, device: str = "auto", cache: bool = False):
        """
        Initialize the Simulator.
        Args:
            data_dir: Path to the directory containing Yelp dataset files.
            device: Device to use for evaluation. "auto" (default) will use GPU if available, otherwise CPU. Available options: "gpu", "cpu", "auto".
            cache: Whether to use cache for interaction tool.
        """
        logger.info("Start initializing Simulator")
        self.data_dir = data_dir
        if data_dir is None:
            self.interaction_tool = None
        else:
            if cache:
                logger.info("Using CacheInteractionTool")
                self.interaction_tool = CacheInteractionTool(data_dir)
            else:
                logger.info("Using Normal InteractionTool")
                self.interaction_tool = InteractionTool(data_dir)
        
        self.tasks = []  # List to store tasks
        self.groundtruth_data = []  # List to store groundtruth data
        self.agent_class = None
        self.llm = None
        self.recommendation_evaluator = RecommendationEvaluator()
        self.simulation_evaluator = SimulationEvaluator(device)
        self.simulation_outputs = []
        self.evaluation_results = []
        logger.info("Simulator initialized")

    def set_interaction_tool(self, interaction_tool: Union[InteractionTool, CacheInteractionTool]):
        self.interaction_tool = interaction_tool

    def set_task_and_groundtruth(self, task_dir: str, groundtruth_dir: str):
        """
        Load tasks from a directory.
        Args:
            task_dir: Directory containing task files.
            groundtruth_dir: Directory containing groundtruth files.
        """
        self.tasks = []  # Clear previous tasks
        self.groundtruth_data = []

        # 获取所有task文件并按index排序
        task_files = sorted([f for f in os.listdir(task_dir) if f.startswith('task_') and f.endswith('.json')], 
                          key=lambda x: int(x.split('_')[1].split('.')[0]))

        for task_file in task_files:
            # 获取对应的groundtruth文件
            task_index = task_file.split('_')[1].split('.')[0]
            groundtruth_file = f'groundtruth_{task_index}.json'
            groundtruth_path = os.path.join(groundtruth_dir, groundtruth_file)
            
            if not os.path.exists(groundtruth_path):
                logger.warning(f"Groundtruth file {groundtruth_file} not found for task {task_file}")
                continue

            # 读取task文件
            task_path = os.path.join(task_dir, task_file)
            with open(task_path, 'r') as f:
                task_data = json.load(f)
                task_type = task_data.get('type')

                # Determine scenario type and create corresponding object
                if task_type == 'user_behavior_simulation':
                    task = SimulationTask(
                        user_id=task_data['user_id'],
                        item_id=task_data['item_id']
                    )
                elif task_type == 'recommendation':
                    task = RecommendationTask(
                        user_id=task_data['user_id'],
                        candidate_category=task_data['candidate_category'],
                        candidate_list=task_data['candidate_list'],
                        loc=task_data['loc']
                    )
                else:
                    raise ValueError(f"Unsupported task type: {task_type}")

            with open(groundtruth_path, 'r') as f:
                groundtruth_data = json.load(f)
                
            self.tasks.append(task)
            self.groundtruth_data.append(groundtruth_data)

        logger.info(f"Loaded {len(self.tasks)} task-groundtruth pairs")

    def set_agent(self, agent_class: Type):
        """
        Set the agent class to be used for the simulation.
        Args:
            agent_class: A class inheriting from the abstract Agent class.
        """
        if not issubclass(agent_class, (SimulationAgent, RecommendationAgent)):
            raise ValueError("Agent class must inherit from SimulationAgent or RecommendationAgent.")
        self.agent_class = agent_class
        logger.info("Agent class set")

    def set_llm(self, llm: Union[LLMBase, list[LLMBase]]):
        """
        Set the LLM to be used for the simulation.
        Args:
            llm: A class inheriting from the abstract LLM class.
        """
        self.llm = llm
        logger.info("LLM set")

    def run_simulation(self, number_of_tasks: int = None, enable_threading: bool = False, max_workers: int = None, time_limitation: float = None) -> List[Any]:
        """
        Run the simulation with optional multi-threading support and time limitation.
        
        Args:
            number_of_tasks: Number of tasks to run. If None, run all tasks.
            enable_threading: Whether to enable multi-threading. Default is False.
            max_workers: Maximum number of threads to use. If None, will use min(32, number_of_tasks).
            time_limitation: Time limit in minutes. If None, no time limit is applied.
        Returns:
            List of outputs from agents for each scenario.
        """
        import time
        from concurrent.futures import ThreadPoolExecutor, as_completed, TimeoutError

        start_time = time.time()
        timeout_seconds = time_limitation * 60 if time_limitation else None

        logger.info("Running simulation")
        if not self.agent_class:
            raise RuntimeError("Agent class is not set. Use set_agent() to set it.")
        if not self.interaction_tool:
            raise RuntimeError("Interaction tool is not set. Use set_interaction_tool() to set it.")

        task_to_run = self.tasks[:number_of_tasks] if number_of_tasks is not None else self.tasks
        logger.info(f"Total tasks: {len(task_to_run)}")

        # 如果不启用多线程，使用原始的串行处理
        if not enable_threading:
            self.simulation_outputs = []
            for index, task in enumerate(task_to_run):
                # 检查是否超时
                if timeout_seconds and (time.time() - start_time) > timeout_seconds:
                    logger.warning(f"Time limit ({time_limitation} minutes) reached. Stopping simulation.")
                    break

                if isinstance(self.llm, list):
                    agent = self.agent_class(llm=self.llm[index%len(self.llm)])
                else:
                    agent = self.agent_class(llm=self.llm)
                agent.set_interaction_tool(self.interaction_tool)
                agent.insert_task(task)
                
                try:
                    output = agent.workflow()
                    result = {
                        "task": task.to_dict(),
                        "output": output
                    }
                except NotImplementedError:
                    result = {
                        "task": task.to_dict(),
                        "error": "Forward method not implemented by participant."
                    }
                self.simulation_outputs.append(result)
                logger.info(f"Simulation finished for task {index}")
        else:
            # 多线程处理
            from threading import Lock, Event
            
            log_lock = Lock()
            cancel_event = Event()  # 添加取消事件标志
            self.simulation_outputs = [None] * len(task_to_run)

            def process_task(task_index_tuple):
                from concurrent.futures import ThreadPoolExecutor, TimeoutError
                
                def run_agent_task(agent, task):
                    output = agent.workflow()
                    return output
                
                index, task = task_index_tuple
                # 检查是否已经被要求取消
                if cancel_event.is_set():
                    return index, None
                    
                if isinstance(self.llm, list):
                    agent = self.agent_class(llm=self.llm[index%len(self.llm)])
                else:
                    agent = self.agent_class(llm=self.llm)
                agent.set_interaction_tool(self.interaction_tool)
                agent.insert_task(task)
                
                try:
                    # 使用内部的ThreadPoolExecutor来执行单个任务，设置超时时间为5分钟
                    with ThreadPoolExecutor(max_workers=1) as single_task_executor:
                        future = single_task_executor.submit(run_agent_task, agent, task)
                        try:
                            output = future.result(timeout=800)  # Increased timeout to allow for rate limits and longer task sequences
                            result = {
                                "task": task.to_dict(),
                                "output": output
                            }
                        except TimeoutError:
                            logger.warning(f"Task {index} timed out")
                            # 强制关闭执行器
                            single_task_executor._threads.clear()
                            single_task_executor.shutdown(wait=False)
                            return index, None
                except NotImplementedError:
                    result = {
                        "task": task.to_dict(),
                        "error": "Forward method not implemented by participant."
                    }
                except Exception as e:
                    logger.error(f"Task {index} failed with error: {str(e)}")
                    return index, None
                
                with log_lock:
                    logger.info(f"Simulation finished for task {index}")
                
                return index, result

            # 确定线程数
            if max_workers is None:
                max_workers = min(32, len(task_to_run))
            else:
                max_workers = min(max_workers, len(task_to_run))
            
            logger.info(f"Running with {max_workers} threads")
            
            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                future_to_index = {
                    executor.submit(process_task, (i, task)): i 
                    for i, task in enumerate(task_to_run)
                }

                try:
                    for future in as_completed(future_to_index, timeout=timeout_seconds):
                        try:
                            index, result = future.result()
                            self.simulation_outputs[index] = result
                        except Exception as e:
                            logger.error(f"Task failed with error: {str(e)}")
                except TimeoutError:
                    logger.error(f"Time limit ({time_limitation} minutes) reached.")
                    # 设置取消标志
                    cancel_event.set()
                    # 强制取消所有任务
                    for future in future_to_index:
                        future.cancel()
                    # 立即关闭执行器，不等待任务完成
                    executor._threads.clear()
                    executor.shutdown(wait=False)
                    raise TimeoutError

        logger.info("Simulation finished")
        # 过滤掉None值（未完成的任务）
        return self.simulation_outputs

    def evaluate(self) -> Dict[str, Any]:
        """
        Evaluate the simulation results using the loaded groundtruth data.
        Returns:
            Dictionary containing evaluation metrics
        """
        logger.info("Evaluating simulation results")
        if not self.simulation_outputs:
            raise RuntimeError("No simulation outputs to evaluate. Run simulation first.")
        
        # 检查数据条目数量
        sim_count = len(self.simulation_outputs)
        gt_count = len(self.groundtruth_data)
        
        if sim_count != gt_count:
            logger.warning(f"Warning: Number of simulation outputs ({sim_count}) does not match ground truth data ({gt_count})")
            # 使用较小的数量
            eval_count = min(sim_count, gt_count)
            groundtruth_data = self.groundtruth_data[:eval_count]
            self.simulation_outputs = self.simulation_outputs[:eval_count]
        else:
            groundtruth_data = self.groundtruth_data
        
        evaluation_results = {}
        
        # 根据agent类型选择评估方法
        if issubclass(self.agent_class, RecommendationAgent):
            evaluation_results = self._evaluate_recommendation(groundtruth_data)
        elif issubclass(self.agent_class, SimulationAgent):
            evaluation_results = self._evaluate_simulation(groundtruth_data)
        
        # 添加数据条目信息到评估结果中
        evaluation_results['data_info'] = {
            'evaluated_count': eval_count if sim_count != gt_count else sim_count,
            'original_simulation_count': sim_count,
            'original_ground_truth_count': gt_count
        }
        
        self.evaluation_results.append(evaluation_results)
        logger.info("Evaluation finished")
        return evaluation_results

    def _evaluate_recommendation(self, ground_truth_data: List[Dict]) -> Dict[str, Any]:
        """
        Evaluate recommendation results using groundtruth
        """
        # 从ground truth数据中提取真实POI
        gt_pois = [item['ground truth'] for item in ground_truth_data]
        
        pred_pois = []
        for output in self.simulation_outputs:
            if output is not None:
                pred_pois.append(output['output'])
            else:
                pred_pois.append([''])

        # 计算评估指标
        metrics = self.recommendation_evaluator.calculate_hr_at_n(
            ground_truth=gt_pois,
            predictions=pred_pois,
        )

        return {
            'type': 'recommendation',
            'metrics': metrics.__dict__,
        }

    def _evaluate_simulation(self, ground_truth_data: List[Dict]) -> Dict[str, Any]:
        """
        Evaluate simulation results
        """
        simulated_data = []
        for output in self.simulation_outputs:
            if output is not None:
                simulated_data.append(output['output'])
            else:
                simulated_data.append({
                    'stars': 0,
                    'review': ''
                })
        metrics = self.simulation_evaluator.calculate_metrics(
            simulated_data=simulated_data,
            real_data=ground_truth_data
        )
        return {
            'type': 'simulation',
            'metrics': metrics.__dict__,
        }

    def get_evaluation_history(self) -> List[Dict[str, Any]]:
        """
        Get the history of evaluation results
        Returns:
            List of evaluation results
        """
        return self.evaluation_results
```

---

# File: openevolve_evaluator.py
Path: `c:\Users\MCC\Rag_Crew_Profiler\openevolve\AgentSocietyChallenge_OpenEvolve\openevolve_evaluator.py`

```py
import os
import tempfile
import sys
import logging
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FuturesTimeout

project_dir = os.path.dirname(os.path.abspath(__file__))
if project_dir not in sys.path:
    sys.path.append(project_dir)

from websocietysimulator import Simulator
from crewai_simulation_agent import CrewAISimulationAgent

# 整個 simulation 的 hard timeout（秒）。超時則回傳 fallback fitness 讓 OpenEvolve 繼續。
# 預設 15 分鐘，可由 OPENEVOLVE_SIM_TIMEOUT env var 覆寫。
SIM_TIMEOUT_SEC = int(os.environ.get("OPENEVOLVE_SIM_TIMEOUT", 900))

# ---------------------------------------------------------------------------
# Lazy singleton: Simulator is expensive to initialize (loads LMDB dataset).
# OpenEvolve imports this module once and calls evaluate() many times, so we
# initialize on the first call and reuse the same instance afterward.
# ---------------------------------------------------------------------------
_simulator: Simulator = None

def _get_simulator() -> Simulator:
    global _simulator
    if _simulator is None:
        logging.getLogger().setLevel(logging.WARNING)
        print("[Evaluator] Initializing Simulator with sampled dataset (one-time)...")
        _simulator = Simulator(data_dir="dummy_dataset", device="cpu", cache=True)
        _simulator.set_task_and_groundtruth(
            task_dir="dummy_tasks",
            groundtruth_dir="dummy_groundtruth"
        )
        _simulator.set_agent(CrewAISimulationAgent)
        print("[Evaluator] Simulator ready.")
    return _simulator


def evaluate(program_path: str) -> dict:
    """
    Module-level function required by OpenEvolve.

    OpenEvolve writes the mutated YAML to a temp file (suffix configured as
    .yaml) and passes the FILE PATH here as the sole argument.

    Returns a dict with 'combined_score' as the primary fitness metric (required
    by OpenEvolve), plus individual sub-metrics for MAP-Elites feature tracking.

    combined_score = overall_quality (0–1):
      overall_quality = (preference_estimation + review_generation) / 2
    where preference_estimation = 1 - normalized_star_MAE.
    """
    simulator = _get_simulator()
    try:
        # 1. Tell CrewAISimulationAgent to load this YAML config for the run
        os.environ["OPENEVOLVE_AGENTS_YAML"] = program_path

        num_tasks = int(os.environ.get("OPENEVOLVE_NUM_TASKS", 5))
        print(f"\n[Evaluator] Running simulation: {program_path}  (tasks={num_tasks}, timeout={SIM_TIMEOUT_SEC}s)")
        try:
            import yaml
            with open(program_path, 'r', encoding='utf-8') as tmp_f:
                d = yaml.safe_load(tmp_f)
                print(f"[Evaluator Debug] Keys in {program_path}:", list(d.keys()) if isinstance(d, dict) else "Not a dict")
        except Exception as e:
            print(f"[Evaluator Debug] Failed to read/parse {program_path}:", e)

        # Hard timeout 包住整個 simulation。如果 simulator/CrewAI/LiteLLM 內部卡住
        # （例如 rate limit retry 死循環），這層會在 SIM_TIMEOUT_SEC 後強制中止，
        # 讓 evaluator 回傳 fallback 分數讓 OpenEvolve 能繼續下一個 iteration。
        try:
            with ThreadPoolExecutor(max_workers=1) as executor:
                future = executor.submit(
                    simulator.run_simulation,
                    number_of_tasks=num_tasks,
                    enable_threading=True,
                    max_workers=2,
                )
                future.result(timeout=SIM_TIMEOUT_SEC)
        except FuturesTimeout:
            print(f"[Evaluator] ⏱  Simulation exceeded {SIM_TIMEOUT_SEC}s — returning fallback score")
            return {"combined_score": 0.0}

        # 2. Compute official metrics
        # eval_results structure:
        #   {"type": "simulation", "metrics": <SimulationMetrics.__dict__>, "data_info": {...}}
        print("[Evaluator] Calculating official metrics...")
        eval_results = simulator.evaluate()

        metrics           = eval_results.get("metrics", {}) if isinstance(eval_results, dict) else {}
        overall_quality   = metrics.get("overall_quality", 0.0)
        pref_estimation   = metrics.get("preference_estimation", 0.0)
        review_generation = metrics.get("review_generation", 0.0)

        print(
            f"[Evaluator] preference_estimation={pref_estimation:.4f}, "
            f"review_generation={review_generation:.4f}, "
            f"overall_quality={overall_quality:.4f}  →  combined_score={overall_quality:.4f}"
        )

        return {"combined_score": float(overall_quality)}

    except Exception as e:
        print(f"[Evaluator] ❌ Error during evaluation: {e}")
        import traceback
        traceback.print_exc()
        return {"combined_score": 0.0}


if __name__ == "__main__":
    # Lightweight integration test — write initial YAML to a temp file,
    # then call evaluate() exactly as OpenEvolve would.
    import tempfile
    yaml_path = os.path.join(project_dir, "config", "agents_evolving.yaml")
    if os.path.exists(yaml_path):
        with open(yaml_path, "r", encoding="utf-8") as f:
            content = f.read()
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False, encoding='utf-8') as tmp:
            tmp.write(content)
            tmp_path = tmp.name
        try:
            fitness = evaluate(tmp_path)
            print(f"Test execution completed with evaluated fitness score: {fitness}")
        finally:
            os.remove(tmp_path)
```

---

# File: LAB 14 DONE - OPENEVOLVE
Path: `c:\Users\MCC\Rag_Crew_Profiler\openevolve\LAB 14 DONE - OPENEVOLVE`

```text
# LLM & APP (w14 2026 Spring)

**Tuesday 10:10-13:00, E307 Engineering II**

**Instructor: Yu-Chieh Jack Ho**

**Office:** A302, Engineering II  | **Office hours:** Weds 10:30-12:30 | **Email:** yc.ho@gms.ndhu.edu.tw

# Recap:

### **Dynamic** Meta prompting

- During code e**volution**, OpenEvolve d**ynamically** apply meta prompting in every iterations (generations)

![image.png](attachment:38d2e37f-7a9e-4870-90fe-84869f84e05a:image.png)

### Lab: General Function M**inimization**

A  Function M**inimizer** which accept any user defined target function 

![image.png](attachment:afbf1ba3-8809-46a2-8afb-69886c075a26:image.png)

- Tip: Utilize a dynamic baseline (relative competition within the population) in evaluator.
    - Evaluator is the key to boost evaluation

```python
# The current historical best value of the population (passed in by the OpenEvolve system or stored in a file)
CURRENT_BEST = {"value": None}

def evaluate(program_path):
    x, y, value = run_with_timeout(program.run_search, timeout_seconds=5)
    
    # First run: no baseline exists, so accept it directly
    if CURRENT_BEST["value"] is None:
        CURRENT_BEST["value"] = value
        return EvaluationResult(metrics={"combined_score": 0.5})
    
    # Compared with the historical best; the "margin of improvement" determines the score
    improvement = CURRENT_BEST["value"] - value  # Positive value = improved
    score = 0.5 + np.tanh(improvement * 5)       # Squashed into a 0 to 1 range

    # If the historical best is broken, update the baseline
    if value < CURRENT_BEST["value"]:
        CURRENT_BEST["value"] = value
    
    return EvaluationResult(metrics={"combined_score": score})

```

### OpenEvolve’s Evolutionary Algorithm

A Combination of the **Island-based Evolution model**  and the **MAP-Elites algorithm**

- **“Islands”:** A mechanism that isolate “DNAs” and force them to evolve independently
    - In the `ProgramDatabase` class within `openevolve/database.py`, the system creates multiple independent "islands" based on the configuration file (`config.num_islands`).
        
        ```python
        # The population of each island (a Set storing Program IDs)
        self.islands: List[Set[str]] = [set() for _ in range(config.num_islands)]
        ```
        
    
    ![image.png](attachment:ce8bc88b-852e-4e8d-a0d7-8d970b9c8e1a:image.png)
    
- **MAP-Elites:** A ****structure and approach to efficiently maintain the diversity of “population” on each island by **Keep  “weird codes”, e.g., overly complex, or extremely simple for more inspiration.**
    
    ```python
    # Each island has its own independent MAP-Elites feature map
    self.island_feature_maps: List[Dict[str, str]] = [{} for _ in range(config.num_islands)]
    ```
    
    - E**ach island maintains its own independent MAP-Elites feature map**. This means that the exact same feature dimention can be occupied by entirely different code variants across different islands

# Agenda:

- Recap
- Seminar
- Lecture
    - FunSearch - ****Problem Formulation of AlphaEvolve
    - Primary Breakthrough: Heuristic Algorithm Discovery
    - Leverage AlphaEvolve to Solve a Meaningful and Complex Problem
        - What’s a Meaningful Problem and Why AgentSociety Challenge
- Lab: Integration or New Problem Formulation

# FunSearch - ****Problem Formulation of AlphaEvolve

**FunSearch** ("searching in the function space"): Discover computer programs that solve complex mathematical and algorithmic problems by searching over a space of program fragments, usually computer [functions](https://en.wikipedia.org/wiki/Function_(computer_programming)) embedded in a fixed program skeleton (e.g., Evolve Block.)

Its core mechanism combines: 

- A **Large Language Model (LLM)**,
- An **automated evaluator**,
- An **evolutionary search procedure (algorithm)**.

### **1. Definition**

- $\mathcal{F} =\{f_0,...,f_n\}$： Space of all candidate functions.
    - $f_0$ : the initial function
- $S: \mathcal{F} \to \mathbb{R}$：  Evaluator function that measure a candidate functions by mapping them to real numbers.
    - e.g., $S(f_{0})=0.345$
- $D$ ：Program database that store valid functions and their evaluation score.
    - $D =\{(f_{0}, S(f_{0})),...,(f_{m}, S(f_{m}))\}$

### 2. Objective Function

- $f^{*} = \operatorname{arg\,max}_{f \in \mathcal{F}} S(f)$
    - Find the optimal candidate function $f^{*}$ *in the function space that maximizes the evaluator score:*

### 3. Pseudocode

**Input:**
• $f_0$ : Initial function (e.g., `initial_program.py`)
• $S: \mathcal{F} \to \mathbb{R}$: Evaluator function (`evaluator.py`)
• $\operatorname{LLM}$ : Pre-trained Large Language Model. (set up in `config.yaml`)
• $\text{max\_iter}$ : Maximum number of iterations. (set up in `config.yaml`) 
**Output:**
• $f_{\text{best}}$ : The candidate function with the highest evaluator score. (in `./openevolve_output`)

**1. Initialization** (`openevolve/database.py`)
• Initialize the database: $D \leftarrow \{(f_0, S(f_0))\}$
• Track the best function: $f_{\text{best}} \leftarrow f_0$
- Track the maximum score: $\text{max\_score}\leftarrow S(f_0)$

**2. Evolutionary Search Loop** (`openevolve/prompt/sampler.py` & `openevolve/database.py`)
• **For**  $\text{iter} = 1$  **to**  $\text{max\_iter}$ **do:**
    ◦ **Step A: Sample Functions 
          Sample diverse, high-scoring functions from $D$**
        ▪ e.g., $F_{\text{sample}} \leftarrow \operatorname{Sample}(D, k, \text{bias}=\text{"high\_score"})$

              Let $F_{\text{sample}}$ = $\{f_1,f_2,\ldots,f_k\}$.
       **Step B: Construct Prompt**   
        ◦ $\text{prompt} \leftarrow \operatorname{ConstructPrompt}(F_{\text{sample}})$
    ◦ **Step C: Generate New Candidate**
        ▪ $f' \sim \operatorname{LLM.Generate}(\text{prompt})$
    ◦ **Step D: Evaluate and Validate**
        ▪ **If** $\operatorname{IsValid}(f')$ **Then**
            • Calculate the score: $\text{score}' \leftarrow S(f')$
    • **Step E: Update Database**
             $D \leftarrow D \cup \{(f', \text{score}')\}$
    • **Step F: Track Best Result**

          **If** $\text{score}' > \text{max\_score}$ **Then**
                ◦ $f_{\text{best}} \leftarrow f'$
                ◦ $\text{max\_score} \leftarrow \text{score}'$
• **End For**
**3. Return Result**
• **Return** $f_{\text{best}}$

### Note:

The previously mentioned island-based model and MAP-Elites algorithm are applied during **Initialization, Function Sampling,** and **Prompt Construction.**  

- **Reference week 13 hangouts and following** DataFlow **for details**

### OpenEvolve DataFlow

# Primary Breakthrough: Heuristic Algorithm Discovery

## What is a Heuristic in AI?

A **heuristic** is a practical shortcut or "rule of thumb" used when facing a very complex problem, for which finding a perfect solution is computationally impossible. It trades absolute perfection for speed, guiding the AI toward a **"good enough"** solution.

## **Example: The Challenge of TSP**

The **Traveling Salesperson Problem (TSP)** is a classic **NP-Hard** problem where an agent must find the shortest route visiting $N$ cities exactly once.

- Because possible routes scale factorially—calculated as $\frac{(N-1)!}{2}$—it triggers a **combinatorial explosion**.  For 100 cities, the possibilities outnumber the atoms in the universe, making heuristics absolutely mandatory for practical logistics.
- *Nearest Neighbor* approach
    
    ![Nearestneighbor.gif](attachment:db85cab2-da4f-4308-b02f-3dea2f1aa9b9:Nearestneighbor.gif)
    
- One of the best heuristics: https://en.wikipedia.org/wiki/Lin%E2%80%93Kernighan_heuristic

#### Real-World Applications

Any industry problem involving the **"optimal sequencing of limited resources"** can be modeled as a variant of the TSP, e.g.:

- **Logistics & Warehousing:** Routing delivery vehicles or automated warehouse-picking robots to minimize travel time.
    
    ![image.png](attachment:8921b9ee-407b-45d7-987e-493784e3e2cf:image.png)
    
- **Microchip Manufacturing:** Optimizing the path of a robotic drill punching thousands of microscopic holes in circuit boards to save production time.
- **Astronomy:** Minimizing the mechanical movement time of telescopes when scheduling observations of multiple celestial bodies to reduce operation time, as well as ordinary wear and tear.

## How FunSearch Discovers Superior Heuristics

- **Bypasses Human Cognitive Bias:** By running millions of automatic iterations, it discovers unorthodox strategies that human would never think to try.
- **Human-Readable Output:** FunSearch outputs actual **codes**. Humans can read, understand, and learn the underlying mathematical logic.
- Best Practice:
    - Start with Human Intelligence, evolve with Artificial Intelligence, complete with human understanding.

![image.png](attachment:e40fc65a-eb6f-4d71-9c61-ca4097142d13:image.png)

# Leverage AlphaEvolve to Solve a Meaningful Complex Problem

## AgentSociety Challenge

- The core concept of **Agent-Based Simulation — simulating human behavior through LLM agent**s—requiring memory, reasoning, environment perception, and tool use—is driving several high-value AI frameworks:

#### 1. Social & Population Dynamics

- **Example:** Stanford's *Generative Agents (Smallville)*, where virtual agents with unique personas live, socialize, and share information in a sandbox town.
- **Value:** It captures **emergent behaviors**. This helps researchers simulate real-world phenomena like how infectious diseases spread, how misinformation propagates on social networks, or how crowds move during urban planning.

#### 2. Economic & Market Simulation

- **Example:** Macroeconomic sandboxes where individual AI agents play the roles of consumers (with varying budgets and risk appetites) and businesses.
- **Value:** It acts as a **risk-free policy testbed**. Governments and enterprises can simulate how a market will react to a new tax policy, stimulus package, or algorithmic pricing model before launching it in reality.

#### 3. Web Navigation & Digital Action

- **Example:** *WebArena* and *Mind2Web*, where agents are tasked with browsing real-world web environments to complete tasks like booking flights or buying specific products.
- **Value:** It tests an agent's **multi-step reasoning and error recovery** (e.g., knowing to hit "back" if a page fails). This forms the foundation for next-generation digital assistants and advanced workflow automation (RPA 2.0).

### Summary

**Agent-Based Simulation** provides **low-cost, zero-risk sandboxes** for complex real-world scenarios. 

### Current Progress

Now we have

- Baseline Agent Crew
- Historical Review data
- Clear Evaluation Metrics

### Next: Integrate and Evolve

- Sample Code:
    - https://github.com/yuchieh/AgentSocietyChallenge_OpenEvolve
- Agent Design improved within 10 iterations.:

### Final Project Focus

- Novelty
    - What can be evolve besides agent design?
    - What’s the best way to evolve them?
- Analysis
    - How do you parse the evolution path
    - How do you explain the results
- Accuracy
    - The final evaluation result (combined score)

## An alternative for the final project: Propose your problem

- Discuss with me about its importance and challenge
- Describe your problem clearly (e.g., the initial function)
- Describe how would you evaluate it clearly (e.g., the evaluation function)

# Lab: Bringing Your Agent Crew into the OpenEvolve Framework or Propose your Problem Formulation

Follow the guide to integrate your baseline crew with the OpenEvolve framework and complete a smoke test (Step 3)

OR

Formulate your problem and discuss with me

# Integration Guide

> This guide walks you through migrating the Multi-Agent CrewAI system you designed in
**`AgentSocietyChallenge_w_CrewAI`** (the teaching parent repo) into
**`AgentSocietyChallenge_OpenEvolve`** (the version integrated with OpenEvolve), and
then launching an LLM-driven evolutionary optimization of your agent prompts.
> 

---

## 0. The Role of Each Repo

| Repo | Role | What You Do |
| --- | --- | --- |
| [`AgentSocietyChallenge_w_CrewAI`](https://github.com/yuchieh/AgentSocietyChallenge_w_CrewAI) | **Design sandbox** | Design, iterate, and test your Multi-Agent Crew |
| [`AgentSocietyChallenge_OpenEvolve`](https://github.com/yuchieh/AgentSocietyChallenge_OpenEvolve) | **Evolution framework** | Move your validated Crew here and let an LLM auto-evolve the best prompts |

The two repos share **the exact same underlying code** (same `websocietysimulator/` competition framework, same CrewAI integration layer). The only difference is that the evolution version wraps everything with an OpenEvolve evaluator.

## 1. The Three-Layer Architecture

```
┌─────────────────────────────────────────────────────────────┐
│ OpenEvolve (outer layer — exists only in the evolution repo)│
│   - LLM mutates the contents of agents.yaml                 │
│   - Runs evaluator → collects fitness → decides next mutation│
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼ passes mutated YAML downward
┌─────────────────────────────────────────────────────────────┐
│ Your CrewAI System (middle layer — present in both repos)   │
│   - config/agents.yaml      ← your Agent role definitions   │
│   - config/tasks.yaml       ← your Task instructions        │
│   - src/crews/...           ← your Crew assembly logic      │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼ queries data, returns prediction
┌─────────────────────────────────────────────────────────────┐
│ Competition Simulator (bottom — present in both, immutable) │
│   - websocietysimulator/                                    │
│   - InteractionTool: get_user / get_item / get_reviews      │
│   - SimulationEvaluator: computes stars MAE + review sim    │
└─────────────────────────────────────────────────────────────┘
```

Anything that runs in the parent repo will run in the evolution version too. The only addition is "a layer that can evolve your prompts on top".

---

## 2. File Correspondence Between the Two Repos (Most Important!)

Parent Repo (design)	Evolution Repo (execution)	Action
config/agents.yaml	config/agents.yaml	✅ Copy in full
config/tasks.yaml	config/tasks.yaml	✅ Copy in full
src/crews/simulation_crew.py	src/crews/simulation_crew.py	✅ Copy in full
src/tools/interaction_tool_wrapper.py	src/tools/interaction_tool_wrapper.py	⛔ Usually untouched
src/flows/serving_flow.py	src/flows/serving_flow.py	⛔ Do NOT modify (OpenEvolve already added the agents_config_path mechanism)
crewai_simulation_agent.py	crewai_simulation_agent.py	⛔ Do NOT modify (same reason as above)
run_pipeline.py / run_test.py	run_test.py	⛔ Use the existing one
❌ Does not exist	config/agents_evolving.yaml	🆕 Create new (from agents.yaml + EVOLVE-BLOCK markers)
❌ Does not exist	config/openevolve_config.yaml	⛔ Defaults are usually fine
❌ Does not exist	openevolve_evaluator.py	⛔ Do not touch

Note: Some merges may be necessary if you customized the files in the Parent Repo, e.g,: 

- `src/flows/serving_flow.pysrc/flows/serving_flow.py`
- `crewai_simulation_agent.pycrewai_simulation_agent.py`
- etc…

### 2.1 Data Directory Structure (Identical in Both Repos)

Both repos use the same data directory naming, so **bringing data over from the parent repo requires no path/filename changes**:

```
dummy_dataset/
├── item.json                # items / businesses
├── user.json                # users
├── review.json              # historical reviews
├── test_review_subset.json  # sampling source (input for create_sampled_dataset.py)
└── lmdb_cache/              # LMDB index (auto-built on first run; safe to delete)

dummy_tasks/                 # simulation tasks (task_1.json ~ task_N.json)
dummy_groundtruth/           # corresponding groundtruth (groundtruth_*.json)
```

If you generated new data in the parent repo via create_sampled_dataset.py or data_process.py

What you produced in the parent repo	Where it goes in the evolution repo
dummy_tasks/task_*.json	Same-named dummy_tasks/ (just copy)
dummy_groundtruth/groundtruth_*.json	Same-named dummy_groundtruth/ (just copy)
dummy_dataset/{item,user,review}.json	Same-named dummy_dataset/ (just copy; remember to remove the old lmdb_cache/)

> 💡 Paths are hard-coded in `openevolve_evaluator.py`, `run_test.py`, and `src/utils/create_sampled_dataset.py`, but **because the naming matches the parent repo, you don't need to edit those files**.
> 

---

## 3. Complete Migration Workflow (5 Steps)

### Assumptions

- You have already designed a Multi-Agent Crew in the parent repo (e.g., `user_analyst` + `item_analyst` + `prediction_modeler`)
- You have run `uv run python run_pipeline.py` in the parent repo and obtained reasonable metrics

### Step 1: Clone the Evolution Repo and Initialize

```bash
cd ~/WorkSpace/your_workspace/
git clone <https://github.com/yuchieh/AgentSocietyChallenge_OpenEvolve.git>
cd AgentSocietyChallenge_OpenEvolve

cp .env.example .env
# Edit .env to fill in OPENAI_API_KEY and OPENAI_API_BASE (e.g., NVIDIA NIM)

make install      # uv sync
```

### Step 2: Port Your Agent Design (3 Files)

**Assuming your parent repo lives at** `~/WorkSpace/your_workspace/AgentSocietyChallenge_w_CrewAI/`:

```bash
# Copy from parent repo into the same locations in the evolution repo
cp ~/WorkSpace/your_workspace/AgentSocietyChallenge_w_CrewAI/config/agents.yaml             config/agents.yaml
cp ~/WorkSpace/your_workspace/AgentSocietyChallenge_w_CrewAI/config/tasks.yaml              config/tasks.yaml
cp ~/WorkSpace/your_workspace/AgentSocietyChallenge_w_CrewAI/src/crews/simulation_crew.py   src/crews/simulation_crew.py
```

### Step 3: Run a Smoke Test to Confirm the Port

```bash
make smoke
```

Expected output:

```
✅ Integration test complete!
overall_quality: 0.7x ~ 0.8x  
```
> **If smoke test fails**, go back to the parent repo and verify it still works there, then re-check the file paths in Step 2. **Do not move forward until smoke passes.**
> 

### Step 4: Create `agents_evolving.yaml` — Mark Which Agents Should Evolve

Make a copy of `agents.yaml`:

```bash
cp config/agents.yaml config/agents_evolving.yaml
```

Then edit `config/agents_evolving.yaml` and **use `EVOLVE-BLOCK` markers to wrap the section you want the LLM to mutate**.

### Rules (Critical!)

| Rule | Why |
| --- | --- |
| 🔴 **Exactly one block per file** | OpenEvolve does not accept multiple blocks (it technically runs but converges much slower) |
| 🟢 **Agents WITH tools go OUTSIDE the block in the first run.** | Their prompts are tightly coupled to the ReAct format in `tasks.yaml`; if mutated, tool calls may break |
| 🟢 **Pure reasoning agents go INSIDE the block** | These agents have no tools, just synthesize information into output — perfect targets for evolution |
| 🟢 **Keep `llm:` field inside the block** | The LLM tends to preserve it naturally, but keeping it inside is safer |

### Example: Parent Repo's 3-Agent Structure

```yaml
# config/agents_evolving.yaml

# === Agents WITH tools stay OUTSIDE EVOLVE-BLOCK (protect tool-calling format) ===
user_analyst:
  role: >
    Yelp User Profiler
  goal: >
    Analyze user {user_id}'s historical reviews and preferences
  backstory: >
    You are an expert behavior analyst...
  llm: openai/minimaxai/minimax-m2.7

item_analyst:
  role: >
    Yelp Restaurant Analyst
  goal: >
    Analyze business {item_id}'s characteristics and reputation
  backstory: >
    You are a restaurant critic...
  llm: openai/minimaxai/minimax-m2.7

# === Pure reasoning agents go INSIDE the EVOLVE-BLOCK ===
# EVOLVE-BLOCK-START
prediction_modeler:
  role: >
    Review Prediction Expert
  goal: >
    Predict the exact Star rating (1.0 to 5.0) and generate a mock review text...
  backstory: >
    You are a master of predicting human behavior...
  llm: openai/minimaxai/minimax-m2.7
# EVOLVE-BLOCK-END
```

### Step 5: Launch Evolution

```bash
# Default: 10 iter × 5 tasks
make evolve

# Custom parameters
make evolve ITERS=10 TASKS=1

# Resume from a checkpoint (if a previous run was interrupted)
make evolve-resume CHECKPOINT=config/openevolve_output/checkpoints/checkpoint_10
```

While evolution runs, open another terminal for the visualizer:

```bash
make visualize
# Open browser at <http://127.0.0.1:8080>
```

---

## 4. Use the Best Evolved Result

```bash
# 1. Check the final best score
cat config/openevolve_output/best/best_program_info.json

# 2. Inspect the best evolved YAML
cat config/openevolve_output/best/best_program.yaml

# 3. Apply it to the production agents.yaml
cp config/openevolve_output/best/best_program.yaml config/agents.yaml

# 4. Run a full real-LLM test with the best version
make test
```

> Note: the `EVOLVE-BLOCK` markers in `agents_evolving.yaml` will appear in
`best_program.yaml` as YAML comments (`#`-prefixed). They are harmless — CrewAI
ignores them — but you may delete them for cleanliness when copying to `agents.yaml`.
>

5. Troubleshooting

Symptom	Likely Cause	Fix
make smoke returns overall_quality: 0.27	LLM API failed, evaluator returned fallback	Verify .env API key / base URL; confirm make test-mock works (mock mode doesn't use tokens)
Evaluator prints ⏱  Simulation exceeded 900s	A single simulation got stuck on LLM rate limits	Reduce TASKS=N, raise OPENEVOLVE_SIM_TIMEOUT=1800, or switch API
Mutated YAML breaks → all evaluations fail	OpenEvolve uses diff mode by default, which corrupts YAML	Confirm config/openevolve_config.yaml has diff_based_evolution: false
combined_score shows no improvement	EVOLVE-BLOCK is too small, search space is limited	Move more agents inside the block, or increase ITERS
Tool calls fail entirely (agent never invokes tools)	A tool-using agent inside EVOLVE-BLOCK and the LLM ruined its role	Move tool-using agents OUTSIDE the block

## 6. Quick Look: Evolution Loop Internals

When you run `make evolve`, here is what happens behind the scenes:

[Repeats for ITERS iterations]

  1. OpenEvolve samples a parent YAML from the population
                ▼
  2. LLM reads the parent YAML (including your EVOLVE-BLOCK markers)
     and produces a full-rewrite mutated YAML
                ▼
  3. The mutated YAML is written to /tmp/xxxxx.yaml
                ▼
  4. OpenEvolve calls openevolve_evaluator.py's evaluate(/tmp/xxxxx.yaml)
                ▼
  5. evaluate() sets env var OPENEVOLVE_AGENTS_YAML=/tmp/xxxxx.yaml
                ▼
  6. evaluate() calls simulator.run_simulation(N=TASKS)
                ▼
  7. Simulator spawns a CrewAISimulationAgent per task
                ▼
  8. CrewAISimulationAgent reads the env var → loads /tmp/xxxxx.yaml
     → assembles SimulationCrew with the mutated agents config
     → executes the 3 Tasks
                ▼
  9. Each task produces {stars, review}; Simulator computes metrics
     by comparing against groundtruth
                ▼
 10. evaluate() returns {"combined_score": overall_quality}
                ▼
 11. OpenEvolve writes this fitness into the MAP-Elites database
                ▼
 12. In the next iteration, high-fitness YAMLs are more likely
     to be sampled as parents

7. Additional Resources

| To learn about | See |
| --- | --- |
| How OpenEvolve works | https://github.com/algorithmicsuperintelligence/openevolve |
| How to write EVOLVE-BLOCK markers | `examples/README.md` inside the OpenEvolve repo |
| Detailed Simulator / InteractionTool API | `docs/legacy/tutorials/agent_development.md` |
| Our specific OpenEvolve integration details | `CLAUDE.md` |

## TL;DR — One-Page Cheat Sheet

1. **Clone** `AgentSocietyChallenge_OpenEvolve`, then `cp .env.example .env` and fill in API keys
2. **Copy 3 files** from parent repo into evolution repo: `agents.yaml`, `tasks.yaml`, `simulation_crew.py`
3. **`make smoke`** to verify nothing broke
4. **`cp agents.yaml agents_evolving.yaml`**, edit the copy to wrap pure-reasoning agents in **one** `EVOLVE-BLOCK`
5. **`make evolve ITERS=50 TASKS=3`** to launch evolution
6. After completion: **`cp config/openevolve_output/best/best_program.yaml config/agents.yaml`** to deploy the best version

🎉 Enjoy automatic LLM-driven prompt optimization for your Multi-Agent system.

Dear All:

I believe that you've finished the Step1-Step3 in the Integration Guide yesterday,
Please continue Steps 4 and 5, let the system evolve for 30 iterations on 1 task
 (make evolve ITERS=30 TASKS=1), Then copy and upload the best result you saw in the
 Visualizer to this folder.  Here is an example of 10 iterations.
Deadline: Next Monday (6/1) at 24:00.

Note: The evolution takes several hours, so it is recommended to start before sleep, and you will see the result the next morning. Besides, although the deadline is next Monday, I would recommend you try it tonight and buy some buffers. 

Let me know if you have any questions.

I RAN IT AND GOT THIS RESULT HERE -> C:\Users\MCC\Rag_Crew_Profiler\openevolve\AgentSocietyChallenge_OpenEvolve\config\openevolve_output

i think i will optimize it more later and add stuff to : C:\Users\MCC\Rag_Crew_Profiler\openevolve\AgentSocietyChallenge_OpenEvolve\config\agents_evolving.yaml

I WILL SEE THE BEST BUT NOW I HAVE TO FOCUS ON LAB 15 SINCE I ALREADY RAN OPENEVOLVE TEST AS PROFESSOR ASKED AND IT RAN FOR 2 HOURS AND I GOT FAIR RESULT. WORSE THAN MY CLASSMATES THO LOL! 


```

---

# File: LAB 16 TODAY IMPORTANT
Path: `c:\Users\MCC\Rag_Crew_Profiler\openevolve\LAB 16 TODAY IMPORTANT`

```text
# LLM & APP (w16 2026 Spring)

**Tuesday 10:10-13:00, E307 Engineering II**

**Instructor: Yu-Chieh Jack Ho**

**Office:** A302, Engineering II  | **Office hours:** Weds 10:30-12:30 | **Email:** yc.ho@gms.ndhu.edu.tw


# Agenda:

- **Final Project Discussion**
- **Seminar: World Models Paper Wrap Up**
- **Lecture: Preference Fine-Tuning**
- **LAB: Preference Fine-Tuning with DPO (Direct Preference Optimization) and QLoRA**
- **Final Project Spirint**

# **Final Project Recap and Discussion**

## **📊 Grading (30% of Course Grade)**

- The grading will be based on:
    - The **Novelty** about **what** and **how** you leverage ****OpenEvolve to optimize your agent crew.
        - Be creative!
    - The **depth of evolution analysis**
        - Parse and explain the evolution path, discuss interesting strategies OpenEvolve discovered.
    - **Performance**
        - Evolve 50 iterations on 1 task and report the final combined score in the report.

## **Technical Report &** Presentation

- Format:
    - Google Slides, Markdown (can be the README of your repo), or Both. Just make sure you can share your findings properly.
- Content:
    - **Novelty finding first**:
        - Crew **Diagram**: Members and their Collaboration Pattern
        - Agents Design: Role, Goal, Backstory, **TOOL USE**
        - Tasks: Description, Expected_output
        - Etc…
    - **Evolution Analysis**:
        - Use the **visualizer** to compare the differences between Gen-0 and evolved results
        - Analyze  the checkpoints data to parse and explain the evolution ****paths.
- Please attach your GitHub link to your report and push your report to your GitHub, then upload your report to  https://drive.google.com/drive/folders/1S_m8D_uugqc64czOPOeTGRMlS3bjOiA4?usp=sharing

## Presentation Date
- **6/23**
- **6/16**

## Future Plan: Co-Evolving Agents and Tasks

Yes, you absolutely can!

In OpenEvolve, you can co-evolve both agents and tasks simultaneously. You simply wrap the specific agents you want to evolve in config/agents_evolving.yaml with the # EVOLVE-BLOCK-START and # EVOLVE-BLOCK-END tags, and do the exact same thing for the specific tasks you want to evolve in config/tasks_evolving.yaml.

During the evolution loop, the framework will mutate both the agent personas (roles/backstories) and the task instructions together to find the best combined strategy.

```

---

# File: task_1.json
Path: `c:\Users\MCC\Rag_Crew_Profiler\openevolve\AgentSocietyChallenge_OpenEvolve\dummy_tasks\task_1.json`

```json
{
  "type": "user_behavior_simulation",
  "user_id": "PZ47ZU2aXZNd9SKm-Ua7JA",
  "item_id": "Uc6PdjT_MO5bRPQsUUEy5Q"
}
```

---

# File: groundtruth_1.json
Path: `c:\Users\MCC\Rag_Crew_Profiler\openevolve\AgentSocietyChallenge_OpenEvolve\dummy_groundtruth\groundtruth_1.json`

```json
{
  "stars": 5.0,
  "review": "I was stationed in Italy my first 3 years in the military and have been struggling to find amazing pizza ever since... I was very spoiled! I found an amazing place when I was stationed in Texas and was very happy to stumble upon this place while here in Tampa on business! My team and I ordered the white pizza with prosciutto and the carnivore, as well... and they were both absolutely delicious!!! This is absolutely at the top of my list for the next time I'm in town and would definitely recommend this place to pizza lovers!!!"
}
```

---

# File: evaluation_result.py
Path: `c:\Users\MCC\Rag_Crew_Profiler\openevolve\openevolve\evaluation_result.py`

```py
"""
Evaluation result structures for OpenEvolve
"""

import json
from dataclasses import dataclass, field
from typing import Dict, Union


@dataclass
class EvaluationResult:
    """
    Result of program evaluation containing both metrics and optional artifacts

    This maintains backward compatibility with the existing dict[str, float] contract
    while adding a side-channel for arbitrary artifacts (text or binary data).

    IMPORTANT: For custom MAP-Elites features, metrics values must be raw continuous
    scores (e.g., actual counts, percentages, continuous measurements), NOT pre-computed
    bin indices. The database handles all binning internally using min-max scaling.

    Examples:
        ✅ Correct: {"combined_score": 0.85, "prompt_length": 1247, "execution_time": 0.234}
        ❌ Wrong:   {"combined_score": 0.85, "prompt_length": 7, "execution_time": 3}
    """

    metrics: Dict[str, float]  # mandatory - existing contract
    artifacts: Dict[str, Union[str, bytes]] = field(default_factory=dict)  # optional side-channel

    @classmethod
    def from_dict(cls, metrics: Dict[str, float]) -> "EvaluationResult":
        """Auto-wrap dict returns for backward compatibility"""
        return cls(metrics=metrics)

    def to_dict(self) -> Dict[str, float]:
        """Backward compatibility - return just metrics"""
        return self.metrics

    def has_artifacts(self) -> bool:
        """Check if this result contains any artifacts"""
        return bool(self.artifacts)

    def get_artifact_keys(self) -> list:
        """Get list of artifact keys"""
        return list(self.artifacts.keys())

    def get_artifact_size(self, key: str) -> int:
        """Get size of a specific artifact in bytes"""
        if key not in self.artifacts:
            return 0

        value = self.artifacts[key]
        if isinstance(value, str):
            return len(value.encode("utf-8"))
        elif isinstance(value, bytes):
            return len(value)
        else:
            return len(str(value).encode("utf-8"))

    def get_total_artifact_size(self) -> int:
        """Get total size of all artifacts in bytes"""
        return sum(self.get_artifact_size(key) for key in self.artifacts.keys())
```

---

# File: controller.py
Path: `c:\Users\MCC\Rag_Crew_Profiler\openevolve\openevolve\controller.py`

```py
"""
Main controller for OpenEvolve
"""

import asyncio
import logging
import os
import shutil
import signal
import time
import uuid
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from openevolve.config import Config, load_config
from openevolve.database import Program, ProgramDatabase
from openevolve.evaluator import Evaluator
from openevolve.evolution_trace import EvolutionTracer
from openevolve.llm.ensemble import LLMEnsemble
from openevolve.process_parallel import ProcessParallelController
from openevolve.prompt.sampler import PromptSampler
from openevolve.utils.code_utils import extract_code_language
from openevolve.utils.format_utils import format_improvement_safe, format_metrics_safe

logger = logging.getLogger(__name__)


def _format_metrics(metrics: Dict[str, Any]) -> str:
    """Safely format metrics, handling both numeric and string values"""
    formatted_parts = []
    for name, value in metrics.items():
        if isinstance(value, (int, float)) and not isinstance(value, bool):
            try:
                formatted_parts.append(f"{name}={value:.4f}")
            except (ValueError, TypeError):
                formatted_parts.append(f"{name}={value}")
        else:
            formatted_parts.append(f"{name}={value}")
    return ", ".join(formatted_parts)


def _format_improvement(improvement: Dict[str, Any]) -> str:
    """Safely format improvement metrics"""
    formatted_parts = []
    for name, diff in improvement.items():
        if isinstance(diff, (int, float)) and not isinstance(diff, bool):
            try:
                formatted_parts.append(f"{name}={diff:+.4f}")
            except (ValueError, TypeError):
                formatted_parts.append(f"{name}={diff}")
        else:
            formatted_parts.append(f"{name}={diff}")
    return ", ".join(formatted_parts)


class OpenEvolve:
    """
    Main controller for OpenEvolve

    Orchestrates the evolution process, coordinating between the prompt sampler,
    LLM ensemble, evaluator, and program database.

    Features:
    - Tracks the absolute best program across evolution steps
    - Ensures the best solution is not lost during the MAP-Elites process
    - Always includes the best program in the selection process for inspiration
    - Maintains detailed logs and metadata about improvements
    """

    def __init__(
        self,
        initial_program_path: str,
        evaluation_file: str,
        config: Config,
        output_dir: Optional[str] = None,
    ):
        # Load configuration (loaded in main_async)
        self.config = config

        # Set up output directory
        self.output_dir = output_dir or os.path.join(
            os.path.dirname(initial_program_path), "openevolve_output"
        )
        os.makedirs(self.output_dir, exist_ok=True)

        # Set up logging
        self._setup_logging()

        # Manual mode queue lives in <openevolve_output>/manual_tasks_queue
        self._setup_manual_mode_queue()

        # Set random seed for reproducibility if specified
        if self.config.random_seed is not None:
            import hashlib
            import random

            import numpy as np

            # Set global random seeds
            random.seed(self.config.random_seed)
            np.random.seed(self.config.random_seed)

            # Create hash-based seeds for different components
            base_seed = str(self.config.random_seed).encode("utf-8")
            llm_seed = int(hashlib.md5(base_seed + b"llm").hexdigest()[:8], 16) % (2**31)

            # Propagate seed to LLM configurations
            self.config.llm.random_seed = llm_seed
            for model_cfg in self.config.llm.models:
                if not hasattr(model_cfg, "random_seed") or model_cfg.random_seed is None:
                    model_cfg.random_seed = llm_seed
            for model_cfg in self.config.llm.evaluator_models:
                if not hasattr(model_cfg, "random_seed") or model_cfg.random_seed is None:
                    model_cfg.random_seed = llm_seed

            logger.info(f"Set random seed to {self.config.random_seed} for reproducibility")
            logger.debug(f"Generated LLM seed: {llm_seed}")

        # Load initial program
        self.initial_program_path = initial_program_path
        self.initial_program_code = self._load_initial_program()
        if not self.config.language:
            self.config.language = extract_code_language(self.initial_program_code)

        # Extract file extension from initial program
        self.file_extension = os.path.splitext(initial_program_path)[1]
        if not self.file_extension:
            # Default to .py if no extension found
            self.file_extension = ".py"
        else:
            # Make sure it starts with a dot
            if not self.file_extension.startswith("."):
                self.file_extension = f".{self.file_extension}"

        # Set the file_suffix in config (can be overridden in YAML)
        if not hasattr(self.config, "file_suffix") or self.config.file_suffix == ".py":
            self.config.file_suffix = self.file_extension

        # Initialize components
        self.llm_ensemble = LLMEnsemble(self.config.llm.models)
        self.llm_evaluator_ensemble = LLMEnsemble(self.config.llm.evaluator_models)

        self.prompt_sampler = PromptSampler(self.config.prompt)
        self.evaluator_prompt_sampler = PromptSampler(self.config.prompt)
        self.evaluator_prompt_sampler.set_templates("evaluator_system_message")

        # Pass random seed to database if specified
        if self.config.random_seed is not None:
            self.config.database.random_seed = self.config.random_seed

        self.config.database.novelty_llm = self.llm_ensemble
        self.database = ProgramDatabase(self.config.database)

        self.evaluator = Evaluator(
            self.config.evaluator,
            evaluation_file,
            self.llm_evaluator_ensemble,
            self.evaluator_prompt_sampler,
            database=self.database,
            suffix=Path(self.initial_program_path).suffix,
        )
        self.evaluation_file = evaluation_file

        logger.info(f"Initialized OpenEvolve with {initial_program_path}")

        # Initialize evolution tracer
        if self.config.evolution_trace.enabled:
            trace_output_path = self.config.evolution_trace.output_path
            if not trace_output_path:
                # Default to output_dir/evolution_trace.{format}
                trace_output_path = os.path.join(
                    self.output_dir, f"evolution_trace.{self.config.evolution_trace.format}"
                )

            self.evolution_tracer = EvolutionTracer(
                output_path=trace_output_path,
                format=self.config.evolution_trace.format,
                include_code=self.config.evolution_trace.include_code,
                include_prompts=self.config.evolution_trace.include_prompts,
                enabled=True,
                buffer_size=self.config.evolution_trace.buffer_size,
                compress=self.config.evolution_trace.compress,
            )
            logger.info(f"Evolution tracing enabled: {trace_output_path}")
        else:
            self.evolution_tracer = None

        # Initialize improved parallel processing components
        self.parallel_controller = None

    def _setup_logging(self) -> None:
        """Set up logging"""
        log_dir = self.config.log_dir or os.path.join(self.output_dir, "logs")
        os.makedirs(log_dir, exist_ok=True)

        # Set up root logger
        root_logger = logging.getLogger()
        root_logger.setLevel(getattr(logging, self.config.log_level))

        # Add file handler
        log_file = os.path.join(log_dir, f"openevolve_{time.strftime('%Y%m%d_%H%M%S')}.log")
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(
            logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        )
        root_logger.addHandler(file_handler)

        # Add console handler
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))
        root_logger.addHandler(console_handler)

        logger.info(f"Logging to {log_file}")

    def _setup_manual_mode_queue(self) -> None:
        """
        Set up manual task queue directory if llm.manual_mode is enabled

        Queue directory is always:
          <openevolve_output>/manual_tasks_queue

        The directory is cleared on controller start so the UI shows only tasks
        from the current run (no stale tasks after restart)
        """
        if not bool(getattr(self.config.llm, "manual_mode", False)):
            return

        qdir = (Path(self.output_dir).expanduser().resolve() / "manual_tasks_queue")

        # Clear stale tasks from previous runs
        if qdir.exists():
            shutil.rmtree(qdir)
        qdir.mkdir(parents=True, exist_ok=True)

        # Inject runtime-only queue dir into configs
        self.config.llm._manual_queue_dir = str(qdir)
        for model_cfg in self.config.llm.models:
            model_cfg._manual_queue_dir = str(qdir)
        for model_cfg in self.config.llm.evaluator_models:
            model_cfg._manual_queue_dir = str(qdir)

        logger.info(f"Manual mode enabled. Queue dir: {qdir}")

    def _load_initial_program(self) -> str:
        """Load the initial program from file"""
        with open(self.initial_program_path, "r") as f:
            return f.read()

    async def run(
        self,
        iterations: Optional[int] = None,
        target_score: Optional[float] = None,
        checkpoint_path: Optional[str] = None,
    ) -> Optional[Program]:
        """
        Run the evolution process with improved parallel processing

        Args:
            iterations: Maximum number of iterations (uses config if None)
            target_score: Target score to reach (continues until reached if specified)
            checkpoint_path: Path to resume from checkpoint

        Returns:
            Best program found
        """
        max_iterations = iterations or self.config.max_iterations

        # Determine starting iteration
        start_iteration = 0
        if checkpoint_path and os.path.exists(checkpoint_path):
            self._load_checkpoint(checkpoint_path)
            start_iteration = self.database.last_iteration + 1
            logger.info(f"Resuming from checkpoint at iteration {start_iteration}")
        else:
            start_iteration = self.database.last_iteration

        # Only add initial program if starting fresh (not resuming from checkpoint)
        should_add_initial = (
            start_iteration == 0
            and len(self.database.programs) == 0
            and not any(
                p.code == self.initial_program_code for p in self.database.programs.values()
            )
        )

        if should_add_initial:
            logger.info("Adding initial program to database")
            initial_program_id = str(uuid.uuid4())

            # Evaluate the initial program
            initial_metrics = await self.evaluator.evaluate_program(
                self.initial_program_code, initial_program_id
            )

            initial_program = Program(
                id=initial_program_id,
                code=self.initial_program_code,
                changes_description=self.config.prompt.initial_changes_description,
                language=self.config.language,
                metrics=initial_metrics,
                iteration_found=start_iteration,
            )

            self.database.add(initial_program)

            # Check if combined_score is present in the metrics
            if "combined_score" not in initial_metrics:
                # Calculate average of numeric metrics
                numeric_metrics = [
                    v
                    for v in initial_metrics.values()
                    if isinstance(v, (int, float)) and not isinstance(v, bool)
                ]
                if numeric_metrics:
                    avg_score = sum(numeric_metrics) / len(numeric_metrics)
                    logger.warning(
                        f"⚠️  No 'combined_score' metric found in evaluation results. "
                        f"Using average of all numeric metrics ({avg_score:.4f}) for evolution guidance. "
                        f"For better evolution results, please modify your evaluator to return a 'combined_score' "
                        f"metric that properly weights different aspects of program performance."
                    )
        else:
            logger.info(
                f"Skipping initial program addition (resuming from iteration {start_iteration} "
                f"with {len(self.database.programs)} existing programs)"
            )

        # Initialize improved parallel processing
        try:
            self.parallel_controller = ProcessParallelController(
                self.config,
                self.evaluation_file,
                self.database,
                self.evolution_tracer,
                file_suffix=self.config.file_suffix,
            )

            # Set up signal handlers for graceful shutdown
            def signal_handler(signum, frame):
                logger.info(f"Received signal {signum}, initiating graceful shutdown...")
                self.parallel_controller.request_shutdown()

                # Set up a secondary handler for immediate exit if user presses Ctrl+C again
                def force_exit_handler(signum, frame):
                    logger.info("Force exit requested - terminating immediately")
                    import sys

                    sys.exit(0)

                signal.signal(signal.SIGINT, force_exit_handler)

            signal.signal(signal.SIGINT, signal_handler)
            signal.signal(signal.SIGTERM, signal_handler)

            self.parallel_controller.start()

            # When starting from iteration 0, we've already done the initial program evaluation
            # So we need to adjust the start_iteration for the actual evolution
            evolution_start = start_iteration
            evolution_iterations = max_iterations

            # If we just added the initial program at iteration 0, start evolution from iteration 1
            if should_add_initial and start_iteration == 0:
                evolution_start = 1
                # User expects max_iterations evolutionary iterations AFTER the initial program
                # So we don't need to reduce evolution_iterations

            # Run evolution with improved parallel processing and checkpoint callback
            await self._run_evolution_with_checkpoints(
                evolution_start, evolution_iterations, target_score
            )

        finally:
            # Clean up parallel processing resources
            if self.parallel_controller:
                self.parallel_controller.stop()
                self.parallel_controller = None

            # Close evolution tracer
            if self.evolution_tracer:
                self.evolution_tracer.close()
                logger.info("Evolution tracer closed")

        # Get the best program
        best_program = None
        if self.database.best_program_id:
            best_program = self.database.get(self.database.best_program_id)
            logger.info(f"Using tracked best program: {self.database.best_program_id}")

        if best_program is None:
            best_program = self.database.get_best_program()
            logger.info("Using calculated best program (tracked program not found)")

        if best_program:
            if (
                hasattr(self, "parallel_controller")
                and self.parallel_controller
                and self.parallel_controller.early_stopping_triggered
            ):
                logger.info(
                    f"🛑 Evolution complete via early stopping. Best program has metrics: "
                    f"{format_metrics_safe(best_program.metrics)}"
                )
            else:
                logger.info(
                    f"Evolution complete. Best program has metrics: "
                    f"{format_metrics_safe(best_program.metrics)}"
                )
            self._save_best_program(best_program)
            return best_program
        else:
            logger.warning("No valid programs found during evolution")
            return None

    def _log_iteration(
        self,
        iteration: int,
        parent: Program,
        child: Program,
        elapsed_time: float,
    ) -> None:
        """
        Log iteration progress

        Args:
            iteration: Iteration number
            parent: Parent program
            child: Child program
            elapsed_time: Elapsed time in seconds
        """
        # Calculate improvement using safe formatting
        improvement_str = format_improvement_safe(parent.metrics, child.metrics)

        logger.info(
            f"Iteration {iteration+1}: Child {child.id} from parent {parent.id} "
            f"in {elapsed_time:.2f}s. Metrics: "
            f"{format_metrics_safe(child.metrics)} "
            f"(Δ: {improvement_str})"
        )

    def _save_checkpoint(self, iteration: int) -> None:
        """
        Save a checkpoint

        Args:
            iteration: Current iteration number
        """
        checkpoint_dir = os.path.join(self.output_dir, "checkpoints")
        os.makedirs(checkpoint_dir, exist_ok=True)

        # Create specific checkpoint directory
        checkpoint_path = os.path.join(checkpoint_dir, f"checkpoint_{iteration}")
        os.makedirs(checkpoint_path, exist_ok=True)

        # Save the database
        self.database.save(checkpoint_path, iteration)

        # Save the best program found so far
        best_program = None
        if self.database.best_program_id:
            best_program = self.database.get(self.database.best_program_id)
        else:
            best_program = self.database.get_best_program()

        if best_program:
            # Save the best program at this checkpoint
            best_program_path = os.path.join(checkpoint_path, f"best_program{self.file_extension}")
            with open(best_program_path, "w") as f:
                f.write(best_program.code)

            # Save metrics
            best_program_info_path = os.path.join(checkpoint_path, "best_program_info.json")
            with open(best_program_info_path, "w") as f:
                import json

                json.dump(
                    {
                        "id": best_program.id,
                        "generation": best_program.generation,
                        "iteration": best_program.iteration_found,
                        "current_iteration": iteration,
                        "metrics": best_program.metrics,
                        "language": best_program.language,
                        "timestamp": best_program.timestamp,
                        "saved_at": time.time(),
                    },
                    f,
                    indent=2,
                )

            logger.info(
                f"Saved best program at checkpoint {iteration} with metrics: "
                f"{format_metrics_safe(best_program.metrics)}"
            )

        logger.info(f"Saved checkpoint at iteration {iteration} to {checkpoint_path}")

    def _load_checkpoint(self, checkpoint_path: str) -> None:
        """Load state from a checkpoint directory"""
        if not os.path.exists(checkpoint_path):
            raise FileNotFoundError(f"Checkpoint directory {checkpoint_path} not found")

        logger.info(f"Loading checkpoint from {checkpoint_path}")
        self.database.load(checkpoint_path)
        logger.info(f"Checkpoint loaded successfully (iteration {self.database.last_iteration})")

    async def _run_evolution_with_checkpoints(
        self, start_iteration: int, max_iterations: int, target_score: Optional[float]
    ) -> None:
        """Run evolution with checkpoint saving support"""
        logger.info(f"Using island-based evolution with {self.config.database.num_islands} islands")
        self.database.log_island_status()

        # Run the evolution process with checkpoint callback
        await self.parallel_controller.run_evolution(
            start_iteration, max_iterations, target_score, checkpoint_callback=self._save_checkpoint
        )

        # Check if shutdown or early stopping was triggered
        if self.parallel_controller.shutdown_event.is_set():
            logger.info("Evolution stopped due to shutdown request")
            return
        elif self.parallel_controller.early_stopping_triggered:
            logger.info("Evolution stopped due to early stopping - saving final checkpoint")
            # Continue to save final checkpoint for early stopping

        # Save final checkpoint if needed
        # Note: start_iteration here is the evolution start (1 for fresh start, not 0)
        # max_iterations is the number of evolution iterations to run
        final_iteration = start_iteration + max_iterations - 1
        if final_iteration > 0 and final_iteration % self.config.checkpoint_interval == 0:
            self._save_checkpoint(final_iteration)

    def _save_best_program(self, program: Optional[Program] = None) -> None:
        """
        Save the best program

        Args:
            program: Best program (if None, uses the tracked best program)
        """
        # If no program is provided, use the tracked best program from the database
        if program is None:
            if self.database.best_program_id:
                program = self.database.get(self.database.best_program_id)
            else:
                # Fallback to calculating best program if no tracked best program
                program = self.database.get_best_program()

        if not program:
            logger.warning("No best program found to save")
            return

        best_dir = os.path.join(self.output_dir, "best")
        os.makedirs(best_dir, exist_ok=True)

        # Use the extension from the initial program file
        filename = f"best_program{self.file_extension}"
        code_path = os.path.join(best_dir, filename)

        with open(code_path, "w") as f:
            f.write(program.code)

        # Save complete program info including metrics
        info_path = os.path.join(best_dir, "best_program_info.json")
        with open(info_path, "w") as f:
            import json

            json.dump(
                {
                    "id": program.id,
                    "generation": program.generation,
                    "iteration": program.iteration_found,
                    "timestamp": program.timestamp,
                    "parent_id": program.parent_id,
                    "metrics": program.metrics,
                    "language": program.language,
                    "saved_at": time.time(),
                },
                f,
                indent=2,
            )

        logger.info(f"Saved best program to {code_path} with program info to {info_path}")
```

---

# File: interaction_tool.py
Path: `c:\Users\MCC\Rag_Crew_Profiler\openevolve\AgentSocietyChallenge_OpenEvolve\websocietysimulator\tools\interaction_tool.py`

```py
import logging
import os
import json
import pandas as pd
from typing import Optional, Dict, List, Any

logger = logging.getLogger("websocietysimulator")

class InteractionTool:
    def __init__(self, data_dir: str):
        """
        Initialize the tool with the dataset directory.
        Args:
            data_dir: Path to the directory containing Yelp dataset files.
        """
        logger.info(f"Initializing InteractionTool with data directory: {data_dir}")
        self.data_dir = data_dir
        # Convert DataFrames to dictionaries for O(1) lookup
        logger.info(f"Loading item data from {os.path.join(data_dir, 'item.json')}")
        self.item_data = {item['item_id']: item for item in self._load_data('item.json')}
        logger.info(f"Loading user data from {os.path.join(data_dir, 'user.json')}")
        self.user_data = {user['user_id']: user for user in self._load_data('user.json')}
        
        # Create review indices
        logger.info(f"Loading review data from {os.path.join(data_dir, 'review.json')}")
        reviews = self._load_data('review.json')
        self.review_data = {review['review_id']: review for review in reviews}
        self.item_reviews = {}
        self.user_reviews = {}
        
        # Build review indices
        logger.info("Building review indices")
        for review in reviews:
            # Index by item_id
            self.item_reviews.setdefault(review['item_id'], []).append(review)
            # Index by user_id
            self.user_reviews.setdefault(review['user_id'], []).append(review)

    def _load_data(self, filename: str) -> List[Dict]:
        """Load data as a list of dictionaries."""
        file_path = os.path.join(self.data_dir, filename)
        with open(file_path, 'r', encoding='utf-8') as file:
            return [json.loads(line) for line in file]

    def get_user(self, user_id: str) -> Optional[Dict]:
        """Fetch user data based on user_id."""
        return self.user_data.get(user_id)

    def get_item(self, item_id: str = None) -> Optional[Dict]:
        """Fetch item data based on item_id."""
        return self.item_data.get(item_id) if item_id else None

    def get_reviews(
        self, 
        item_id: Optional[str] = None, 
        user_id: Optional[str] = None, 
        review_id: Optional[str] = None
    ) -> List[Dict]:
        """Fetch reviews filtered by various parameters."""
        if review_id:
            return [self.review_data[review_id]] if review_id in self.review_data else []
        
        if item_id:
            return self.item_reviews.get(item_id, [])
        elif user_id:
            return self.user_reviews.get(user_id, [])
        
        return []
```

---

# File: evaluation_tool.py
Path: `c:\Users\MCC\Rag_Crew_Profiler\openevolve\AgentSocietyChallenge_OpenEvolve\websocietysimulator\tools\evaluation_tool.py`

```py
import json
import logging
import numpy as np
from typing import List, Dict, Union
from dataclasses import dataclass
from nltk.sentiment import SentimentIntensityAnalyzer
from transformers import pipeline
from sentence_transformers import SentenceTransformer
from scipy.spatial import distance
import torch
import nltk

def ensure_nltk_data():
    """Ensure NLTK data is available"""
    try:
        nltk.data.find('sentiment/vader_lexicon.zip')
    except LookupError:
        logging.warning("VADER lexicon not found, downloading...")
        nltk.download('vader_lexicon', quiet=True)

# Check NLTK data availability at import time
ensure_nltk_data()

@dataclass
class RecommendationMetrics:
    top_1_hit_rate: float
    top_3_hit_rate: float
    top_5_hit_rate: float
    average_hit_rate: float
    total_scenarios: int
    top_1_hits: int
    top_3_hits: int
    top_5_hits: int

@dataclass
class SimulationMetrics:
    preference_estimation: float
    review_generation: float
    overall_quality: float

class BaseEvaluator:
    """Base class for evaluation tools"""
    def __init__(self):
        self.metrics_history: List[Union[RecommendationMetrics, SimulationMetrics]] = []

    def save_metrics(self, metrics: Union[RecommendationMetrics, SimulationMetrics]):
        """Save metrics to history"""
        self.metrics_history.append(metrics)

    def get_metrics_history(self):
        """Get all historical metrics"""
        return self.metrics_history

class RecommendationEvaluator(BaseEvaluator):
    """Evaluator for recommendation tasks"""
    
    def __init__(self):
        super().__init__()
        self.n_values = [1, 3, 5]  # 预定义的n值数组

    def calculate_hr_at_n(
        self,
        ground_truth: List[str],
        predictions: List[List[str]]
    ) -> RecommendationMetrics:
        """Calculate Hit Rate at different N values"""
        total = len(ground_truth)
        hits = {n: 0 for n in self.n_values}
        
        for gt, pred in zip(ground_truth, predictions):
            for n in self.n_values:
                if gt in pred[:n]:
                    hits[n] += 1
        
        top_1_hit_rate = hits[1] / total if total > 0 else 0
        top_3_hit_rate = hits[3] / total if total > 0 else 0
        top_5_hit_rate = hits[5] / total if total > 0 else 0
        average_hit_rate = (top_1_hit_rate + top_3_hit_rate + top_5_hit_rate) / 3
        metrics = RecommendationMetrics(
            top_1_hit_rate=top_1_hit_rate,
            top_3_hit_rate=top_3_hit_rate,
            top_5_hit_rate=top_5_hit_rate,
            average_hit_rate=average_hit_rate,
            total_scenarios=total,
            top_1_hits=hits[1],
            top_3_hits=hits[3],
            top_5_hits=hits[5]
        )
        
        self.save_metrics(metrics)
        return metrics

class SimulationEvaluator(BaseEvaluator):
    """Evaluator for simulation tasks"""
    
    def __init__(self, device: str = "auto"):
        super().__init__()
        self.device = self._get_device(device)
        
        pipeline_device = self.device
        st_device = "cuda" if self.device == 0 else "cpu" 
        
        self.sia = SentimentIntensityAnalyzer()
        self.emotion_classifier = pipeline(
            "text-classification",
            model="cardiffnlp/twitter-roberta-base-emotion",
            top_k=5,
            device=pipeline_device
        )
        self.topic_model = SentenceTransformer(
            'paraphrase-MiniLM-L6-v2',
            device=st_device
        )
        
    def _get_device(self, device: str) -> int:
        """Parse device from string"""
        if device == "gpu":
            if torch.cuda.is_available():
                return 0  # GPU
            else:
                logging.warning("GPU is not available, falling back to CPU")
                return -1  # CPU
        elif device == "cpu":
            return -1  # CPU
        elif device == "auto":
            return 0 if torch.cuda.is_available() else -1
        else:
            raise ValueError("Device type must be 'cpu', 'gpu' or 'auto'")

    def calculate_metrics(
        self,
        simulated_data: List[Dict],
        real_data: List[Dict]
    ) -> SimulationMetrics:
        """Calculate all simulation metrics"""
        # Calculate star error
        simulated_stars = [item['stars'] for item in simulated_data]
        real_stars = [item['stars'] for item in real_data]
        star_error = 0
        for sim_star, real_star in zip(simulated_stars, real_stars):
            if sim_star > 5:
                sim_star = 5
            elif sim_star < 0:
                sim_star = 0
            star_error += abs(sim_star - real_star) / 5
        star_error = star_error / len(real_stars)
        preference_estimation = 1 - star_error

        # Calculate review metrics
        simulated_reviews = [item['review'] for item in simulated_data]
        real_reviews = [item['review'] for item in real_data]
        review_details = self._calculate_review_metrics(
            simulated_reviews,
            real_reviews
        )

        sentiment_error = review_details['sentiment_error']
        emotion_error = review_details['emotion_error']
        topic_error = review_details['topic_error']
        review_generation = 1 - (sentiment_error * 0.25 + emotion_error * 0.25 + topic_error * 0.5)
        overall_quality = (preference_estimation + review_generation) / 2

        metrics = SimulationMetrics(
            preference_estimation=preference_estimation,
            review_generation=review_generation,
            overall_quality=overall_quality
        )

        self.save_metrics(metrics)
        return metrics

    def _calculate_review_metrics(
        self,
        simulated_reviews: List[str],
        real_reviews: List[str]
    ) -> Dict[str, float]:
        """Calculate detailed review metrics between two texts"""
        # sentiment analysis
        sentiment_error = []
        emotion_error = []
        topic_error = []
        for simulated_review, real_review in zip(simulated_reviews, real_reviews):
            # sentiment analysis
            sentiment1 = self.sia.polarity_scores(simulated_review)['compound']
            sentiment2 = self.sia.polarity_scores(real_review)['compound']
            sentiment_error_single = abs(sentiment1 - sentiment2) / 2
            sentiment_error.append(sentiment_error_single)

            # Topic analysis
            embeddings = self.topic_model.encode([simulated_review, real_review])
            topic_error_single = distance.cosine(embeddings[0], embeddings[1]) / 2
            topic_error.append(topic_error_single)

        # Emotion analysis
        for i in range(len(simulated_reviews)):
            if len(simulated_reviews[i]) > 300:
                simulated_reviews[i] = simulated_reviews[i][:300]
            if len(real_reviews[i]) > 300:
                real_reviews[i] = real_reviews[i][:300]
        simulated_emotions = self.emotion_classifier(simulated_reviews)
        real_emotions = self.emotion_classifier(real_reviews)
        for sim_emotion, real_emotion in zip(simulated_emotions, real_emotions):
            emotion_error_single = self._calculate_emotion_error(sim_emotion, real_emotion)
            emotion_error.append(emotion_error_single)

        sentiment_error = np.mean(sentiment_error)
        emotion_error = np.mean(emotion_error)
        topic_error = np.mean(topic_error)
        return {
            'sentiment_error': sentiment_error,
            'emotion_error': emotion_error,
            'topic_error': topic_error,
        }

    def _calculate_emotion_error(
        self,
        emotions1: List[Dict],
        emotions2: List[Dict]
    ) -> float:
        """Calculate similarity between two emotion distributions"""
        # Convert emotions to vectors
        emotion_dict1 = {e['label']: e['score'] for e in emotions1}
        emotion_dict2 = {e['label']: e['score'] for e in emotions2}
        
        # Get all unique emotions
        all_emotions = set(emotion_dict1.keys()) | set(emotion_dict2.keys())
        
        # Create vectors
        vec1 = np.array([emotion_dict1.get(e, 0) for e in all_emotions])
        vec2 = np.array([emotion_dict2.get(e, 0) for e in all_emotions])

        # Calculate emotion error
        return float(np.mean(np.abs(vec1 - vec2)))
```

---

# File: cache_interaction_tool.py
Path: `c:\Users\MCC\Rag_Crew_Profiler\openevolve\AgentSocietyChallenge_OpenEvolve\websocietysimulator\tools\cache_interaction_tool.py`

```py
import logging
import os
import json
import lmdb
from typing import Optional, Dict, List, Iterator
from tqdm import tqdm

logger = logging.getLogger("websocietysimulator")

class CacheInteractionTool:
    def __init__(self, data_dir: str):
        """
        Initialize the tool with the dataset directory.
        Args:
            data_dir: Path to the directory containing Yelp dataset files.
        """
        logger.info(f"Initializing InteractionTool with data directory: {data_dir}")
        self.data_dir = data_dir

        # Create LMDB environments
        self.env_dir = os.path.join(data_dir, "lmdb_cache")
        os.makedirs(self.env_dir, exist_ok=True)

        self.user_env = lmdb.open(os.path.join(self.env_dir, "users"), map_size=2 * 1024 * 1024 * 1024)
        self.item_env = lmdb.open(os.path.join(self.env_dir, "items"), map_size=2 * 1024 * 1024 * 1024)
        self.review_env = lmdb.open(os.path.join(self.env_dir, "reviews"), map_size=8 * 1024 * 1024 * 1024)

        # Initialize the database if empty
        self._initialize_db()

    def _initialize_db(self):
        """Initialize the LMDB databases with data if they are empty."""
        # Initialize users
        with self.user_env.begin(write=True) as txn:
            if not txn.stat()['entries']:
                with txn.cursor() as cursor:
                    for user in tqdm(self._iter_file('user.json')):
                        cursor.put(
                            user['user_id'].encode(),
                            json.dumps(user).encode()
                        )

        # Initialize items
        with self.item_env.begin(write=True) as txn:
            if not txn.stat()['entries']:
                with txn.cursor() as cursor:
                    for item in tqdm(self._iter_file('item.json')):
                        cursor.put(
                            item['item_id'].encode(),
                            json.dumps(item).encode()
                        )

        # Initialize reviews and their indices
        with self.review_env.begin(write=True) as txn:
            if not txn.stat()['entries']:
                for review in tqdm(self._iter_file('review.json')):
                    # Store the review
                    txn.put(
                        review['review_id'].encode(),
                        json.dumps(review).encode()
                    )

                    # Update item reviews index (store only review_ids)
                    item_review_ids = json.loads(txn.get(f"item_{review['item_id']}".encode()) or '[]')
                    item_review_ids.append(review['review_id'])
                    txn.put(
                        f"item_{review['item_id']}".encode(),
                        json.dumps(item_review_ids).encode()
                    )

                    # Update user reviews index (store only review_ids)
                    user_review_ids = json.loads(txn.get(f"user_{review['user_id']}".encode()) or '[]')
                    user_review_ids.append(review['review_id'])
                    txn.put(
                        f"user_{review['user_id']}".encode(),
                        json.dumps(user_review_ids).encode()
                    )

    def _iter_file(self, filename: str) -> Iterator[Dict]:
        """Iterate through file line by line."""
        file_path = os.path.join(self.data_dir, filename)
        with open(file_path, 'r', encoding='utf-8') as file:
            for line in file:
                yield json.loads(line)

    def get_user(self, user_id: str) -> Optional[Dict]:
        """Fetch user data based on user_id."""
        with self.user_env.begin() as txn:
            user_data = txn.get(user_id.encode())
            if user_data:
                return json.loads(user_data)
        return None

    def get_item(self, item_id: str) -> Optional[Dict]:
        """Fetch item data based on item_id."""
        if not item_id:
            return None

        with self.item_env.begin() as txn:
            item_data = txn.get(item_id.encode())
            if item_data:
                return json.loads(item_data)
        return None

    def get_reviews(
            self,
            item_id: Optional[str] = None,
            user_id: Optional[str] = None,
            review_id: Optional[str] = None
    ) -> List[Dict]:
        """Fetch reviews filtered by various parameters."""
        if review_id:
            with self.review_env.begin() as txn:
                review_data = txn.get(review_id.encode())
                if review_data:
                    return [json.loads(review_data)]
            return []

        with self.review_env.begin() as txn:
            if item_id:
                review_ids = json.loads(txn.get(f"item_{item_id}".encode()) or '[]')
            elif user_id:
                review_ids = json.loads(txn.get(f"user_{user_id}".encode()) or '[]')
            else:
                return []

            # Fetch complete review data for each review_id
            reviews = []
            for rid in review_ids:
                review_data = txn.get(rid.encode())
                if review_data:
                    reviews.append(json.loads(review_data))
            return reviews

    def __del__(self):
        """Cleanup LMDB environments on object destruction."""
        self.user_env.close()
        self.item_env.close()
        self.review_env.close()
```

---

