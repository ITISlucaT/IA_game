import pygame as pg
import numpy as np
from typing import List, Dict

class Player:
    def __init__(self, room_size: int, num_rooms: int, config: Dict, player_color: str, spawn_room: int):
        self.current_room = spawn_room
        self.tile_size = config['tile_size']
        self.grid_x = (room_size // self.tile_size) // 2
        self.grid_y = (room_size // self.tile_size) // 2

        self.pos = [
            self.grid_x * self.tile_size + self.tile_size // 2,
            self.grid_y * self.tile_size + self.tile_size // 2
        ]

        self.room_size = room_size
        self.speed = config['player']['speed']
        self.size = config['player']['size']
        self.direction = "left"
        self.last_movement_time = 0
        self.previous_room = self.current_room
        self.room_changed = False
        self.move_progress = 0  # 0-100% dell'animazione
        self.is_moving = False
        self.target_pos = [self.grid_x, self.grid_y]
        self.player_color = player_color
        
        # New attributes for movement tracking
        self.movement_history = []
        self.total_movement_distance = 0
        self.idle_time = 0
        self.last_position = self.pos.copy()

    def draw(self, surface, num_cols: int, colors: Dict):
        room_row = self.current_room // num_cols
        room_col = self.current_room % num_cols
        x = room_col * self.room_size + self.pos[0]
        y = room_row * self.room_size + self.pos[1]
        pg.draw.circle(surface, colors[self.player_color], (x, y), self.size)

    def move(self, direction: str, num_cols: int, num_rooms: int, current_room: 'Room'):
        new_grid_x, new_grid_y = self.grid_x, self.grid_y
        target_direction = None

        if direction == "UP":
            new_grid_y -= 1
            target_direction = 'top'
        elif direction == "DOWN":
            new_grid_y += 1
            target_direction = 'bottom'
        elif direction == "LEFT":
            new_grid_x -= 1
            target_direction = 'left'
        elif direction == "RIGHT":
            new_grid_x += 1
            target_direction = 'right'

        # Controlla se il movimento è all'interno della stanza
        grid_size = current_room.grid_size
        if 0 <= new_grid_x < grid_size and 0 <= new_grid_y < grid_size:
            self.grid_x = new_grid_x
            self.grid_y = new_grid_y
            self.is_moving = True
            self.target_pos = [new_grid_x, new_grid_y]
        else:
            # Controlla se c'è una porta valida e se il giocatore è allineato con essa
            if current_room.can_pass_through(self.grid_x, self.grid_y, target_direction):
                self._change_room(target_direction, num_cols, num_rooms)
                self.is_moving = True
            else:
                # Blocca il movimento se non c'è una porta o il giocatore non è allineato
                return

        # Aggiorna la posizione assoluta
        self.pos = [
            self.grid_x * self.tile_size + self.tile_size // 2,
            self.grid_y * self.tile_size + self.tile_size // 2
        ]

    def is_currently_moving(self) -> bool:
        """
        Determina se il giocatore si sta muovendo attivamente.
        
        Returns:
            bool: True se il giocatore è in movimento, False altrimenti
        """
        return self.is_moving

    def get_movement_metrics(self) -> Dict[str, float]:
        """
        Calcola metriche di movimento per l'utilizzo nella rete neurale.
        
        Returns:
            Dict[str, float]: Dizionario con metriche di movimento
        """
        # Calcola la distanza percorsa
        current_distance = np.sqrt(
            (self.pos[0] - self.last_position[0])**2 + 
            (self.pos[1] - self.last_position[1])**2
        )
        
        # Aggiorna la distanza totale
        self.total_movement_distance += current_distance
        
        # Aggiorna la posizione precedente
        self.last_position = self.pos.copy()
        
        # Calcola il tempo di inattività
        if not self.is_moving:
            self.idle_time += 1
        else:
            self.idle_time = 0
        
        return {
            'is_moving': float(self.is_moving),
            'total_distance': self.total_movement_distance,
            'idle_time': self.idle_time
        }

    def _change_room(self, direction: str, num_cols: int, num_rooms: int):
        grid_size = self.room_size // self.tile_size
        if direction == 'left':
            self.current_room -= 1
            self.grid_x = grid_size - 1
        elif direction == 'right':
            self.current_room += 1
            self.grid_x = 0
        elif direction == 'top':
            self.current_room -= num_cols
            self.grid_y = grid_size - 1
        elif direction == 'bottom':
            self.current_room += num_cols
            self.grid_y = 0

    def update(self, dt):
        if self.is_moving:
            self.move_progress += dt * 5  # Regola la velocità dell'animazione
            if self.move_progress >= 100:
                self.is_moving = False
                self.move_progress = 0
                # Aggiorna posizione finale
                self.pos = [
                    self.grid_x * self.tile_size + self.tile_size // 2,
                    self.grid_y * self.tile_size + self.tile_size // 2
                ]
            else:
                # Calcola posizione interpolata
                start_x = self.target_pos[0] * self.tile_size + self.tile_size//2
                start_y = self.target_pos[1] * self.tile_size + self.tile_size//2
                self.pos[0] = start_x + (self.grid_x - self.target_pos[0]) * self.tile_size * (self.move_progress/100)
                self.pos[1] = start_y + (self.grid_y - self.target_pos[1]) * self.tile_size * (self.move_progress/100)

def are_players_near(player1: Player, player2: Player) -> bool:
    # Calcola la distanza tra i due giocatori
    distance_x = abs(player1.pos[0] - player2.pos[0])
    distance_y = abs(player1.pos[1] - player2.pos[1])
    
    # Verifica se la distanza è inferiore alla somma delle dimensioni
    if distance_x < (player1.size + player2.size) and distance_y < (player1.size + player2.size):
        return True
    return False