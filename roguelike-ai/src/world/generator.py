from typing import List, Dict, Set

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