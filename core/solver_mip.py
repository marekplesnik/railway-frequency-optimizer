import gurobipy as gp
from core.utils import is_subpath


def solve_mip(network):
    model = gp.Model()
    model.setParam('OutputFlag', 0)

    lines_for_path = {node_pair : [] for node_pair in network.traffic_demands.keys()}
    for node_pair, path in network.shortest_paths.items():
        for i, line in enumerate(network.lines):
            if is_subpath(path, line):
                lines_for_path[node_pair].append(i)

    lines_for_edge = {edge : [] for edge in network.line_frequencies.keys()}
    for i, line_edges in enumerate(network.line_edges):
        for edge in line_edges:
            if edge in lines_for_edge:
                lines_for_edge[edge].append(i)

    direct_travelers = model.addVars(
        network.traffic_demands.keys(),
        vtype = "C",
        lb = 0,
        name = "direct_travelers"
    )

    line_frequencies = model.addVars(
        len(network.lines),
        vtype = "I",
        lb = 0,
        name = "line_frequency"
    )

    model.setObjective(
        gp.quicksum(direct_travelers[node_pair] for node_pair in network.traffic_demands.keys()) - 0.001 * gp.quicksum(line_frequencies[i] for i in range(len(network.lines))),
        sense = -1
    )

    for node_pair, demand in network.traffic_demands.items():
        model.addConstr(direct_travelers[node_pair] <= demand)
        model.addConstr(direct_travelers[node_pair] <= network.capacity * gp.quicksum(line_frequencies[i] for i in lines_for_path[node_pair]))

    for edge, requirement in network.line_frequencies.items():
        model.addConstr(gp.quicksum(line_frequencies[i] for i in lines_for_edge[edge]) >= requirement)

    model.optimize()

    if model.Status == 2:
        calculated_frequencies = [int(round(line_frequencies[i].X)) for i in range(len(network.lines))]
        total_travelers = sum(direct_travelers[node_pair].X for node_pair in network.traffic_demands.keys())
        return calculated_frequencies, total_travelers
    
    return None, 0