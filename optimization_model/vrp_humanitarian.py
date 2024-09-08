import gurobipy as gp
from gurobipy import GRB
import geopandas as gpd
class HumanitarianReliefVRP:
    def __init__(self, warehouses, shelters,  vehicles, distances, demands, capacities, ranges, population):
        self.warehouses = warehouses
        self.shelters = shelters
        self.vehicles = vehicles
        self.distances = distances
        self.demands = demands
        self.capacities = capacities
        self.ranges = ranges
        self.population = population
        self.model = gp.Model("HumanitarianReliefVRP")
        self.x = None
        self.y = None

    def build_model(self):
        # Decision variables
        self.x = self.model.addVars(self.warehouses, self.shelters, self.vehicles, vtype=GRB.BINARY, name="x")
        self.y = self.model.addVars(self.shelters, vtype=GRB.BINARY, name="y")

        # Objective: Maximize the proportion of the population covered
        self.model.setObjective(gp.quicksum(self.population[s] * self.y[s] for s in self.shelters), GRB.MAXIMIZE)

        # Constraints
        for s in self.shelters:
            self.model.addConstr(gp.quicksum(self.x[w, s, v] for w in self.warehouses for v in self.vehicles) >= self.y[s])

        for w in self.warehouses:
            for v in self.vehicles:
                self.model.addConstr(gp.quicksum(self.demands[s] * self.x[w, s, v] for s in self.shelters) <= self.capacities[v])
                self.model.addConstr(gp.quicksum(self.distances[w, s] * self.x[w, s, v] for s in self.shelters) <= self.ranges[v])

    def solve(self):
        self.model.optimize()

    def get_routes(self):
        routes = []
        for w in self.warehouses:
            for s in self.shelters:
                for v in self.vehicles:
                    if self.x[w, s, v].x > 0.5:
                        routes.append((w, s, v))
        return routes

import networkx as nx
import matplotlib.pyplot as plt

class ReliefNetwork:
    def __init__(self, warehouses_location, shelters_location, node_positions, demands):
        self.graph = nx.DiGraph()
        self.warehouses_location = warehouses_location
        self.shelters_location = shelters_location
        self.node_positions = node_positions
        self.demands = demands

    def add_routes(self, routes):
        for route in routes:
            vehicle_type = route[2]
            if vehicle_type.startswith('D'):
                color = 'blue'  # Color for drones
            elif vehicle_type.startswith('T'):
                color = 'green'  # Color for trucks
            else:
                color = 'black'  # Default color
            self.graph.add_edge(route[0], route[1], vehicle=route[2], color=color)

    def plot_network(self, title="Optimized Humanitarian Relief Distribution Network"):
        pos = self.node_positions
        print('pos--------', pos)
        # Separate nodes into warehouses and demand points
        warehouses = [node for node in self.graph.nodes if node.startswith('W')]
        shelters = [node for node in self.graph.nodes if node.startswith('S')]

        # Draw nodes with different shapes and colors
        nx.draw_networkx_nodes(self.graph, pos=pos, nodelist=warehouses, node_color='red', node_shape='s', node_size=1000,
                               label='Warehouses', alpha=0.5)
        nx.draw_networkx_nodes(self.graph, pos=pos, nodelist=shelters, node_color='blue', node_shape='o', node_size=400, # self.demands
                               label='Shelters', alpha=0.5)

        # Draw edges with arrows
        edges = self.graph.edges()
        colors = [self.graph[u][v]['color'] for u, v in edges]
        nx.draw_networkx_edges(self.graph, pos, edgelist=edges, edge_color=colors, arrowstyle='->', arrowsize=15)

        # Add labels for nodes & edges
        nx.draw_networkx_labels(self.graph, pos, font_size=10, font_weight='bold')
        edge_labels = nx.get_edge_attributes(self.graph, 'vehicle')
        nx.draw_networkx_edge_labels(self.graph, pos, edge_labels=edge_labels)

        """
        fig, ax = plt.subplots(figsize=(10, 8))
        feni_GIS_map = gpd.read_file("dataset/processed/feni_GIS_map/feni_GIS_map.shp")
        feni_GIS_map = feni_GIS_map.to_crs(epsg=4326)  # 3857
        feni_GIS_map.plot(ax=ax, color="lightskyblue") #ax=ax,
        nx.draw(self.graph, pos=pos, ax=ax, with_labels=True, font_size=10)
        """
        plt.title(title)
        plt.legend(scatterpoints=1)
        plt.tight_layout()

        plt.savefig('plots/optimized_network.svg')
        plt.show()
