import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
import numpy as np

class FeatureAnalyzer:
    def __init__(self, features_path, deps_path):
        self.features_df = pd.read_csv(features_path)
        self.deps_df = pd.read_csv(deps_path)
        self.G = self._build_graph()
        
        self.change_requests = self.features_df[
            self.features_df['Revised_Effort'] != self.features_df['Baseline_Effort']
        ]['Feature_ID'].tolist()

    def _build_graph(self):
        G = nx.DiGraph()
        for _, row in self.features_df.iterrows():
            G.add_node(row['Feature_ID'], **row.to_dict())
        for _, row in self.deps_df.iterrows():
            if row['Predecessor'] in G and row['Successor'] in G:
                G.add_edge(row['Predecessor'], row['Successor'])
        return G

    def calculate_schedule(self, effort_col):
        nodes = list(nx.topological_sort(self.G))
        start_days, end_days = {}, {}
        for node in nodes:
            preds = list(self.G.predecessors(node))
            start_days[node] = max([end_days[p] for p in preds]) if preds else 0
            end_days[node] = start_days[node] + self.G.nodes[node][effort_col]
        return start_days, end_days

    def generate_full_analysis(self):
        b_start, b_end = self.calculate_schedule('Baseline_Effort')
        r_start, r_end = self.calculate_schedule('Revised_Effort')
        self._plot_impact_map()
        self._plot_schedule_comparison(b_start, b_end, r_start, r_end)

    def _plot_impact_map(self):
        impacted = set(self.change_requests)
        for req in self.change_requests:
            impacted.update(nx.descendants(self.G, req))
            
        fig, ax = plt.subplots(figsize=(12, 8))
        pos = nx.spring_layout(self.G, seed=42, k=0.9)
        
        node_colors = ['#e74c3c' if n in self.change_requests else 
                       '#f39c12' if n in impacted else '#bdc3c7' for n in self.G.nodes()]
        
        nx.draw_networkx_edges(self.G, pos, edge_color='#7f8c8d', arrowsize=25, ax=ax)
        nx.draw_networkx_nodes(self.G, pos, node_color=node_colors, node_size=3000, ax=ax)
        
        labels = {n: f"{n}\n{self.G.nodes[n]['Team']}" for n in self.G.nodes()}
        nx.draw_networkx_labels(self.G, pos, labels=labels, font_size=9, font_weight='bold', ax=ax)
        
        ax.set_title("STRATEGIC IMPACT MAP: CROSS-FUNCTIONAL RISK", fontsize=16, fontweight='bold', pad=20)
        
        plt.axis('off')
        plt.savefig('impact_map.png', bbox_inches='tight')
        plt.close()
        print("Success: Generated impact_map.png")

    def _plot_schedule_comparison(self, b_start, b_end, r_start, r_end):
        features = sorted(list(self.G.nodes()))
        y_pos = np.arange(len(features))
        fig, ax = plt.subplots(figsize=(14, 8))
        
        ax.barh(y_pos + 0.2, [b_end[f] - b_start[f] for f in features], 
                left=[b_start[f] for f in features], height=0.4, 
                label='Baseline', color='#bdc3c7', alpha=0.6)
        
        ax.barh(y_pos - 0.2, [r_end[f] - r_start[f] for f in features], 
                left=[r_start[f] for f in features], height=0.4, 
                label='Revised', color='#1e90ff')
        
        for i, f in enumerate(features):
            slip = r_end[f] - b_end[f]
            if slip > 0:
                ax.text(r_end[f] + 1, i, f"DELAY: +{int(slip)}d", 
                        va='center', color='#1e90ff', fontweight='bold')

        ax.set_yticks(y_pos)
        ax.set_yticklabels([f"{f} ({self.G.nodes[f]['Team']})" for f in features])
        ax.invert_yaxis()
        
        ax.set_title("SCHEDULE SHIFT ANALYSIS: BASELINE VS REVISED", fontsize=16, fontweight='bold', pad=20)
        ax.set_xlabel("Working Days")
        ax.legend(loc='lower right')
        
        ax.set_xlim(right=max(r_end.values()) * 1.1)
        
        plt.savefig('schedule_comparison.png', bbox_inches='tight')
        plt.close()
        print("Success: Generated schedule_comparison.png")

if __name__ == "__main__":
    analyzer = FeatureAnalyzer('features.csv', 'dependencies.csv')
    analyzer.generate_full_analysis()
