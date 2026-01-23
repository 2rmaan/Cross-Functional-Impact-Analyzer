import networkx as nx
import pandas as pd
import matplotlib.pyplot as plt
import textwrap

def build_requirements_graph():
    G = nx.DiGraph()
    derivations = {
        'Req 1': ['Req 1.1', 'Req 1.2', 'Req 1.3', 'Req 1.4'],
        'Req 2': ['Req 2.1', 'Req 2.2'],
        'Req 3': ['Req 3.1', 'Req 3.2', 'Req 3.3', 'Req 3.4', 'Req 3.5', 'Req 3.6', 'Req 3.7', 'Req 3.8'],
        'Req 4': ['Req 4.1'],
        'Req 5': ['Req 5.1', 'Req 5.2', 'Req 5.3', 'Req 5.4', 'Req 5.5'],
        'Req 6': ['Req 6.1', 'Req 6.2', 'Req 6.3', 'Req 6.4']
    }
    for parent, children in derivations.items():
        for child in children:
            G.add_edge(parent, child, type='derived')

    dependencies = [
        ('Req 1', 'Req 3'),
        ('Req 3', 'Req 4'),
        ('Req 1', 'Req 6'),
        ('Req 2', 'Req 5')
    ]
    for provider, dependent in dependencies:
        G.add_edge(provider, dependent, type='dependency')
    return G

def plot_organized_table(G):
    parents = ['Req 1', 'Req 2', 'Req 3', 'Req 4', 'Req 5', 'Req 6']
    table_data = []

    for p in parents:
        children = sorted([n for n in G.successors(p) if G[p][n]['type'] == 'derived'])
        children_str = "\n".join(textwrap.wrap(", ".join(children), width=30)) if children else "-"
        upstream = [n for n in G.predecessors(p) if G[n][p]['type'] == 'dependency']
        upstream_str = "\n".join(upstream) if upstream else "None"
        downstream = [n for n in G.successors(p) if G[p][n]['type'] == 'dependency']
        downstream_str = "\n".join(downstream) if downstream else "None"
        table_data.append([p, children_str, upstream_str, downstream_str])

    columns = ["Parent Req", "Sub-Requirements", "Depends On\n(Input)", "Impacts\n(Output)"]
    fig, ax = plt.subplots(figsize=(12, 8)) 
    ax.axis('tight')
    ax.axis('off')
    
    table = ax.table(cellText=table_data, colLabels=columns, cellLoc='left', loc='center', colWidths=[0.15, 0.45, 0.2, 0.2])
    table.auto_set_font_size(False)
    table.set_fontsize(11)
    table.scale(1, 4)
    
    for (row, col), cell in table.get_celld().items():
        if row == 0:
            cell.set_text_props(weight='bold', color='white')
            cell.set_facecolor('#003366')
            cell.set_height(0.1)
        else:
            if row % 2 == 0: cell.set_facecolor('#f2f2f2')
            else: cell.set_facecolor('white')
            cell.set_text_props(verticalalignment='center')

    plt.title("Requirement Traceability Matrix (RTM)", fontsize=16, weight='bold', y=0.98)
    # SAVE THE IMAGE
    plt.savefig('traceability_table.png', bbox_inches='tight', dpi=300)
    print("Saved traceability_table.png")
    plt.show()

def perform_impact_analysis(G, changed_reqs):
    impacted_nodes = set()
    for req in changed_reqs:
        impacted_nodes.add(req)
        descendants = nx.descendants(G, req)
        impacted_nodes.update(descendants)

    color_map = []
    for node in G.nodes():
        if node in changed_reqs: color_map.append('#ff4d4d') 
        elif node in impacted_nodes: color_map.append('#ffcc00') 
        else: color_map.append('#e6e6e6') 

    plt.figure(figsize=(14, 10))
    pos = nx.spring_layout(G, seed=42, k=0.9) 
    nx.draw(G, pos, node_color=color_map, with_labels=True, node_size=2500, font_size=9, font_weight='bold', edge_color='gray', arrows=True)
    
    legend_elements = [
        plt.Line2D([0], [0], marker='o', color='w', markerfacecolor='#ff4d4d', markersize=15, label='Changed Req'),
        plt.Line2D([0], [0], marker='o', color='w', markerfacecolor='#ffcc00', markersize=15, label='Impacted Risk'),
        plt.Line2D([0], [0], marker='o', color='w', markerfacecolor='#e6e6e6', markersize=15, label='Safe')
    ]
    plt.legend(handles=legend_elements, loc='upper left')
    
    plt.title(f"Impact Analysis Simulation: Changing {', '.join(changed_reqs)}", fontsize=16)
    # SAVE THE IMAGE
    plt.savefig('impact_analysis.png', bbox_inches='tight', dpi=300)
    print("Saved impact_analysis.png")
    plt.show()

if __name__ == "__main__":
    req_graph = build_requirements_graph()
    plot_organized_table(req_graph)
    change_scenario = ['Req 1', 'Req 3']
    perform_impact_analysis(req_graph, change_scenario)
