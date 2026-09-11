import os
import requests
import json
from crewai import Agent, Crew, Process, Task, LLM
from crewai.project import CrewBase, agent, crew, task, llm
from crewai.tools import tool
from langchain_openai import ChatOpenAI

# 根據目錄結構加載自訂的工具層
from src.tools.interaction_tool_wrapper import get_interaction_tool

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
        
        snippets = []
        if "organic" in results:
            for result in results["organic"][:3]: 
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

@tool("get_background_knowledge")
def get_background_knowledge(query: Any = None) -> str:
    """Useful to get background knowledge about the Yelp dataset format and mappings. 
    Accepts any string query and returns the relevant data translation documentation."""
    return load_knowledge()

@CrewBase
class SimulationCrewHierarchical():
    """Hierarchical Simulation Crew for generating user review simulation"""
    
    agents_config = '../../config/agents.yaml'
    tasks_config = '../../config/tasks.yaml'

    @llm
    def simulation_llm(self) -> LLM:
        """Shared LLM configuration for all agents."""
        return LLM(
            model=f"openai/{os.environ.get('NVIDIA_MODEL_NAME')}",
            base_url=os.environ.get("NVIDIA_API_BASE"),
            api_key=os.environ.get("NVIDIA_API_KEY")
        )

    @agent
    def user_analyst(self) -> Agent:
        return Agent(
            config=self.agents_config['user_analyst'],
            verbose=True,
            tools=[get_interaction_tool(), get_background_knowledge],
            llm=self.simulation_llm(),
            max_iter=5
        )

    @agent
    def item_analyst(self) -> Agent:
        return Agent(
            config=self.agents_config['item_analyst'],
            verbose=True,
            tools=[get_interaction_tool(), get_background_knowledge],
            llm=self.simulation_llm(),
            max_iter=5
        )

    @agent
    def web_researcher(self) -> Agent:
        return Agent(
            config=self.agents_config['web_researcher'],
            tools=[serper_search_tool],
            verbose=True,
            llm=self.simulation_llm(),
            max_iter=3
        )

    @agent
    def prediction_modeler(self) -> Agent:
        return Agent(
            config=self.agents_config['prediction_modeler'],
            tools=[get_background_knowledge],
            verbose=True,
            llm=self.simulation_llm(),
            max_iter=5
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
            config=self.tasks_config['web_research_task']
        )

    @task
    def predict_review_task(self) -> Task:
        return Task(
            config=self.tasks_config['predict_review_task']
        )

    @crew
    def crew(self) -> Crew:        return Crew(
            agents=self.agents, 
            tasks=self.tasks,
            process=Process.hierarchical, 
            manager_llm=self.simulation_llm(),
            max_rpm=2,
            verbose=True
        )
