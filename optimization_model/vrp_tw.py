import gurobipy as gp
from gurobipy import GRB
import networkx as nx
import matplotlib.pyplot as plt


class VRPTWData:
    def __init__(self):
        self.num_vehicles = 2
        self.depot = 0
        self.distance_matrix = [
            [0, 9, 10, 14, 15, 20],
            [9, 0, 7, 12, 13, 18],
            [10, 7, 0, 5, 6, 11],
            [14, 12, 5, 0, 9, 14],
            [15, 13, 6, 9, 0, 8],
            [20, 18, 11, 14, 8, 0],
        ]
        self.time_windows = [
            (0, 5),  # depot
            (7, 12),  # location 1
            (10, 15),  # location 2
            (16, 18),  # location 3
            (10, 13),  # location 4
            (0, 5),  # location 5
        ]


class VRPTWModel:
    def __init__(self, data):
        self.data = data
        self.model = gp.Model("vrp_tw")
        self.num_locations = len(data.distance_matrix)
        self.vehicle_routes = {}
        self.vars = {}

    def setup_variables(self):
        # Create decision variables
        self.vars = self.model.addVars(self.num_locations, self.num_locations, self.data.num_vehicles, vtype=GRB.BINARY,
                                       name='x')
        self.time_vars = self.model.addVars(self.num_locations, self.data.num_vehicles, vtype=GRB.CONTINUOUS, name='t')

    def setup_constraints(self):
        data = self.data
        model = self.model

        # Time window constraints
        for i in range(self.num_locations):
            for v in range(data.num_vehicles):
                model.addConstr(self.time_vars[i, v] >= data.time_windows[i][0], name=f"tw_lower_{i}_{v}")
                model.addConstr(self.time_vars[i, v] <= data.time_windows[i][1], name=f"tw_upper_{i}_{v}")

        # Flow constraints
        for i in range(self.num_locations):
            model.addConstr(gp.quicksum(
                self.vars[i, j, v] for j in range(self.num_locations) for v in range(data.num_vehicles)) == 1,
                            name=f"flow_out_{i}")
            model.addConstr(gp.quicksum(
                self.vars[j, i, v] for j in range(self.num_locations) for v in range(data.num_vehicles)) == 1,
                            name=f"flow_in_{i}")

        # Subtour elimination and time constraints
        for v in range(data.num_vehicles):
            for i in range(self.num_locations):
                for j in range(self.num_locations):
                    if i != j:
                        model.addConstr(
                            self.time_vars[j, v] >= self.time_vars[i, v] + data.distance_matrix[i][j] - (
                                        1 - self.vars[i, j, v]) * 10000,
                            name=f"subtour_{i}_{j}_{v}")

    def setup_objective(self):
        # Objective: Minimize the total travel distance
        self.model.setObjective(
            gp.quicksum(self.vars[i, j, v] * self.data.distance_matrix[i][j]
                        for i in range(self.num_locations)
                        for j in range(self.num_locations)
                        for v in range(self.data.num_vehicles)),
            GRB.MINIMIZE)

    def solve(self):
        self.setup_variables()
        self.setup_constraints()
        self.setup_objective()
        self.model.optimize()

        if self.model.status == GRB.OPTIMAL:
            for v in range(self.data.num_vehicles):
                self.vehicle_routes[v] = []
                for i in range(self.num_locations):
                    for j in range(self.num_locations):
                        if self.vars[i, j, v].x > 0.5:
                            self.vehicle_routes[v].append((i, j))

    def print_solution(self):
        for v, route in self.vehicle_routes.items():
            print(f"Route for vehicle {v}: {route}")


class VRPNetworkPlot:
    def __init__(self, data, routes):
        self.data = data
        self.routes = routes
        self.G = nx.DiGraph()

    def create_graph(self):
        for v, route in self.routes.items():
            for i, j in route:
                self.G.add_edge(i, j, vehicle=v)

    def draw(self):
        pos = nx.spring_layout(self.G)  # Generate positions for nodes
        labels = {i: f'{i}' for i in self.G.nodes()}  # Labels for nodes
        edge_labels = {(i, j): f'Vehicle {self.G.edges[i, j]["vehicle"]}' for i, j in self.G.edges()}  # Labels for edges
        edge_colors = [self.G.edges[i, j]["vehicle"] for i, j in self.G.edges()]  # Different colors for different vehicles

        # Draw the graph
        nx.draw(self.G, pos, with_labels=True, labels=labels, node_color='lightblue', node_size=3000, edge_color=edge_colors, edge_cmap=plt.cm.Blues, width=2)
        nx.draw_networkx_edge_labels(self.G, pos, edge_labels=edge_labels)
        plt.show()

