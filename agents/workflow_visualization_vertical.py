import memory
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

# Vibe coded... use with care!

def get_data(record, keys:list):
    return [record.get(key, None) for key in keys]

def visualize_workflow_vertical(app, username, session_id):
    data = memory.SessionMemory(app_name=app).get_full_session(session_id, username)
    keys = ["source", "user_content", "agent_response", "timestamp","agent_content", "calling_agent"]
    events = []
    last_label = None
    for record in data:
        source, user_content, agent_response, timestamp, agent_content, calling_agent = get_data(record, keys)
        label = source if source else ""
        show_label = False
        if label and label != last_label:
            show_label = True
            last_label = label
        label_to_show = label if show_label else ""
        if calling_agent:
            content = agent_content if agent_content else user_content if user_content else '(no content)'
            events.append((timestamp, 'AgentCaller', content, label_to_show))
        elif user_content:
            events.append((timestamp, 'User', user_content, label_to_show))
        if source:
            events.append((timestamp, 'Tool', source, label_to_show))
        if agent_response:
            events.append((timestamp, 'Agent', agent_response, label_to_show))
    events.sort(key=lambda x: x[0])
    # Vibe coded... use with care!

    # Add more vertical space between events
    vertical_gap = 1.2
    fig, ax = plt.subplots(figsize=(5, max(3, len(events)*vertical_gap)))
    x_map = {'User': 2, 'AgentCaller': 1.5, 'Tool': 1, 'Agent': 0}
    color_map = {'User': '#0078d7', 'AgentCaller': '#a259e6', 'Tool': '#f4b400', 'Agent': '#34a853'}
    label_map = {'User': 'Human', 'AgentCaller': 'Agent→Agent', 'Tool': 'Tool', 'Agent': 'Agent'}
    points = []
    for i, (timestamp, role, text, label) in enumerate(events):
        y = -i * vertical_gap
        x = x_map[role]
        points.append((x, y))
        ax.scatter(x, y, color=color_map[role], s=220, zorder=3)
        # Source label display removed
        ax.text(x+0.18, y, label_map[role], ha='left', va='center', fontsize=10, fontweight='bold')
        ax.text(x-0.05, y-0.35, str(text)[:60]+('...' if len(str(text))>60 else ''), ha='left', va='top', fontsize=9, color='#444')

    # Draw arrows between points to show flow
    for i in range(len(points)-1):
        x0, y0 = points[i]
        x1, y1 = points[i+1]
        ax.annotate('', xy=(x1, y1), xytext=(x0, y0),
                    arrowprops=dict(arrowstyle='->', color='#888', lw=2, shrinkA=12, shrinkB=12),
                    zorder=2)
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
