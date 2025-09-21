import memory
import workflow_visualization_vertical

def get_data(record, keys:list):
    return [record.get(key, None) for key in keys]

app = "stock_analysis_app"
username = "user1"
session_id = "session_1758481650757" 
data = memory.SessionMemory(app_name=app).get_full_session( session_id, username)

keys = ["source", "interaction_start", "interaction_end", "agent_response", "user_content", "timestamp","agent_content", "calling_agent"]
workflow_visualization_vertical.visualize_workflow_vertical(app, username, session_id)

for record in data:
    print(get_data(record, keys))
