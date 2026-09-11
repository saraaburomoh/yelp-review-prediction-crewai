import sys
import os

# Append current working dir to sys path so absolute imports like 'src.flows...' work seamlessly
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.append(current_dir)

from websocietysimulator.agent import SimulationAgent
from src.flows.serving_flow import AgentSocietyServingFlow, InferenceState
from src.tools.interaction_tool_wrapper import inject_simulator_tool

class CrewAISimulationAgent(SimulationAgent):
    """
    Adapter connecting AgentSociety's simulator framework to the CrewAI flow.
    """
    def __init__(self, llm=None, *args, **kwargs):
        # llm is unused — CrewAI manages its own LLM via env vars (OPENAI_API_KEY / OPENAI_API_BASE)
        super().__init__(llm=llm, *args, **kwargs)

    def workflow(self):
        # 1. 解析官方 Simulator 給予的任務與上下文
        def get_val(obj, key, default=''):
            if isinstance(obj, dict):
                return obj.get(key, default)
            return getattr(obj, key, default)

        # DEBUG: Print the task structure
        print(f"DEBUG: Processing task: {self.task}", flush=True)

        current_user_id = get_val(self.task, 'user_id')
        current_item_id = get_val(self.task, 'item_id')

        # 2. 將官方提供的 interaction_tool 動態注入到全局模組，令 CrewAI Tool Wrapper 可以查資料
        inject_simulator_tool(getattr(self, 'interaction_tool', None))
        
        # 3. 初始化 InferenceState，並掛載給我們定義好的 CrewAI Serving Flow
        initial_state = InferenceState(
            user_id=current_user_id,
            item_id=current_item_id
        )
        
        # 4. 實例化並觸發 CrewAI 引擎
        import time
        # Defensive sleep to avoid hitting rate limits too aggressively between sequential tasks
        if os.environ.get("OPENAI_API_KEY") != "sk-mock-key":
            time.sleep(60)
        
        flow = AgentSocietyServingFlow()
        flow.state.user_id = current_user_id
        flow.state.item_id = current_item_id
        
        try:
            final_state_dict = flow.kickoff()
        except Exception as e:
            print(f"ERROR: Flow execution failed: {str(e)}")
            final_state_dict = None
        
        # 5. 按照 AgentSociety Track 1 要求，回傳 dictionary
        # Handle case where final_state_dict is None (e.g., total failure or 429)
        if final_state_dict is None:
            return {
                'stars': 4.0,
                'review': "The simulation failed to complete due to an external error."
            }
            
        return {
            'stars': float(final_state_dict.get('predicted_rating', 4.0)),
            'review': str(final_state_dict.get('generated_review', 'Good.'))
        }
