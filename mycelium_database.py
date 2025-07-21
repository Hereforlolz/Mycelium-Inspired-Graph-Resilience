# mycelium_database.py
import neo4j
import networkx as nx
import time
from getpass import getpass # This might be used if you set up Neo4j directly in the class

class MyceliumGraphDatabase:
    """
    A bio-inspired graph database wrapper that implements mycelium-like behaviors:
    - Self-healing through path redundancy
    - Adaptive routing based on network conditions
    - Distributed resource allocation
    - Dynamic topology optimization
    """

    def __init__(self, uri=None, user=None, password=None, use_networkx=True):
        self.use_networkx = use_networkx
        self.graph = nx.Graph()
        self.node_resources = {}
        self.edge_weights = {}
        self.healing_factor = 0.8
        self.growth_rate = 0.1

        # For actual Neo4j connection (commented for Colab demo)
        if uri and user and password:
            try:
                self.driver = neo4j.GraphDatabase.driver(uri, auth=(user, password))
                # Test connection
                with self.driver.session() as session:
                    session.run("RETURN 1")
                print("Neo4j driver initialized and connected successfully.")
            except Exception as e:
                self.driver = None
                print(f"Failed to connect to Neo4j: {e}. Operating in NetworkX-only mode.")
        else:
            self.driver = None
            print("Neo4j connection not provided. Operating in NetworkX-only mode.")

    def close(self):
        if self.driver:
            self.driver.close()
            print("Neo4j driver closed.")

    def add_mycelial_node(self, node_id, resources=100, node_type="hyphal_tip"):
        """Add a node with mycelium-inspired properties to NetworkX AND Neo4j"""
        # Add to NetworkX graph
        self.graph.add_node(node_id,
                            resources=resources,
                            node_type=node_type,
                            health=1.0,
                            connections=0)
        self.node_resources[node_id] = resources

        # Add to Neo4j (if driver is available)
        if self.driver:
            query = """
            MERGE (n:MycelialNode {id: $node_id})
            ON CREATE SET
                n.resources = $resources,
                n.type = $node_type,
                n.health = $health,
                n.connections = $connections
            ON MATCH SET
                n.resources = $resources,
                n.type = $node_type,
                n.health = $health,
                n.connections = $connections
            """
            with self.driver.session() as session:
                session.write_transaction(
                    lambda tx: tx.run(query,
                        node_id=node_id,
                        resources=resources,
                        node_type=node_type,
                        health=1.0, # Initial health for Neo4j
                        connections=0 # Initial connections for Neo4j
                    )
                )
            # print(f"Node {node_id} added/updated in NetworkX and Neo4j.")
        # else:
            # print(f"Node {node_id} added to NetworkX only (Neo4j driver not active).")

    def add_mycelial_connection(self, node1, node2, strength=1.0, transport_capacity=10):
        """Create connections with biological transport properties for NetworkX AND Neo4j"""
        # Add to NetworkX graph
        self.graph.add_edge(node1, node2,
                            strength=strength,
                            capacity=transport_capacity,
                            flow=0,
                            last_used=time.time())
        self.edge_weights[(node1, node2)] = strength

        # Add to Neo4j (if driver is available)
        if self.driver:
            query = """
            MATCH (n1:MycelialNode {id: $node1_id})
            MATCH (n2:MycelialNode {id: $node2_id})
            MERGE (n1)-[r:CONNECTS]->(n2)
            ON CREATE SET
                r.strength = $strength,
                r.capacity = $transport_capacity,
                r.flow = $flow,
                r.last_used = $last_used
            ON MATCH SET
                r.strength = $strength,
                r.capacity = $transport_capacity,
                r.flow = $flow,
                r.last_used = $last_used
            """
            with self.driver.session() as session:
                session.write_transaction(
                    lambda tx: tx.run(query,
                        node1_id=node1,
                        node2_id=node2,
                        strength=strength,
                        transport_capacity=transport_capacity,
                        flow=0,
                        last_used=time.time() # Current time for Neo4j
                    )
                )
            # print(f"Edge ({node1}, {node2}) added/updated in NetworkX and Neo4j.")
        # else:
            # print(f"Edge ({node1}, {node2}) added to NetworkX only (Neo4j driver not active).")


# Helper function to create initial network - useful for external use
def create_mycelium_inspired_network(db_instance, num_nodes=20, connection_prob=0.15):
    """
    Create a network that mimics mycelium structure,
    using an existing MyceliumGraphDatabase instance.
    """
    db = db_instance

    # Add nodes with varying resource levels
    for i in range(num_nodes):
        resources = random.randint(50, 150)
        node_type = "source" if i < 3 else "intermediate" if i < num_nodes-3 else "sink"
        db.add_mycelial_node(f"node_{i}", resources, node_type)

    # Create connections with preference for nearby nodes (simulated spatial clustering)
    nodes = list(db.graph.nodes())
    for i, node1 in enumerate(nodes):
        for j, node2 in enumerate(nodes[i+1:], i+1):
            # Higher probability for "nearby" nodes (simulated spatial proximity)
            distance_factor = abs(i - j) / len(nodes)
            prob = connection_prob * (1 - distance_factor)

            if random.random() < prob:
                strength = random.uniform(0.5, 1.5)
                capacity = random.randint(5, 15)
                db.add_mycelial_connection(node1, node2, strength, capacity)

    return db

# Note: `random` is imported in mycelium_algorithm.py,
# but also useful here for `create_mycelium_inspired_network`.
# You might want to consolidate shared imports or import here as well if needed.
import random # Added here for create_mycelium_inspired_network