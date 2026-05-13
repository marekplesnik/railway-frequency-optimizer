import numpy as np
import networkx as nx
from scipy.spatial import Delaunay


class Network:


    def __init__(self):
        self.capacity = np.inf
        self.stations = 0
        self.demand_probability = 0
        
        self.points = {}
        self.graph = nx.Graph()
        self.classification_yards = []
        
        self.lines = []
        self.serviced_edges = set()
        self.serviced_graph = nx.Graph()
        
        self.traffic_demands = {}
        self.shortest_paths = {}
        self.traffic_loads = {}
        self.line_frequencies = {}
        self.line_edges = []


    @classmethod
    def generate_random(cls, stations, classification_yards, capacity, seed, demand_probability, min_demand, max_demand):
        np.random.seed(seed)
        
        network = cls()
        network.stations = stations
        network.capacity = capacity
        network.demand_probability = demand_probability
        
        temp_points = {i : (int(np.random.randint(0, 101)), int(np.random.randint(0, 101))) for i in range(network.stations)}

        station_coordinates = np.array([temp_points[i] for i in range(network.stations)])
        delaunay_mesh = Delaunay(station_coordinates)

        base_graph = nx.Graph()
        for triangle in delaunay_mesh.simplices:
            for i in range(3):
                station_a, station_b = int(triangle[i]), int(triangle[(i + 1) % 3])
                dist = float(np.hypot(temp_points[station_a][0] - temp_points[station_b][0],
                                     temp_points[station_a][1] - temp_points[station_b][1]))
                base_graph.add_edge(station_a, station_b, weight = dist)

        network.graph = nx.minimum_spanning_tree(base_graph)
        
        remaining_edges = [edge for edge in base_graph.edges(data = True) if not network.graph.has_edge(edge[0], edge[1])]
        np.random.shuffle(remaining_edges)
        network.graph.add_edges_from(remaining_edges[:int(network.stations * 0.2)])

        node_degrees = dict(network.graph.degree())
        leaf_nodes = [node for node, degree in node_degrees.items() if degree == 1]
        sample_size = min(len(leaf_nodes), classification_yards)
        network.classification_yards = np.random.choice(leaf_nodes, size = sample_size, replace = False).tolist() if sample_size > 0 else []

        network._build_lines()

        serviced_nodes_set = set(network.serviced_graph.nodes())
        node_mapping = {old_id : new_id for new_id, old_id in enumerate(sorted(serviced_nodes_set))}
        
        network.points = {node_mapping[node] : temp_points[node] for node in serviced_nodes_set}
        network.classification_yards = [node_mapping[y] for y in network.classification_yards]
        
        new_graph = nx.Graph()
        for u, v, data in network.graph.edges(data = True):
            if u in node_mapping and v in node_mapping:
                new_graph.add_edge(node_mapping[u], node_mapping[v], **data)
        
        network.graph = new_graph
        network.stations = len(network.points)

        network._build_lines()

        serviced_nodes = list(network.points.keys())
        for i in range(len(serviced_nodes)):
            for j in range(i + 1, len(serviced_nodes)):
                if np.random.random() < network.demand_probability:
                    station_a, station_b = serviced_nodes[i], serviced_nodes[j]
                    network.traffic_demands[tuple(sorted((station_a, station_b)))] = int(np.random.randint(min_demand, max_demand + 1))

        network._route_demands()

        return network


    @classmethod
    def load_from_file(cls, filepath):
        network = cls()
        blocks, current_block = [], []

        with open(filepath, "r") as file:
            for line in file:
                line = line.strip()

                if line:
                    current_block.append(line)
                elif current_block:
                    blocks.append(current_block)
                    current_block = []

            if current_block:
                blocks.append(current_block)
        
        for block in blocks:
            header, data = block[0].lower(), block[1:]

            if header == "capacity":
                network.capacity = float(data[0])
            
            elif header == "stations":
                network.graph.add_nodes_from([int(node) for node in data])
            
            elif header == "classification yards":
                classification_yards = [int(node) for node in data]
                network.classification_yards.extend(classification_yards)
                network.graph.add_nodes_from(classification_yards)
            
            elif header == "connections":
                for line in data:
                    station_a, station_b, weight = line.split()
                    network.graph.add_edge(int(station_a), int(station_b), weight = float(weight))
            
            elif header == "demands":
                for line in data:
                    station_a, station_b, demand = line.split()
                    network.traffic_demands[tuple(sorted((int(station_a), int(station_b))))] = int(demand)

        network.stations = len(network.graph.nodes())
        network._build_lines()
        network._route_demands()

        return network
        

    def _build_lines(self):
        self.lines = []
        self.serviced_edges = set()

        for i in range(len(self.classification_yards)):
            for j in range(i + 1, len(self.classification_yards)):
                try:
                    path = nx.shortest_path(
                        self.graph,
                        self.classification_yards[i],
                        self.classification_yards[j],
                        weight = "weight"
                    )  
                    
                    self.lines.append(path)
                    for k in range(len(path) - 1):
                        self.serviced_edges.add(tuple(sorted((path[k], path[k + 1]))))
                
                except nx.NetworkXNoPath:
                    pass
        
        self.serviced_graph = nx.Graph()
        for u, v in self.serviced_edges:
            weight = self.graph[u][v].get("weight", 1)
            self.serviced_graph.add_edge(u, v, weight = weight)


    def _route_demands(self):
        self.shortest_paths = {}
        self.traffic_loads = {edge : 0 for edge in self.serviced_edges}

        for (u, v), demand in self.traffic_demands.items():
            try:
                path = nx.shortest_path(
                    self.serviced_graph,
                    u,
                    v,
                    weight = "weight"
                )

                self.shortest_paths[(u, v)] = path
                for k in range(len(path) - 1):
                    edge = tuple(sorted((path[k], path[k + 1])))
                    self.traffic_loads[edge] += demand

            except nx.NetworkXNoPath:
                pass
        
        self.line_frequencies = {edge : int(np.ceil(load / self.capacity)) for edge, load in self.traffic_loads.items()}
        self.line_edges = [[tuple(sorted((path[k], path[k + 1]))) for k in range(len(path) - 1)] for path in self.lines]