from typing import List, Dict, Set
import random
import networkx as nx

class MazeGenerator:
    def __init__(self, num_rows: int, num_cols: int):
        self.num_rows = num_rows
        self.num_cols = num_cols
        self.num_rooms = num_rows * num_cols

    def generate_graph(self) -> Dict[int, Set[int]]:
        """
        Genera un grafo che rappresenta le connessioni tra le stanze del labirinto.
        Returns:
            Dict[int, Set[int]]: Dizionario dove le chiavi sono gli ID delle stanze
                                e i valori sono insiemi di ID delle stanze adiacenti.
        """
        graph = {i: set() for i in range(self.num_rooms)}
        
        # Collega le stanze orizzontalmente
        for row in range(self.num_rows):
            for col in range(self.num_cols - 1):
                room_id = row * self.num_cols + col
                next_room = room_id + 1
                graph[room_id].add(next_room)
                graph[next_room].add(room_id)

        # Collega le stanze verticalmente
        for row in range(self.num_rows - 1):
            for col in range(self.num_cols):
                room_id = row * self.num_cols + col
                room_below = room_id + self.num_cols
                graph[room_id].add(room_below)
                graph[room_below].add(room_id)

        return graph
    

    def generate_grid_graph(self, rows=4, cols=6):
        """
        Generate a 4x6 grid graph with static edge removals based on an internal configuration.
        
        Returns:
            nx.Graph: A 4x6 grid graph with predetermined edges removed
        """
        import networkx as nx
        
        # Create an empty graph
        G = nx.Graph()
        
        # Generate nodes in a grid structure (4 rows x 6 columns)
        for r in range(rows):
            for c in range(cols):
                node_id = r * cols + c
                G.add_node(node_id)
        
        # Dictionary to store adjacent nodes
        adjacent_nodes = {}
        
        # Add connections between adjacent nodes
        for r in range(rows):
            for c in range(cols):
                current_node = r * cols + c
                adjacent = []
                
                # Right connection
                if c < cols - 1:
                    right_node = current_node + 1
                    G.add_edge(current_node, right_node)
                    adjacent.append(right_node)
                
                # Left connection
                if c > 0:
                    left_node = current_node - 1
                    adjacent.append(left_node)
                
                # Down connection
                if r < rows - 1:
                    down_node = current_node + cols
                    G.add_edge(current_node, down_node)
                    adjacent.append(down_node)
                
                # Up connection
                if r > 0:
                    up_node = current_node - cols
                    adjacent.append(up_node)
                
                # Store adjacent nodes
                adjacent_nodes[current_node] = adjacent
        
        # Predefined removal configuration tailored for a 4x6 grid
        # Format: {node_id: [neighbor_ids_to_disconnect]}
        removal_config = {
            0: [1],         # Top row, first node
            2: [8],         # Top row, third node
            5: [11],        # Top row, last node
            6: [7, 12],     # Second row, first node
            9: [10, 15],    # Second row, fourth node
            13: [14],       # Third row, second node
            17: [16, 23],   # Third row, last node
            19: [13],       # Fourth row, second node
            21: [15],       # Fourth row, fourth node
            22: [21]        # Fourth row, fifth node
        }
        
        # Remove edges according to the predefined configuration
        for node, neighbors_to_remove in removal_config.items():
            for neighbor in neighbors_to_remove:
                # Check if node and neighbor are within the grid boundaries
                if (node < rows * cols and neighbor < rows * cols and 
                    node >= 0 and neighbor >= 0 and 
                    G.has_edge(node, neighbor)):
                    
                    # Create a temporary graph to check connectivity
                    G_temp = G.copy()
                    G_temp.remove_edge(node, neighbor)
                    
                    # Only remove the edge if it doesn't disconnect the graph
                    if nx.is_connected(G_temp):
                        G.remove_edge(node, neighbor)
        
        return G






        def get_neighbors(self, room_id: int) -> List[int]:
            """
            Ottiene le stanze adiacenti per una data stanza.
            Args:
                room_id (int): ID della stanza
            Returns:
                List[int]: Lista degli ID delle stanze adiacenti
            """
            neighbors = []
            row = room_id // self.num_cols
            col = room_id % self.num_cols

            # Controlla stanza a sinistra
            if col > 0:
                neighbors.append(room_id - 1)
            
            # Controlla stanza a destra
            if col < self.num_cols - 1:
                neighbors.append(room_id + 1)
            
            # Controlla stanza sopra
            if row > 0:
                neighbors.append(room_id - self.num_cols)
            
            # Controlla stanza sotto
            if row < self.num_rows - 1:
                neighbors.append(room_id + self.num_cols)

            return neighbors