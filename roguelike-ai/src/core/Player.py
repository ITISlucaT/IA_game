import pygame as pg
import numpy as np
from typing import List, Dict

class Player:
    def __init__(self, room_size: int, num_rooms: int, config: Dict):
        self.current_room = np.random.randint(0, num_rooms)
        self.pos = [room_size // 2, room_size // 2]
        self.room_size = room_size
        self.speed = config['player']['speed']
        self.size = config['player']['size']
        self.direction = "left"
        self.last_movement_time = 0
        self.previous_room = self.current_room
        self.room_changed = False

    def draw(self, surface, num_cols: int, colors: Dict):
        room_row = self.current_room // num_cols
        room_col = self.current_room % num_cols
        x = room_col * self.room_size + self.pos[0]
        y = room_row * self.room_size + self.pos[1]
        pg.draw.circle(surface, colors['blue'], (x, y), self.size)

    def move(self, direction: str, num_cols: int, num_rooms: int, current_room: 'Room'):
        # Store the current position before moving
        old_pos = self.pos.copy()
        
        # Try to move in the requested direction
        if direction == "UP":
            self.pos[1] = max(0, self.pos[1] - self.speed)
        elif direction == "DOWN":
            self.pos[1] = min(self.room_size, self.pos[1] + self.speed)
        elif direction == "LEFT":
            self.pos[0] = max(0, self.pos[0] - self.speed)
        elif direction == "RIGHT":
            self.pos[0] = min(self.room_size, self.pos[0] + self.speed)

        # Check if we can pass through in the current direction
        can_pass = True
        if self.pos[0] <= 0:
            can_pass = current_room.can_pass_through((old_pos[0], old_pos[1]), 'left')
        elif self.pos[0] >= self.room_size:
            can_pass = current_room.can_pass_through((old_pos[0], old_pos[1]), 'right')
        elif self.pos[1] <= 0:
            can_pass = current_room.can_pass_through((old_pos[0], old_pos[1]), 'top')
        elif self.pos[1] >= self.room_size:
            can_pass = current_room.can_pass_through((old_pos[0], old_pos[1]), 'bottom')

        # If we can't pass through, revert to the old position
        if not can_pass:
            self.pos = old_pos
        else:
            # Only handle room transition if we can pass through
            self._handle_room_transition(num_cols, num_rooms)
        
        self.player_is_moving = self.pos[0] != old_pos[0] or self.pos[1] != old_pos[1]

    def _handle_room_transition(self, num_cols: int, num_rooms: int):
        if self.pos[0] <= 0 and self.current_room % num_cols != 0:
            self.current_room -= 1
            self.pos[0] = self.room_size
        elif self.pos[0] >= self.room_size and self.current_room % num_cols != num_cols - 1:
            self.current_room += 1
            self.pos[0] = 0
        elif self.pos[1] <= 0 and self.current_room >= num_cols:
            self.current_room -= num_cols
            self.pos[1] = self.room_size
        elif self.pos[1] >= self.room_size and self.current_room < num_rooms - num_cols:
            self.current_room += num_cols
            self.pos[1] = 0

        if self.previous_room == self.current_room:
            self.room_changed = False
        else:
            self.room_changed = True

    def is_moving(self):
        """
        Determines if the player is currently moving based on velocity or action state.
        This method is designed to be compatible with OpenAI Gym environments.
        
        Returns:
            bool: True if the player is moving, False otherwise
        """

        # Option 3: Check movement based on position delta
        if hasattr(self, 'last_position'):
            current_pos = self.pos.copy()
            is_moving = current_pos != self.last_position
            self.last_position = current_pos  # Update last position for next check
            return is_moving
        
        # If none of the above attributes exist, initialize last_position
        else:
            self.last_position = self.pos.copy()
            return False
        
    def is_moving_in_a_step(self, time):
        """
        Check if the player is moving in the last 'time' milliseconds.
        
        Args:
            time: int - Time window in milliseconds to check for movement
            
        Returns:
            bool: True if the player has been moving within the specified time window, False otherwise
        """
        current_moving = self.is_moving()

        current_time = pg.time.get_ticks()
        
        if not hasattr(self, 'last_movement_time'):
            self.last_movement_time = current_time if current_moving else 0
        
        if current_moving:
            self.last_movement_time = current_time
        
        # Check if the player has been moving within the specified time window
        return (current_moving or (current_time - self.last_movement_time) < time)
        
def are_players_near(player1: Player, player2: Player) -> bool:
    # Calcola la distanza tra i due giocatori
    distance_x = abs(player1.x - player2.x)
    distance_y = abs(player1.y - player2.y)
    
    # Verifica se la distanza è inferiore alla somma delle dimensioni
    if distance_x < (player1.size + player2.size) and distance_y < (player1.size + player2.size):
        return True
    return False