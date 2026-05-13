import matplotlib.pyplot as plt
import networkx as nx
import numpy as np


def is_subpath(passenger_path, candidate_line):
    n = len(passenger_path)
    
    if not n:
        return False
    
    for i in range(len(candidate_line) - n + 1):
        if list(candidate_line[i : i + n]) == list(passenger_path):
            return True
            
    reversed_line = list(candidate_line[::-1])
    for i in range(len(reversed_line) - n + 1):
        if reversed_line[i : i + n] == list(passenger_path):
            return True
            
    return False


def plot_network(network, frequencies = None, objective = None, solver_name = None):
    plt.figure(figsize = (12, 10))

    positions = network.points
    edges = list(network.graph.edges())
    
    requirements = [network.line_frequencies.get(tuple(sorted((u, v))), 0) for u, v in edges]
    max_req = max(requirements) if requirements and max(requirements) > 0 else 1
    edge_widths = [1 + 4 * (r / max_req) for r in requirements]

    nx.draw_networkx_edges(
        network.graph,
        positions,
        width = edge_widths,
        edge_color = "gray",
        alpha = 0.15
    )

    if frequencies is not None:
        colors = plt.cm.get_cmap("tab10").colors
        active_indices = [i for i, f in enumerate(frequencies) if f > 0]

        edge_to_lines = {}
        for i in active_indices:
            for edge in network.line_edges[i]:
                s_edge = tuple(sorted(edge))
                if s_edge not in edge_to_lines:
                    edge_to_lines[s_edge] = []
                edge_to_lines[s_edge].append(i)

        offset_step = 1.4
        line_offsets = {}

        for edge, lines in edge_to_lines.items():
            u, v = edge
            lines.sort()
            dx = positions[v][0] - positions[u][0]
            dy = positions[v][1] - positions[u][1]
            dist = np.hypot(dx, dy)
            
            if dist > 0:
                px, py = -dy / dist, dx / dist
                for j, i in enumerate(lines):
                    shift = (j - (len(lines) - 1) / 2.0) * offset_step
                    line_offsets[(edge, i)] = (px * shift, py * shift)

        for color_i, i in enumerate(active_indices):
            path = network.lines[i]
            color = colors[color_i % len(colors)]
            
            for k in range(len(path) - 1):
                u, v = path[k], path[k + 1]
                s_edge = tuple(sorted((u, v)))
                vx, vy = line_offsets.get((s_edge, i), (0, 0))
                
                plt.plot(
                    [positions[u][0] + vx, positions[v][0] + vx],
                    [positions[u][1] + vy, positions[v][1] + vy],
                    color = color, linewidth = 4, alpha = 0.8,
                    solid_capstyle = "round"
                )

    nx.draw_networkx_nodes(
        network.graph, positions, 
        node_color = "lightblue", node_size = 300, 
        edgecolors = "white", linewidths = 1.5
    )

    nx.draw_networkx_nodes(
        network.graph, positions, 
        nodelist = network.classification_yards,
        node_color = "orange", node_shape = "s", 
        node_size = 450, edgecolors = "white", linewidths = 1.5
    )

    nx.draw_networkx_labels(
        network.graph, positions, 
        font_size = 8, font_weight = "bold"
    )

    if objective is not None:
        title_text = f"Total Direct Travelers: {objective:.1f}"
        if solver_name is not None:
            title_text += f" | Solver: {solver_name.upper()}"
        plt.title(title_text, fontsize = 14, fontweight = "bold")

    plt.axis("equal")
    plt.axis("off")
    plt.show()