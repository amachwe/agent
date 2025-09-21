import memory
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

def get_data(record, keys:list):
    return [record.get(key, None) for key in keys]

def visualize_workflow_vertical(app, username, session_id):
    data = memory.SessionMemory(app_name=app).get_full_session(session_id, username)
    keys = ["source", "user_content", "agent_response", "timestamp","agent_content", "calling_agent"]
    events = []
    for record in data:
        source, user_content, agent_response, timestamp, agent_content, calling_agent = get_data(record, keys)
        # If calling_agent is set, always show as Agent→Agent (even if agent_content is empty)
        if calling_agent:
            content = agent_content if agent_content else user_content if user_content else '(no content)'
            events.append((timestamp, 'AgentCaller', content))
        elif user_content:
            events.append((timestamp, 'User', user_content))
        if source:
            events.append((timestamp, 'Tool', source))
        if agent_response:
            events.append((timestamp, 'Agent', agent_response))
    events.sort(key=lambda x: x[0])

    # Add more vertical space between events
    vertical_gap = 1.2
    fig, ax = plt.subplots(figsize=(5, max(3, len(events)*vertical_gap)))
    x_map = {'User': 2, 'AgentCaller': 1.5, 'Tool': 1, 'Agent': 0}
    color_map = {'User': '#0078d7', 'AgentCaller': '#a259e6', 'Tool': '#f4b400', 'Agent': '#34a853'}
    label_map = {'User': 'Human', 'AgentCaller': 'Agent→Agent', 'Tool': 'Tool', 'Agent': 'Agent'}
    for i, (timestamp, role, text) in enumerate(events):
        y = -i * vertical_gap
        ax.scatter(x_map[role], y, color=color_map[role], s=220, zorder=3)
        ax.text(x_map[role]+0.18, y, label_map[role], ha='left', va='center', fontsize=10, fontweight='bold')
        ax.text(x_map[role]-0.05, y-0.35, str(text)[:60]+('...' if len(str(text))>60 else ''), ha='left', va='top', fontsize=9, color='#444')
    ax.set_xticks([0,1,1.5,2])
    ax.set_xticklabels(['Agent', 'Tool', 'Agent→Agent', 'Human'])
    ax.set_yticks([])
    ax.set_title(f"Session Sequence: {session_id}")
    ax.set_ylim(-len(events)*vertical_gap+0.5, 1)
    ax.set_xlim(-0.7, 2.9)
    ax.grid(axis='x', linestyle='--', alpha=0.3)
    legend_handles = [mpatches.Patch(color=color_map[r], label=label_map[r]) for r in x_map]
    ax.legend(handles=legend_handles, loc='upper right')
    plt.subplots_adjust(left=0.18, right=0.98, top=0.92, bottom=0.08)
    plt.show()

# Example usage:
# visualize_workflow_vertical('stock_analysis_app', 'user1', 'session_1758480329938')
