import networkx as nx
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

def build_requirements_graph():
    """
    Constructs the directed graph based on the user's specific requirement hierarchy.
    """
    G = nx.DiGraph()

    # 1. Define Parent-Child (Derivation) Relationships
    # Structure: Parent: [Children]
    derivations = {
        'Req 1': ['Req 1.1', 'Req 1.2', 'Req 1.3', 'Req 1.4'],
        'Req 2': ['Req 2.1', 'Req 2.2'],
        'Req 3': ['Req 3.1', 'Req 3.2', 'Req 3.3', 'Req 3.4', 'Req 3.5', 'Req 3.6', 'Req 3.7', 'Req 3.8'],
        'Req 4': ['Req 4.1'],
        'Req 5': ['Req 5.1', 'Req 5.2', 'Req 5.3', 'Req 5.4', 'Req 5.5'],
        'Req 6': ['Req 6.1', 'Req 6.2', 'Req 6.3', 'Req 6.4']
    }

    # Add derivation edges (Parent -> Child)
    for parent, children in derivations.items():
        for child in children:
            G.add_edge(parent, child, type='derived')

    # 2. Define High-Level Dependencies (Parent to Parent)
    # Structure: Provider -> Dependent (If Provider changes, Dependent is impacted)
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

def plot_traceability_matrix(G):
    """
    Visual 1: A traditional Traceability Matrix (Heatmap style).
    """
    nodes = sorted(list(G.nodes()))
    matrix_data = []

    for source in nodes:
        row = []
        for target in nodes:
            if source == target:
                row.append(1) # Self
            elif G.has_edge(source, target):
                row.append(1) # Direct connection
            elif nx.has_path(G, source, target):
                row.append(0.5) # Indirect connection
            else:
                row.append(0) # No connection
        matrix_data.append(row)

    df = pd.DataFrame(matrix_data, index=nodes, columns=nodes)

    plt.figure(figsize=(12, 10))
    sns.heatmap(df, cmap="Blues", cbar=False, linewidths=.5, linecolor='gray')
    plt.title("Requirement Traceability Matrix\n(Dark = Direct, Light = Indirect)", fontsize=16)
    plt.tight_layout()
    plt.show()

def perform_impact_analysis(G, changed_reqs):
    """
    Visual 2: Network Graph highlighting the 'Blast Radius' of the change.
    """
    # 1. Identify all impacted nodes (downstream)
    impacted_nodes = set()
    for req in changed_reqs:
        impacted_nodes.add(req)
        # Get all descendants (everything that flows FROM this node)
        descendants = nx.descendants(G, req)
        impacted_nodes.update(descendants)

    # 2. Set Colors
    color_map = []
    for node in G.nodes():
        if node in changed_reqs:
            color_map.append('red') # The Root Cause
        elif node in impacted_nodes:
            color_map.append('orange') # The Impacted Area
        else:
            color_map.append('lightgrey') # Safe

    # 3. Visualize
    plt.figure(figsize=(14, 10))
    pos = nx.spring_layout(G, seed=42, k=0.8) # k regulates distance between nodes
    
    # Draw graph
    nx.draw(G, pos, node_color=color_map, with_labels=True, 
            node_size=2500, font_size=9, font_weight='bold', 
            edge_color='gray', arrows=True)
    
    # Legend
    legend_elements = [
        plt.Line2D([0], [0], marker='o', color='w', markerfacecolor='red', markersize=15, label='Changed Requirement'),
        plt.Line2D([0], [0], marker='o', color='w', markerfacecolor='orange', markersize=15, label='Impacted (Risk)'),
        plt.Line2D([0], [0], marker='o', color='w', markerfacecolor='lightgrey', markersize=15, label='No Impact')
    ]
    plt.legend(handles=legend_elements, loc='upper left')
    
    plt.title(f"Impact Analysis Simulation: Changing {', '.join(changed_reqs)}", fontsize=16)
    plt.show()
    
    return impacted_nodes

# --- EXECUTION ---
if __name__ == "__main__":
    # 1. Build the Data Structure
    req_graph = build_requirements_graph()
    
    # 2. Show the Static Matrix (The Documentation View)
    print("Generating Traceability Matrix...")
    plot_traceability_matrix(req_graph)

    # 3. Simulate the Change (The Analysis View)
    # User scenario: Change in Req 3 and Req 1
    change_scenario = ['Req 1', 'Req 3']
    print(f"Simulating change in: {change_scenario}")
    
    affected = perform_impact_analysis(req_graph, change_scenario)
    
    print(f"\nTotal Requirements Affected: {len(affected)}")
    print(f"List of impacted requirements: {sorted(list(affected))}")