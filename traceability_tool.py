import networkx as nx
import pandas as pd
import matplotlib.pyplot as plt
import textwrap

def build_requirements_graph():
    """
    Constructs the directed graph based on the user's specific requirement hierarchy.
    """
    G = nx.DiGraph()

    # 1. Define Parent-Child (Derivation) Relationships
    derivations = {
        'Req 1': ['Req 1.1', 'Req 1.2', 'Req 1.3', 'Req 1.4'],
        'Req 2': ['Req 2.1', 'Req 2.2'],
        'Req 3': ['Req 3.1', 'Req 3.2', 'Req 3.3', 'Req 3.4', 'Req 3.5', 'Req 3.6', 'Req 3.7', 'Req 3.8'],
        'Req 4': ['Req 4.1'],
        'Req 5': ['Req 5.1', 'Req 5.2', 'Req 5.3', 'Req 5.4', 'Req 5.5'],
        'Req 6': ['Req 6.1', 'Req 6.2', 'Req 6.3', 'Req 6.4']
    }

    # Add derivation edges
    for parent, children in derivations.items():
        for child in children:
            G.add_edge(parent, child, type='derived')

    # 2. Define High-Level Dependencies
    # Provider -> Dependent
    dependencies = [
        ('Req 1', 'Req 3'), # 3 depends on 1
        ('Req 3', 'Req 4'), # 4 depends on 3
        ('Req 1', 'Req 6'), # 6 depends on 1
        ('Req 2', 'Req 5')  # 5 depends on 2
    ]

    # Add dependency edges
    for provider, dependent in dependencies:
        G.add_edge(provider, dependent, type='dependency')

    return G

def plot_organized_table(G):
    """
    Visual 1: A Hierarchical Table (Only Parents get rows).
    """
    # We only want to create rows for the Top Level requirements
    parents = ['Req 1', 'Req 2', 'Req 3', 'Req 4', 'Req 5', 'Req 6']
    
    table_data = []

    for p in parents:
        # 1. Get Sub-Requirements
        # We sort them so they appear in order (1.1, 1.2...)
        children = sorted([n for n in G.successors(p) if G[p][n]['type'] == 'derived'])
        # We wrap the text so it doesn't make the table too wide
        children_str = "\n".join(textwrap.wrap(", ".join(children), width=30)) if children else "-"

        # 2. Get Dependencies (Who does P need?)
        upstream = [n for n in G.predecessors(p) if G[n][p]['type'] == 'dependency']
        upstream_str = "\n".join(upstream) if upstream else "None"

        # 3. Get Impacts (Who needs P?)
        downstream = [n for n in G.successors(p) if G[p][n]['type'] == 'dependency']
        downstream_str = "\n".join(downstream) if downstream else "None"

        table_data.append([p, children_str, upstream_str, downstream_str])

    # Define Column Names
    columns = ["Parent Req", "Sub-Requirements", "Depends On\n(Input)", "Impacts\n(Output)"]
    
    # Create the Plot
    fig, ax = plt.subplots(figsize=(12, 8)) 
    ax.axis('tight')
    ax.axis('off')
    
    # Draw Table
    # colWidths controls how wide the columns are. 
    # We give more space (0.4) to the Sub-Requirements column.
    table = ax.table(cellText=table_data, colLabels=columns, cellLoc='left', loc='center', 
                     colWidths=[0.15, 0.45, 0.2, 0.2])
    
    # Styling
    table.auto_set_font_size(False)
    table.set_fontsize(11)
    table.scale(1, 4) # This stretches the row height so lines don't overlap
    
    # Color Styling
    for (row, col), cell in table.get_celld().items():
        if row == 0:
            cell.set_text_props(weight='bold', color='white')
            cell.set_facecolor('#003366') # Professional Dark Blue
            cell.set_height(0.1)
        else:
            # Alternating row colors for readability
            if row % 2 == 0:
                cell.set_facecolor('#f2f2f2')
            else:
                cell.set_facecolor('white')
            
            # Add some padding logic by adjusting height
            cell.set_text_props(verticalalignment='center')

    plt.title("Requirement Traceability Matrix (RTM)", fontsize=16, weight='bold', y=0.98)
    plt.show()

def perform_impact_analysis(G, changed_reqs):
    """
    Visual 2: The Network Graph (Unchanged)
    """
    impacted_nodes = set()
    for req in changed_reqs:
        impacted_nodes.add(req)
        descendants = nx.descendants(G, req)
        impacted_nodes.update(descendants)

    color_map = []
    for node in G.nodes():
        if node in changed_reqs:
            color_map.append('#ff4d4d') 
        elif node in impacted_nodes:
            color_map.append('#ffcc00') 
        else:
            color_map.append('#e6e6e6') 

    plt.figure(figsize=(14, 10))
    pos = nx.spring_layout(G, seed=42, k=0.9) 
    
    nx.draw(G, pos, node_color=color_map, with_labels=True, 
            node_size=2500, font_size=9, font_weight='bold', 
            edge_color='gray', arrows=True)
    
    legend_elements = [
        plt.Line2D([0], [0], marker='o', color='w', markerfacecolor='#ff4d4d', markersize=15, label='Changed Req'),
        plt.Line2D([0], [0], marker='o', color='w', markerfacecolor='#ffcc00', markersize=15, label='Impacted Risk'),
        plt.Line2D([0], [0], marker='o', color='w', markerfacecolor='#e6e6e6', markersize=15, label='Safe')
    ]
    plt.legend(handles=legend_elements, loc='upper left')
    
    plt.title(f"Impact Analysis Simulation: Changing {', '.join(changed_reqs)}", fontsize=16)
    plt.show()

# --- EXECUTION ---
if __name__ == "__main__":
    req_graph = build_requirements_graph()
    
    print("Generating Traceability Table...")
    plot_organized_table(req_graph)

    change_scenario = ['Req 1', 'Req 3']
    print(f"Simulating change in: {change_scenario}")
    
    perform_impact_analysis(req_graph, change_scenario)
