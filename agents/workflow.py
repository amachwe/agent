import memory

app = "stock_analysis_app"
username = "user1"
session_id = "session_1758406385903"
data = memory.SessionMemory(app_name=app).get_full_session( session_id, username)

for record in data:
    print(record["source"], record.get("interaction_start", False), record.get("interaction_end", False), record["timestamp"])
