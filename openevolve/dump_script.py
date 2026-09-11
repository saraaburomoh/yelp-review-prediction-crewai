import os

files_to_dump = [
    r"c:\Users\MCC\Rag_Crew_Profiler\openevolve\AgentSocietyChallenge_OpenEvolve\config\agents_evolving.yaml",
    r"c:\Users\MCC\Rag_Crew_Profiler\openevolve\AgentSocietyChallenge_OpenEvolve\config\tasks.yaml",
    r"c:\Users\MCC\Rag_Crew_Profiler\openevolve\AgentSocietyChallenge_OpenEvolve\config\tasks_evolving.yaml",
    r"c:\Users\MCC\Rag_Crew_Profiler\openevolve\AgentSocietyChallenge_OpenEvolve\config\openevolve_tasks_config.yaml",
    r"c:\Users\MCC\Rag_Crew_Profiler\openevolve\AgentSocietyChallenge_OpenEvolve\src\flows\serving_flow.py",
    r"c:\Users\MCC\Rag_Crew_Profiler\openevolve\AgentSocietyChallenge_OpenEvolve\src\crews\simulation_crew.py",
    r"c:\Users\MCC\Rag_Crew_Profiler\openevolve\AgentSocietyChallenge_OpenEvolve\src\tools\interaction_tool_wrapper.py",
    r"c:\Users\MCC\Rag_Crew_Profiler\openevolve\AgentSocietyChallenge_OpenEvolve\websocietysimulator\simulator.py",
    r"c:\Users\MCC\Rag_Crew_Profiler\openevolve\AgentSocietyChallenge_OpenEvolve\openevolve_evaluator.py",
    r"c:\Users\MCC\Rag_Crew_Profiler\openevolve\LAB 14 DONE - OPENEVOLVE",
    r"c:\Users\MCC\Rag_Crew_Profiler\openevolve\LAB 16 TODAY IMPORTANT",
    r"c:\Users\MCC\Rag_Crew_Profiler\openevolve\AgentSocietyChallenge_OpenEvolve\dummy_tasks\task_1.json",
    r"c:\Users\MCC\Rag_Crew_Profiler\openevolve\AgentSocietyChallenge_OpenEvolve\dummy_groundtruth\groundtruth_1.json"
]

output_file = r"c:\Users\MCC\Rag_Crew_Profiler\openevolve\FINAL_PROJECT_CODE_DUMP.md"

with open(output_file, "w", encoding="utf-8") as out_f:
    for file_path in files_to_dump:
        if os.path.exists(file_path):
            with open(file_path, "r", encoding="utf-8", errors="replace") as in_f:
                content = in_f.read()
            out_f.write(f"# File: {os.path.basename(file_path)}\n")
            out_f.write(f"Path: `{file_path}`\n\n")
            ext = os.path.splitext(file_path)[1].replace(".", "")
            if ext == "":
                ext = "text"
            out_f.write(f"```{ext}\n")
            out_f.write(content)
            if not content.endswith("\n"):
                out_f.write("\n")
            out_f.write("```\n\n")
            out_f.write("---\n\n")
        else:
            out_f.write(f"# File: {os.path.basename(file_path)}\n")
            out_f.write(f"Path: `{file_path}`\n\n")
            out_f.write("```text\n")
            out_f.write(f"File not found: {file_path}\n")
            out_f.write("```\n\n")
            out_f.write("---\n\n")
            
print(f"Dumped to {output_file}")
