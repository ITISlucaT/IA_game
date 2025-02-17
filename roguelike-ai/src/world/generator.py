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
    

    def generate_grid_graph(self, rows, cols):
        # Creare un grafo vuoto
        G = nx.Graph()
        
        # Generare nodi in una struttura a griglia
        for r in range(rows):
            for c in range(cols):
                node_id = r * cols + c
                G.add_node(node_id)
        
        # Dizionario per memorizzare i nodi adiacenti
        adjacent_nodes = {}
        
        # Aggiungere connessioni tra nodi adiacenti
        for r in range(rows):
            for c in range(cols):
                current_node = r * cols + c
                adjacent = []
                
                # Connessione destra
                if c < cols - 1:
                    right_node = current_node + 1
                    G.add_edge(current_node, right_node)
                    adjacent.append(right_node)
                
                # Connessione sinistra
                if c > 0:
                    left_node = current_node - 1
                    adjacent.append(left_node)
                
                # Connessione sotto
                if r < rows - 1:
                    down_node = current_node + cols
                    G.add_edge(current_node, down_node)
                    adjacent.append(down_node)
                
                # Connessione sopra
                if r > 0:
                    up_node = current_node - cols
                    adjacent.append(up_node)
                
                # Memorizzare i nodi adiacenti
                adjacent_nodes[current_node] = adjacent
        
        # Rimuovere connessioni in modo selettivo
        for node in list(G.nodes()):
            # Ottenere i vicini attuali
            current_neighbors = list(G.neighbors(node))
            
            # Numero massimo di connessioni da rimuovere
            max_removals = len(current_neighbors)
            
            # Numero casuale di connessioni da rimuovere
            num_removals = random.randint(0, 1)#max_removals)
            
            # Tentativi di rimozione
            for _ in range(num_removals):
                if len(current_neighbors) > 1:  # Assicurarsi di mantenere almeno una connessione
                    # Scegliere un vicino casuale da rimuovere
                    neighbor_to_remove = random.choice(current_neighbors)
                    
                    # Simulare la rimozione e verificare la connettività
                    G_temp = G.copy()
                    G_temp.remove_edge(node, neighbor_to_remove)
                    
                    # Verificare che la rimozione non isoli nessun nodo
                    if nx.is_connected(G_temp):
                        G = G_temp
                        current_neighbors.remove(neighbor_to_remove)

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