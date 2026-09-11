"""
openevolve_tasks_evaluator.py

NOVELTY: This evaluator evolves the TASK INSTRUCTIONS (tasks.yaml) rather than
the agent personas (agents.yaml). The hypothesis is that the predict_review_task
description — which defines the reasoning chain and output contract — has more
impact on performance than agent backstory alone.

OpenEvolve writes the mutated tasks YAML to a temp file and passes the path here.
We inject it into SimulationCrew via OPENEVOLVE_TASKS_YAML environment variable.
"""
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

SIM_TIMEOUT_SEC = int(os.environ.get("OPENEVOLVE_SIM_TIMEOUT", 900))

_simulator: Simulator = None

def _get_simulator() -> Simulator:
    global _simulator
    if _simulator is None:
        logging.getLogger().setLevel(logging.WARNING)
        print("[TasksEvaluator] Initializing Simulator (one-time)...")
        _simulator = Simulator(data_dir="dummy_dataset", device="cpu", cache=True)
        _simulator.set_task_and_groundtruth(
            task_dir="dummy_tasks",
            groundtruth_dir="dummy_groundtruth"
        )
        _simulator.set_agent(CrewAISimulationAgent)
        print("[TasksEvaluator] Simulator ready.")
    return _simulator


def evaluate(program_path: str) -> dict:
    """
    OpenEvolve calls this with the path to the mutated tasks YAML.

    We inject it via OPENEVOLVE_TASKS_YAML so serving_flow.py picks it up
    and passes it to SimulationCrew as the tasks_config override.

    Returns combined_score = overall_quality (0-1).
    """
    simulator = _get_simulator()
    try:
        # Inject the evolved TASKS yaml path (not agents yaml)
        os.environ["OPENEVOLVE_TASKS_YAML"] = program_path
        # Keep a stable agents.yaml (the best one from our previous run)
        os.environ["OPENEVOLVE_AGENTS_YAML"] = os.path.join(
            project_dir, "config", "agents.yaml"
        )

        num_tasks = int(os.environ.get("OPENEVOLVE_NUM_TASKS", 5))
        print(f"\n[TasksEvaluator] Running simulation: tasks={program_path}  (n={num_tasks}, timeout={SIM_TIMEOUT_SEC}s)")

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
            print(f"[TasksEvaluator] ⏱  Simulation exceeded {SIM_TIMEOUT_SEC}s — returning fallback score")
            return {"combined_score": 0.0}

        print("[TasksEvaluator] Calculating official metrics...")
        eval_results = simulator.evaluate()

        metrics           = eval_results.get("metrics", {}) if isinstance(eval_results, dict) else {}
        overall_quality   = metrics.get("overall_quality", 0.0)
        pref_estimation   = metrics.get("preference_estimation", 0.0)
        review_generation = metrics.get("review_generation", 0.0)

        print(
            f"[TasksEvaluator] pref={pref_estimation:.4f}, "
            f"review={review_generation:.4f}, "
            f"overall={overall_quality:.4f}  → combined_score={overall_quality:.4f}"
        )

        return {
            "combined_score": float(overall_quality),
            "preference_estimation": float(pref_estimation),
            "review_generation": float(review_generation),
        }

    except Exception as e:
        print(f"[TasksEvaluator] ❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return {"combined_score": 0.0}


if __name__ == "__main__":
    yaml_path = os.path.join(project_dir, "config", "tasks_evolving.yaml")
    if os.path.exists(yaml_path):
        with open(yaml_path, "r", encoding="utf-8") as f:
            content = f.read()
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False, encoding='utf-8') as tmp:
            tmp.write(content)
            tmp_path = tmp.name
        try:
            fitness = evaluate(tmp_path)
            print(f"Test completed with fitness: {fitness}")
        finally:
            os.remove(tmp_path)
