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
