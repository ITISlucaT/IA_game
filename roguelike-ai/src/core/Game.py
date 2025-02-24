import pygame as pg
import numpy as np
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
        self.NUM_ROWS = np.random.randint(
            self.config['maze']['min_rows'],
            self.config['maze']['max_rows']
        )
        self.NUM_COLS = np.random.randint(
            self.config['maze']['min_cols'],
            self.config['maze']['max_cols']
        )
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
        
        # Configure doors for each room based on the maze graph
        self._setup_room_doors()
        
        self.player1 = Player(self.ROOM_SIZE, self.NUM_ROOMS, self.config)
        self.player2 = Player(self.ROOM_SIZE, self.NUM_ROOMS, self.config)
        self.previous_distance = 10000

    def _create_rooms(self):
        return [Room(c * self.ROOM_SIZE,
                    r * self.ROOM_SIZE,
                    self.ROOM_SIZE,
                    r * self.NUM_COLS + c)
                for r in range(self.NUM_ROWS)
                for c in range(self.NUM_COLS)]

    def _setup_room_doors(self):
        """Configure doors for each room based on the maze graph."""
        for room in self.rooms:
            room.setup_doors(self.NUM_COLS, self.NUM_ROWS, self.graph[room.room_number])

    def draw(self):
        self.screen.fill(self.COLORS['white'])
        for room in self.rooms:
            room.draw(self.screen, self.NUM_COLS, self.NUM_ROWS, self.COLORS)
        self.player1.draw(self.screen, self.NUM_COLS, self.COLORS)
        self.player2.draw(self.screen, self.NUM_COLS, self.COLORS)
        pg.display.flip()

    def handle_input(self):
        keys = pg.key.get_pressed()
        current_room = self.rooms[self.player1.current_room]
        
        if keys[pg.K_UP]:
            self.player1.move("UP", self.NUM_COLS, self.NUM_ROOMS, current_room)
        if keys[pg.K_DOWN]:
            self.player1.move("DOWN", self.NUM_COLS, self.NUM_ROOMS, current_room)
        if keys[pg.K_LEFT]:
            self.player1.move("LEFT", self.NUM_COLS, self.NUM_ROOMS, current_room)
        if keys[pg.K_RIGHT]:
            self.player1.move("RIGHT", self.NUM_COLS, self.NUM_ROOMS, current_room)

        current_room = self.rooms[self.player2.current_room]
        # muovo il giocatore con le freccette
        if keys[pg.K_w]:
            self.player2.move("UP", self.NUM_COLS, self.NUM_ROOMS, current_room)
        if keys[pg.K_s]:
            self.player2.move("DOWN", self.NUM_COLS, self.NUM_ROOMS, current_room)
        if keys[pg.K_a]:
            self.player2.move("LEFT", self.NUM_COLS, self.NUM_ROOMS, current_room)
        if keys[pg.K_d]:
            self.player2.move("RIGHT", self.NUM_COLS, self.NUM_ROOMS, current_room)
        
    def check_collision_between_player(self):
        if self.player1.current_room == self.player2.current_room:
            distanza_quadrata = (self.player2.pos[0] - self.player1.pos[0]) ** 2 + (self.player2.pos[1] - self.player1.pos[1]) ** 2
            r_somma_quadrato = (self.player1.size + self.player2.size) ** 2
            return distanza_quadrata <= r_somma_quadrato
        return False
    
    def check_collision_with_wall(self, player):
        """
        Check if a player is colliding with a wall in the current room.
        
        Args:
            player: Player object to check for collisions
            
        Returns:
            bool: True if collision with wall detected, False otherwise
        """
        current_room = self.rooms[player.current_room]
        room_col = player.current_room % self.NUM_COLS
        room_row = player.current_room // self.NUM_COLS
        
        # Calculate absolute position in the screen coordinates
        abs_x = room_col * self.ROOM_SIZE + player.pos[0]
        abs_y = room_row * self.ROOM_SIZE + player.pos[1]
        
        # Check collision with room boundaries
        collision = False
        
        # Check left wall
        if player.pos[0] - player.size <= 0:
            # Check if there's a door and if the player can pass through it
            if not current_room.can_pass_through((player.pos[0], player.pos[1]), 'left'):
                collision = True
        
        # Check right wall
        if player.pos[0] + player.size >= self.ROOM_SIZE:
            if not current_room.can_pass_through((player.pos[0], player.pos[1]), 'right'):
                collision = True
        
        # Check top wall
        if player.pos[1] - player.size <= 0:
            if not current_room.can_pass_through((player.pos[0], player.pos[1]), 'top'):
                collision = True
        
        # Check bottom wall
        if player.pos[1] + player.size >= self.ROOM_SIZE:
            if not current_room.can_pass_through((player.pos[0], player.pos[1]), 'bottom'):
                collision = True
        
        return collision

    
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
            
    def player_changing_room(self):
        ret = (self.player1.room_changed, self.player2.room_changed)
        self.player1.room_changed = False
        self.player2.room_changed = False
        return ret


    def run(self):
        running = True
        clock = pg.time.Clock()
        
        while running:
            if self.check_collision_with_wall(self.player1):
                print("Muro toccato")
            if self.player1.is_moving_in_a_step(5000):
                print("Giocatore 1 muove")
            else:
                print("Giocatore 1 non muove")

            if self.player_getting_closer():
                print("Giocatori si avvicinano")
            else:
                print("Giocatori non si avvicinano")

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
            # Check if player1 has reached player2 based on their positions x(Player.pos[0]) and y(Player.pos[1]), considering their size
            # if (abs(self.player1.pos[0] - self.player2.pos[0]) <= self.player1.size and abs(self.player1.pos[1] - self.player2.pos[1]) <= self.player1.size):
            #     print("game winned")
            #     running = False
            

            self.handle_input()
            self.draw()
            clock.tick(60)  # Limit to 60 FPS
            
        pg.quit()