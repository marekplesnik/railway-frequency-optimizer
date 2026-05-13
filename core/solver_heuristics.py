import numpy as np
from core.utils import is_subpath


def get_objective(network, frequencies, lines_for_path):
    total_direct_travelers = 0
    for node_pair, demand in network.traffic_demands.items():
        if node_pair in lines_for_path:
            frequency_sum = sum(frequencies[i] for i in lines_for_path[node_pair])
            total_direct_travelers += min(demand, network.capacity * frequency_sum)
    
    total_trains = sum(frequencies)
    return total_direct_travelers - (0.001 * total_trains)


def is_feasible(network, frequencies):
    edge_counts = {edge : 0 for edge in network.line_frequencies.keys()}
    for i, frequency in enumerate(frequencies):
        if frequency > 0:
            for edge in network.line_edges[i]:
                if edge in edge_counts:
                    edge_counts[edge] += frequency

    for edge, requirement in network.line_frequencies.items():
        if edge_counts[edge] < requirement:
            return False
    return True


def solve_sa(network):
    iterations, initial_temperature = 5000, 1000
    lines_for_path = {node_pair : [] for node_pair in network.traffic_demands.keys()}

    for node_pair, path in network.shortest_paths.items():
        for line_index, line in enumerate(network.lines):
            if is_subpath(path, line):
                lines_for_path[node_pair].append(line_index)

    current_frequencies = [0] * len(network.lines)
    for edge, requirement in network.line_frequencies.items():
        while True:
            current_edge_count = sum(current_frequencies[i] for i, edges in enumerate(network.line_edges) if edge in edges)
            if current_edge_count >= requirement:
                break
            
            valid_lines = [i for i, edges in enumerate(network.line_edges) if edge in edges]
            
            if valid_lines:
                current_frequencies[np.random.choice(valid_lines)] += 1
            else:
                break

    current_objective = get_objective(network, current_frequencies, lines_for_path)
    best_frequencies = current_frequencies[:]
    best_objective = current_objective

    for it in range(iterations):
        temperature = initial_temperature * (1 - it / iterations)
        neighbor_frequencies = current_frequencies[:]
        line_index = np.random.randint(len(network.lines))
        
        change = 1 if np.random.random() > 0.5 else -1
        neighbor_frequencies[line_index] = max(0, neighbor_frequencies[line_index] + change)

        if not is_feasible(network, neighbor_frequencies):
            continue

        neighbor_objective = get_objective(network, neighbor_frequencies, lines_for_path)
        delta_objective = neighbor_objective - current_objective

        if delta_objective > 0 or np.random.random() < np.exp(delta_objective / max(temperature, 1e-10)):
            current_frequencies = neighbor_frequencies
            current_objective = neighbor_objective

            if current_objective > best_objective:
                best_objective = current_objective
                best_frequencies = current_frequencies[:]

    clean_objective = best_objective + (0.001 * sum(best_frequencies))
    return best_frequencies, clean_objective