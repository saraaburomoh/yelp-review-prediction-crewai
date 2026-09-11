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
