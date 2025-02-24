import pygame as pg
import numpy as np
from config import load_config
from src.world.Room import Room
from src.core.Player import Player
from src.world.generator import MazeGenerator

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
    
    def timer(self, duration_min = 5):
        duration_ticks = duration_min * 60 * 1000
        return (pg.time.get_ticks() - self.starting_time) >= duration_ticks

    def run(self):
        running = True
        clock = pg.time.Clock()
        
        while running:
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