#!/usr/bin/env python3
import argparse
import sys
import networkx as nx
from core.network import Network
from core.solver_mip import solve_mip
from core.solver_heuristics import solve_sa
from core.utils import plot_network


parser = argparse.ArgumentParser()
parser.add_argument("--network", type = str, default = "random", help = "Path to network file or 'random' to generate.")
parser.add_argument("--stations", type = int, default = 30, help = "Number of stations.")
parser.add_argument("--classification_yards", type = int, default = 5, help = "Number of classification yards.")
parser.add_argument("--capacity", type = int, default = 500, help = "Train capacity.")
parser.add_argument("--demand_probability", type = float, default = 0.2, help = "Probability of demand between nodes.")
parser.add_argument("--min_demand", type = int, default = 10, help = "Minimum demand value.")
parser.add_argument("--max_demand", type = int, default = 20, help = "Maximum demand value.")
parser.add_argument("--solver", type = str, default = "mip", choices = ["mip", "sa"], help = "Solver algorithm to use.")
parser.add_argument("--visualize", action = "store_true", help = "Visualize the network.")
parser.add_argument("--seed", type = int, default = 42, help = "Random seed.")


def main(args):
    if args.network == "random":
        network = Network.generate_random(
            stations = args.stations,
            classification_yards = args.classification_yards,
            capacity = args.capacity,
            seed = args.seed,
            demand_probability = args.demand_probability,
            min_demand = args.min_demand,
            max_demand = args.max_demand
        )
    else:
        try:
            network = Network.load_from_file(args.network)
            if args.visualize and not network.points:
                network.points = nx.spring_layout(network.graph, seed = args.seed)
        except Exception as exception:
            print(f"Error: {exception}")
            sys.exit(1)

    try:
        if args.solver == "mip":
            frequencies, direct_travelers = solve_mip(network)
        elif args.solver == "sa":
            frequencies, direct_travelers = solve_sa(network)
    except Exception as exception:
        print(f"Error: {exception}")
        sys.exit(1)

    if frequencies is None:
        print("No solution found.")
        sys.exit(1)

    active_lines = [(i, f) for i, f in enumerate(frequencies) if f > 0]

    print("***********************************************************")
    print(f"Network: {args.network}")
    print(f"Solver: {args.solver.upper()}")
    print(f"Candidate Lines: {len(network.lines)}")
    print(f"Active Lines: {len(active_lines)}")
    print(f"Objective (Total Direct Travelers): {direct_travelers:.1f}")
    print("***********************************************************")

    for i, frequency in active_lines:
        print(f"Line {i:2d} [Frequency: {frequency:2d}]: {network.lines[i]}")

    if args.visualize:
        plot_network(network, frequencies = frequencies, objective = direct_travelers)


if __name__ == "__main__":
    main_args = parser.parse_args()
    main(main_args)