import os
import logging
from websocietysimulator import Simulator

# 載入我們的 CrewAI 轉接層
from crewai_simulation_agent import CrewAISimulationAgent

logging.basicConfig(level=logging.INFO)

# ======================================================================
# [第一步] 設定您的 LLM API Key
# ======================================================================
# ⚠️【重要】CrewAI 架構下，LLM 是「必須的」，但設定方式與官方不同：
#   - 官方寫法: simulator.set_llm(DeepseekLLM(api_key="..."))
#   - CrewAI 寫法: 透過「環境變數」提供 API Key，CrewAI 會自動抓取
#
# 使用 dotenv 從 .env 讀取真實的 API Key
from dotenv import load_dotenv
load_dotenv()

# 💡 您也可以在 config/agents.yaml 裡為每個 Agent 指定不同模型，
#    例如 llm: deepseek/deepseek-chat 或 llm: openai/gpt-4o

print("🚀 啟動 CrewAI 真實訓練集大規模評測")

# ======================================================================
# [第二步] 指向真實的龐大 Dataset 與任務路徑
# ======================================================================
# 💡 注意: 建議保留 cache=True，否則 16GB+ 的資料表會瞬間吃滿您的本機記憶體！
DATA_DIR        = "data"               # Your 38-user local subset
TASK_DIR        = "real_tasks_842"     # ✅ 842 verified tasks (user+item guaranteed in data/)
GROUNDTRUTH_DIR = "real_groundtruth_842" # ✅ Matching ground truth

simulator = Simulator(data_dir=DATA_DIR, device="auto", cache=True)
simulator.set_task_and_groundtruth(task_dir=TASK_DIR, groundtruth_dir=GROUNDTRUTH_DIR)

# ======================================================================
# [第三步] 掛載轉接器 (不需要 simulator.set_llm()!)
# ======================================================================
simulator.set_agent(CrewAISimulationAgent)
# ⚠️ 不需要呼叫 simulator.set_llm(...)！
# 在 CrewAI 架構下，LLM 由 CrewAI Agent 內部自行管理，
# 而非由 Simulator 統一分發。API Key 已在第一步透過環境變數提供。

# ======================================================================
# [第四步] 啟動多執行緒全速評測  ⚡️
# ======================================================================
# 💡 注意: 同時併發多個 Flow 會以 N 倍的速度消耗您的 Token Rate Limit (TPM/RPM)，
# 如果遇到 HTTP 429 Too Many Requests 報錯，請把 max_workers 降低。
outputs = simulator.run_simulation(
    number_of_tasks=10,       # None 代表跑完資料夾內所有任務
    enable_threading=False,      # 關閉多執行緒並發以避免 429 Rate Limit Error
    max_workers=1              # 降為單執行緒
)

# ======================================================================
# [第五步] 產生成績單
# ======================================================================
print("\n📊 呼叫官方評分系統 (simulator.evaluate())...")
evaluation_results = simulator.evaluate()

import json
print("\n💡 最終競賽衡量結果:")
print(json.dumps(evaluation_results, indent=2, ensure_ascii=False))
