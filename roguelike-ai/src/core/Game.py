import pygame as pg
import numpy as np
import networkx as nx
from config import load_config
from src.world.Room import Room
from src.core.Player import Player
from src.world.generator import MazeGenerator
import math

class MazeGame:
    def __init__(self):
        pg.init()
        self.starting_time = pg.time.get_ticks()
        self.config = load_config()
        self.WIDTH = self.config['display']['width']
        self.HEIGHT = self.config['display']['height']
        self.NUM_ROWS = self.config['maze']['min_rows']
        self.NUM_COLS = self.config['maze']['min_cols']
        self.NUM_ROOMS = self.NUM_ROWS * self.NUM_COLS
        self.ROOM_SIZE = min(self.WIDTH // self.NUM_COLS, self.HEIGHT // self.NUM_ROWS)
        self.COLORS = {
            color: tuple(values) for color, values in self.config['colors'].items()
        }
        
        self.screen = pg.display.set_mode((self.WIDTH, self.HEIGHT), pg.RESIZABLE)
        pg.display.set_caption(self.config['display']['caption'])
        
        self.maze_generator = MazeGenerator(self.NUM_ROWS, self.NUM_COLS)
        self.graph = self.maze_generator.generate_grid_graph(self.NUM_ROWS, self.NUM_COLS)
        self.rooms = self._create_rooms()
        self.size = self.NUM_ROOMS * self.ROOM_SIZE
        #print(self.maze_generator.get_neighbors(11))
        # Configure doors for each room based on the maze graph
        self._setup_room_doors()
        player1_room, player2_room = np.random.choice(np.arange(0, self.NUM_ROOMS ), size=2, replace=False)
        self.player1 = Player(self.ROOM_SIZE, self.NUM_ROOMS, self.config, 'blue', player1_room)
        self.player2 = Player(self.ROOM_SIZE, self.NUM_ROOMS, self.config, 'red', player2_room)
        self.previous_distance_room = nx.shortest_path_length(self.graph, self.player1.current_room, self.player2.current_room)
        self.previous_distance = 10000
        self.last_move_time = 0
        self.move_delay = 200  # Millisecondi tra i movimenti
        self.unauthorized_movement = False

    def _create_rooms(self):
        tile_size = self.config['tile_size']
        return [Room(c * self.ROOM_SIZE,
                    r * self.ROOM_SIZE,
                    self.ROOM_SIZE,
                    r * self.NUM_COLS + c,
                    tile_size)
                for r in range(self.NUM_ROWS)
                for c in range(self.NUM_COLS)]

    def _setup_room_doors(self):
        """Configure doors for each room based on the maze graph."""
        for room in self.rooms:
            room.setup_doors(self.NUM_COLS, self.NUM_ROWS, list(self.graph.neighbors(room.room_number)))

    def handle_input(self):
        current_time = pg.time.get_ticks()
        if current_time - self.last_move_time < self.move_delay:
            return

        keys = pg.key.get_pressed()
        moved = False
        unauthorized_movement = False  # Nuova variabile per tenere traccia

        # Player 1 movement (ARROW KEYS)
        moved_p1, unauthorized_p1 = self._handle_player_movement(
            self.player1, 
            {
                'UP': pg.K_UP, 
                'DOWN': pg.K_DOWN, 
                'LEFT': pg.K_LEFT, 
                'RIGHT': pg.K_RIGHT
            }
        )
        moved |= moved_p1
        unauthorized_movement |= unauthorized_p1  # OR per mantenere il flag

        # Check unauthorized movement for Player 1
        available_moves_p1 = list(self.graph.neighbors(self.player1.current_room))
        # if not self.check_unauthorized_movement(self.player1, available_moves_p1):
        #     unauthorized_movement = True

        # Player 2 movement (WASD KEYS)
        moved_p2, unauthorized_p2 = self._handle_player_movement(
            self.player2, 
            {
                'UP': pg.K_w, 
                'DOWN': pg.K_s, 
                'LEFT': pg.K_a, 
                'RIGHT': pg.K_d
            }
        )
        moved |= moved_p2
        unauthorized_movement |= unauthorized_p2  # OR per mantenere il flag

        # Check unauthorized movement for Player 2
        available_moves_p2 = list(self.graph.neighbors(self.player2.current_room))
        # if not self.check_unauthorized_movement(self.player2, available_moves_p2):
        #     unauthorized_movement = True

        if moved:
            self.last_move_time = current_time
        
        self.unauthorized_movement = unauthorized_movement


    def _handle_player_movement(self, player, key_map):
        """
        Handle movement for a specific player with given key mappings.
        
        Args:
            player (Player): The player to move
            key_map (dict): Mapping of movement directions to Pygame key constants
        
        Returns:
            tuple: (bool: movement occurred, bool: unauthorized movement detected)
        """
        keys = pg.key.get_pressed()
        available_moves = list(self.graph.neighbors(player.current_room))
        moved = False
        unauthorized_movement = False

        # Up movement
        if keys[key_map['UP']]:
            self._move_player_between_rooms(player, "UP")
            moved = True
        
        # Down movement
        if keys[key_map['DOWN']]:
            self._move_player_between_rooms(player, "DOWN")
            moved = True
        
        # Left movement
        if keys[key_map['LEFT']]:
            self._move_player_between_rooms(player, "LEFT")
            moved = True
        
        # Right movement
        if keys[key_map['RIGHT']]:
            self._move_player_between_rooms(player, "RIGHT")
            moved = True

        # Check unauthorized movement
        # if self.check_unauthorized_movement(player, available_moves):
        #     unauthorized_movement = True

        return moved, unauthorized_movement


    # def check_unauthorized_movement(self, player, available_moves):
    #     """
    #     Check if the player is trying to move to an unauthorized room.
        
    #     Args:
    #         player (Player): The player to check
    #         available_moves (list): List of available moves for the player
        
    #     Returns:
    #         bool: True if the move is unauthorized, False otherwise
    #     """
    #     return player.current_room not in available_moves

    def _move_player_between_rooms(self, player, direction):
        """
        Move player between rooms based on the graph's connections.
        
        Args:
            player (Player): The player to move
            direction (str): Direction of movement
        """
        current_room = self.rooms[player.current_room]
        
        # Determine target room based on direction
        if direction == "UP":
            target_room = player.current_room - self.NUM_COLS
        elif direction == "DOWN":
            target_room = player.current_room + self.NUM_COLS
        elif direction == "LEFT":
            target_room = player.current_room - 1
        elif direction == "RIGHT":
            target_room = player.current_room + 1
        print(self.graph)
        # Validate target room index
        if target_room not in self.maze_generator.get_neighbors(player.current_room):
            return  # Prevent moving to an invalid room
        if target_room in self.graph.neighbors(player.current_room):
            print("authorized")
        else:
            print("Unauthorized")
              
        
        # Update player's room and grid position
        player.current_room = target_room
        target_room_obj = self.rooms[target_room]
        
        # Reset grid position to center of the new room
        player.grid_x = (target_room_obj.grid_size) // 2
        player.grid_y = (target_room_obj.grid_size) // 2
        
        # Update absolute position
        player.pos = [
            player.grid_x * player.tile_size + player.tile_size // 2,
            player.grid_y * player.tile_size + player.tile_size // 2
        ]
        # self.check_last_move_authorization() 
        # Mark that the room has changed
        player.room_changed = True
    def draw(self):
        self.screen.fill(self.COLORS['white'])
        for room in self.rooms:
            room.draw(self.screen, self.NUM_COLS, self.NUM_ROWS, self.COLORS)
        self.player1.draw(self.screen, self.NUM_COLS, self.COLORS)
        self.player2.draw(self.screen, self.NUM_COLS, self.COLORS)
        pg.display.flip()
            
    def check_collision_between_player(self):
        if self.player1.current_room == self.player2.current_room:
            return (self.player1.grid_x == self.player2.grid_x and 
                    self.player1.grid_y == self.player2.grid_y)
        return False
    
    def check_collision_with_wall(self, player):
        current_room = self.rooms[player.current_room]
        
        # Check if the player is trying to move outside the borders
        if (player.grid_x < 0 or player.grid_x >= current_room.grid_size or
            player.grid_y < 0 or player.grid_y >= current_room.grid_size):
            
            # Determina la direzione del movimento
            direction = None
            if player.grid_x < 0:
                direction = 'left'
            elif player.grid_x >= current_room.grid_size:
                direction = 'right'
            elif player.grid_y < 0:
                direction = 'top'
            elif player.grid_y >= current_room.grid_size:
                direction = 'bottom'
            
            # Controlla se c'è una porta valida in quella direzione
            if direction and not current_room.can_pass_through(player.grid_x, player.grid_y, direction):
                return True  # Collisione con un muro senza porta
        
        return False
    
    def timer(self, duration_min = 5):
        duration_ticks = duration_min * 60 * 1000
        return (pg.time.get_ticks() - self.starting_time) >= duration_ticks
    
    #def penalties(self):

        #metodo per vedere se i giocatori si avvcinano fra loro
    def player_getting_closer(self):
        if self.player1.current_room == self.player2.current_room:
            x1, y1 = self.player1.pos
            x2, y2 = self.player2.pos

            distanza_attuale = math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)

            
            if distanza_attuale < self.previous_distance:
                self.previous_distance = distanza_attuale
                return True
            else:
                self.previous_distance = distanza_attuale
                return False
        else:
            distanza_attuale = nx.shortest_path_length(self.graph, self.player1.current_room, self.player2.current_room)
            if distanza_attuale < self.previous_distance:
                self.previous_distance = distanza_attuale
                return True
            else:
                self.previous_distance = distanza_attuale
                return False
            
    def player_doing_unauthorized_move(self):
        
        return self.unauthorized_movement
            
    def player_changing_room(self):
        ret = (self.player1.room_changed, self.player2.room_changed)
        self.player1.room_changed = False
        self.player2.room_changed = False
        return ret


    # def check_last_move_authorization(self):
    #     """
    #     Check if the last move made by the player was authorized.
    #     """
       
    #     available_moves = list(self.graph.neighbors(self.player1.current_room))
    #     if self.check_unauthorized_movement(self.player1, available_moves):
    #         print(f"Player 1 in room {self.player1.current_room} made an unauthorized move.")
        
    #     print(f"Player 1 available moves: {available_moves}")


    #     available_moves = list(self.graph.neighbors(self.player2.current_room))
    #     if self.check_unauthorized_movement(self.player2, available_moves):
    #         print(f"Player 2 in room {self.player2.current_room} made an unauthorized move.")


    def run(self):
        running = True
        clock = pg.time.Clock()
        print(self.player1.check_unauthorized_movement(list(self.graph.neighbors(self.player1.current_room))))
        
        while running:
            dt = clock.tick(60)  # Delta time in milliseconds
        
            # Update player animations
            self.player1.update(dt)
            self.player2.update(dt)


            # print(f"[DEBUG]pl1 available move")
            # print(list(self.graph.neighbors(self.player1.current_room)))
            # print(f"[DEBUG]pl2 available move")
            # print(list(self.graph.neighbors(self.player2.current_room)))


            # if self.player1.check_last_move_authorization(list(self.graph.neighbors(self.player1.current_room))):
            #     print(f"Player 1 in room {self.player1.current_room} made an unauthorized move")
            # if self.player2.check_last_move_authorization(list(self.graph.neighbors(self.player2.current_room))):
            #     print(f"Player 2 in room {self.player2.current_room} made an unauthorized move")


            ret = self.player_changing_room()
            if ret[0]:
                print("player 1 ha cambiato stanza")
            if ret[1]:
                print("player 2 ha cambiato stanza")
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    running = False

            if self.check_collision_between_player():
                print("game won")
                running = False
            if self.timer(1):
                print("game lost")
                running = False 

            self.handle_input()
            
            self.draw()
            clock.tick(60)  # Limit to 60 FPS
            
        pg.quit()