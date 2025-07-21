# mycelium_algorithms.py
import networkx as nx
import random
from collections import defaultdict, deque # deque not used in the provided algo, but good to keep if from original notebook
import math # Not used in provided algos, but often in graph math

class MyceliumAlgorithms:
    """
    Bio-inspired algorithms based on mycelium network behaviors
    """

    @staticmethod
    def hyphal_growth_pathfinding(graph, start, target, avoid_overused=True):
        """
        Pathfinding inspired by hyphal growth patterns:
        - Prefers paths with available resources
        - Avoids oversaturated routes
        - Creates redundant pathways naturally
        """
        paths = []

        # Find multiple paths like mycelium creates redundant connections
        try:
            # Primary path (shortest)
            primary = nx.shortest_path(graph, start, target)
            paths.append(("primary", primary))

            # Alternative paths (resource-aware)
            for _ in range(3):  # Try to find 3 alternative routes
                temp_graph = graph.copy()
                # Remove some edges from previous paths to force alternatives
                if paths:
                    for path_type, path in paths:
                        for i in range(len(path)-1):
                            if temp_graph.has_edge(path[i], path[i+1]):
                                if random.random() < 0.3:  # 30% chance to remove
                                    temp_graph.remove_edge(path[i], path[i+1])

                try:
                    alt_path = nx.shortest_path(temp_graph, start, target)
                    if alt_path not in [p[1] for p in paths]:
                        paths.append((f"alternative_{len(paths)}", alt_path))
                except nx.NetworkXNoPath:
                    continue

        except nx.NetworkXNoPath:
            return []

        return paths

    @staticmethod
    def nutrient_flow_simulation(graph, source_nodes, sink_nodes, time_steps=10):
        """
        Simulate resource flow like nutrients in mycelium networks:
        - Resources flow from high to low concentration
        - Pathways strengthen with use
        - Unused pathways may weaken
        """
        flow_history = []

        for step in range(time_steps):
            step_flows = {}

            # Calculate flow between connected nodes
            for edge in graph.edges():
                node1, node2 = edge
                resource1 = graph.nodes[node1].get('resources', 0)
                resource2 = graph.nodes[node2].get('resources', 0)

                # Flow from high to low concentration
                if resource1 != resource2:
                    capacity = graph.edges[edge].get('capacity', 1)
                    flow_rate = min(capacity, abs(resource1 - resource2) * 0.1)

                    if resource1 > resource2:
                        flow_direction = (node1, node2)
                        flow_amount = flow_rate
                    else:
                        flow_direction = (node2, node1)
                        flow_amount = flow_rate

                    step_flows[edge] = {
                        'direction': flow_direction,
                        'amount': flow_amount
                    }

            # Apply flows
            for edge, flow_data in step_flows.items():
                from_node, to_node = flow_data['direction']
                amount = flow_data['amount']

                # Transfer resources
                current_from = graph.nodes[from_node].get('resources', 0)
                current_to = graph.nodes[to_node].get('resources', 0)

                graph.nodes[from_node]['resources'] = max(0, current_from - amount)
                graph.nodes[to_node]['resources'] = current_to + amount

                # Strengthen used pathways
                current_strength = graph.edges[edge].get('strength', 1.0)
                graph.edges[edge]['strength'] = min(2.0, current_strength + 0.1)

            flow_history.append(step_flows.copy())

        return flow_history

    @staticmethod
    def self_healing_response(graph, damaged_nodes, healing_factor=0.8):
        """
        Implement self-healing like mycelium networks:
        - Reroute around damaged areas
        - Create new connections to restore connectivity
        - Redistribute resources from damaged nodes
        """
        healing_actions = []

        # Remove damaged nodes and redistribute their resources
        for node in damaged_nodes:
            if node in graph.nodes():
                # Get neighbors before removal
                neighbors = list(graph.neighbors(node))
                resources = graph.nodes[node].get('resources', 0)

                # Redistribute resources to neighbors
                if neighbors:
                    resource_per_neighbor = resources / len(neighbors)
                    for neighbor in neighbors:
                        current_resources = graph.nodes[neighbor].get('resources', 0)
                        graph.nodes[neighbor]['resources'] = current_resources + resource_per_neighbor

                graph.remove_node(node)
                healing_actions.append(f"Removed damaged node {node}, redistributed {resources} resources")

        # Create new connections to restore network connectivity
        components = list(nx.connected_components(graph))
        if len(components) > 1:
            # Connect isolated components
            for i in range(len(components) - 1):
                comp1_nodes = list(components[i])
                comp2_nodes = list(components[i + 1])

                # Find closest nodes between components (simplified)
                node1 = random.choice(comp1_nodes)
                node2 = random.choice(comp2_nodes)

                graph.add_edge(node1, node2,
                            strength=healing_factor,
                            capacity=5,
                            healing_connection=True)

                healing_actions.append(f"Created healing connection: {node1} -> {node2}")

        return healing_actions