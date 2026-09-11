import os

files_to_add = [
    r"c:\Users\MCC\Rag_Crew_Profiler\openevolve\AgentSocietyChallenge_OpenEvolve\websocietysimulator\tools\cache_interaction_tool.py"
]
output_file = r"c:\Users\MCC\Rag_Crew_Profiler\openevolve\FINAL_PROJECT_CODE_DUMP.md"

with open(output_file, "a", encoding="utf-8") as out_f:
    for file_to_add in files_to_add:
        if os.path.exists(file_to_add):
            with open(file_to_add, "r", encoding="utf-8", errors="replace") as in_f:
                content = in_f.read()
            out_f.write(f"# File: {os.path.basename(file_to_add)}\n")
            out_f.write(f"Path: `{file_to_add}`\n\n")
            ext = os.path.splitext(file_to_add)[1].replace(".", "")
            if ext == "":
                ext = "text"
            out_f.write(f"```{ext}\n")
            out_f.write(content)
            if not content.endswith("\n"):
                out_f.write("\n")
            out_f.write("```\n\n")
            out_f.write("---\n\n")
            print(f"Successfully appended {os.path.basename(file_to_add)}")
        else:
            print(f"File not found: {file_to_add}")
