import memory
import workflow_visualization_vertical

def get_data(record, keys:list):
    return [record.get(key, None) for key in keys]

app = "stock_agents_app"
username = "user1"
session_id = "session_1760298043431"
data = memory.SessionMemory(app_name=app).get_full_session(session_id, username)

keys = ["source", "interaction_start", "interaction_end", "agent_response", "user_content", "timestamp", "agent_content", "calling_agent", "seq"]
workflow_visualization_vertical.visualize_workflow_vertical(app, username, session_id)

# Sort by timestamp and then by seq if available
def sort_key(record):
    ts = record.get("timestamp")
    seq = record.get("seq", 0)
    return (ts, seq)

for record in sorted(data, key=sort_key):
    # Show start of interaction
    if record.get("interaction_start") and not record.get("calling_agent"):
        print("--- Human Interaction Start ---")
        print("User input:", record.get("user_content"))
    # Show agent-to-agent start
    if record.get("interaction_start") and record.get("calling_agent"):
        print(f"--- Agent-to-Agent Start (Caller: {record.get('calling_agent')}) ---")
        print("Agent input:", record.get("agent_content"))
    # Show end of interaction (human receives output)
    if record.get("interaction_end") and not record.get("calling_agent"):
        print("--- Human Interaction End ---")
        print("Agent output to user:", record.get("agent_response"))
    # Show agent-to-agent end
    if record.get("interaction_end") and record.get("calling_agent"):
        print(f"--- Agent-to-Agent End (Caller: {record.get('calling_agent')}) ---")
        print("Agent output:", record.get("agent_response"))
