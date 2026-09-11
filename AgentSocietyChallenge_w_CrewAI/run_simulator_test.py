"""
run_simulator_test.py — AgentSociety + CrewAI 整合測試腳本
支援兩種模式：
  1. 真實 LLM 模式 (預設)：透過 NVIDIA NIM API 進行推論
  2. Mock 模式：攔截 OpenAI API 呼叫，使用假回覆進行快速結構驗證
用法：
  uv run python run_simulator_test.py              # 真實 LLM
  uv run python run_simulator_test.py --mock       # Mock 模式
"""
import sys
import os
import logging
import json
import io

# Force UTF-8 encoding for Windows terminals
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# ======================================================================
# [模式切換] Mock vs. Real LLM
# ======================================================================
USE_MOCK = "--mock" in sys.argv

if USE_MOCK:
    from unittest.mock import patch

    def fake_completion(*args, **kwargs):
        messages = kwargs.get('messages', [])
        last_msg = messages[-1]['content'] if messages else ""
        
        # Determine if it's a JSON prediction task or a profiling task
        if "stars" in last_msg or "JSON" in last_msg:
            content = 'Thought: I have enough information to predict the review.\nFinal Answer: {"stars": 4.5, "review": "[Mocked] Great experience!"}'
        else:
            content = 'Thought: I have analyzed the data.\nFinal Answer: This is a mocked analysis report.'

        class FakeMessage:
            def __init__(self, content):
                self.content = content
            tool_calls = None
            def model_dump(self, *args, **kwargs):
                return {"content": self.content, "tool_calls": None, "role": "assistant"}
        
        class FakeChoice:
            def __init__(self, content):
                self.message = FakeMessage(content)
            finish_reason = "stop"
            index = 0
            
        class FakeResponse:
            def __init__(self, content):
                self.choices = [FakeChoice(content)]
            id = "mock-id"
            model = "gpt-4"
            usage = None
            object = "chat.completion"
            created = 123456789
            def parse(self):
                return self
            def model_dump(self, *args, **kwargs):
                return {
                    "id": self.id,
                    "choices": [{"message": self.choices[0].message.model_dump(), "finish_reason": "stop", "index": 0}],
                    "created": self.created,
                    "model": self.model,
                    "object": self.object
                }
        return FakeResponse(content)

    patcher = patch('openai.resources.chat.completions.Completions.create', side_effect=fake_completion)
    patcher.start()
    os.environ["OPENAI_API_KEY"] = "sk-mock-key"
    print("Mode: Mock LLM")
else:
    from dotenv import load_dotenv
    load_dotenv()
    api_key = os.environ.get("OPENAI_API_KEY", "")
    api_base = os.environ.get("OPENAI_API_BASE", "")
    print(f"Mode: Real LLM (NVIDIA NIM)")
    print(f"API Key: {'Set' if api_key else 'Not Set'}")
    print(f"Base URL: {api_base or 'Not Set'}")

# ======================================================================
# 載入框架
# ======================================================================
from websocietysimulator import Simulator
from crewai_simulation_agent import CrewAISimulationAgent

logging.basicConfig(level=logging.INFO)

print("\n" + "=" * 60)
print("Starting AgentSociety CrewAI Integration Test (End-to-End)")
print("=" * 60)

try:
    # 1. 建立 Simulator，使用 Toy Dataset + Cache
    print(">>> Loading Toy Dataset (dummy_dataset)...")
    simulator = Simulator(data_dir="dummy_dataset", device="cpu", cache=True)
    simulator.set_task_and_groundtruth(task_dir="dummy_tasks", groundtruth_dir="dummy_groundtruth")
    simulator.set_agent(CrewAISimulationAgent)

    # 2. 運行模擬
    print("\nStarting inference...")
    outputs = simulator.run_simulation(number_of_tasks=1, enable_threading=False, max_workers=1)

    print("\nSimulation finished, final output:")
    print("-" * 60)
    print(json.dumps(outputs, indent=2, ensure_ascii=False))
    print("-" * 60)

    # 3. 官方評分
    print("\nCalling official evaluation (simulator.evaluate())...")
    evaluation_results = simulator.evaluate()
    print("Evaluation results:")
    print(json.dumps(evaluation_results, indent=2, ensure_ascii=False))

    print("\nIntegration test completed!")

except Exception as e:
    print(f"\nTest interrupted: {e}")
    import traceback
    traceback.print_exc()
