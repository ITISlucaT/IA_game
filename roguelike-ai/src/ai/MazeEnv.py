import gymnasium as gym
from gymnasium import spaces
import numpy as np
import pygame as pg
from src.core.Game import MazeGame
import networkx as nx
import random

class MazeEnv(gym.Env):
    metadata = {'render.modes': ['human', 'rgb_array'], 'render_fps': 60}

    def __init__(self):
        super(MazeEnv, self).__init__()
        
        # Initialize the game
        self.game = MazeGame()
        
        # Define action space (discrete)
        self.action_space = spaces.Discrete(4)  # 0: UP, 1: DOWN, 2: LEFT, 3: RIGHT
        
        # Define observation space
        # Now using more comprehensive state representation
        self.observation_space = spaces.Box(
            low=0, high=self.game.NUM_ROOMS - 1, 
            shape=(2,),  # Player 1 and Player 2 current rooms
            dtype=np.int32
        )
        
        # Initialize the state
        self.state = self._get_state()
        
        # Rendering variables
        self.screen = None
        self.clock = None

    def _get_state(self):
        """
        Get the current state of the game.
        Returns a numpy array representing the current rooms of both players.
        """
        return np.array([
            self.game.player1.current_room, 
            self.game.player2.current_room
        ], dtype=np.int32)

    def reset(self, seed=None, options=None):
        """
        Reset the environment and return the initial state.
        """
        super().reset(seed=seed)
        
        # Reset the game
        self.game = MazeGame()
        
        # Get initial state
        self.state = self._get_state()
        
        return self.state, {}

    def step(self, action, player):
        """
        Execute an action and return:
        - next_state: the new state
        - reward: the reward obtained
        - done: if the episode is terminated
        - info: additional information
        """
        reward = 0
        if self.unauthorized_moves(action=action, player=player):
            reward -= 5
        # elif self.unauthorized_moves(action=action, player=self.game.player2):
        #     reward -= 15
        #print(f"[DEBUG]reward: {reward}")
        # Execute the action for player1
        self._move_player(player, action)
        
        # Move player2 using a separate strategy 
        #self._move_player(self.game.player2, action)
        #self._move_player2()
        
        # Get the new state
        next_state = self._get_state()
        #print(next_state)
        
        # Calculate the reward
        reward += self._get_reward(action)
        
        # Check if the episode is terminated
        done = self.game.check_collision_between_player() or self.game.timer(1)
        
        # Additional info (optional)
        info = {}
        
        return next_state, reward, done, False, info

    def _move_player(self, player, action):
        """
        Execute movement for a given player based on the action.
        """
        # Map the action to a direction
        action_map = {
            0: "UP",
            1: "DOWN", 
            2: "LEFT", 
            3: "RIGHT"
        }
        direction = action_map[action]
        
        # Get available moves from the current room
        available_moves = list(self.game.graph.neighbors(player.current_room))
        
        # Determine target room based on direction
        target_room = None
        if direction == "UP" and (player.current_room - self.game.NUM_COLS) in available_moves:
            target_room = player.current_room - self.game.NUM_COLS
        elif direction == "DOWN" and (player.current_room + self.game.NUM_COLS) in available_moves:
            target_room = player.current_room + self.game.NUM_COLS
        elif direction == "LEFT" and (player.current_room - 1) in available_moves:
            target_room = player.current_room - 1
        elif direction == "RIGHT" and (player.current_room + 1) in available_moves:
            target_room = player.current_room + 1
        
        # If a valid move is found, move the player
        if target_room is not None:
            # Update player's room
            player.current_room = target_room
            
            # Reset grid position to center of the new room
            target_room_obj = self.game.rooms[target_room]
            player.grid_x = (target_room_obj.grid_size) // 2
            player.grid_y = (target_room_obj.grid_size) // 2
            
            # Update absolute position
            player.pos = [
                player.grid_x * player.tile_size + player.tile_size // 2,
                player.grid_y * player.tile_size + player.tile_size // 2
            ]

    def _move_player2(self):
        """
        Move player2 using a strategy to approach player1.
        """
        player1 = self.game.player1
        player2 = self.game.player2
        
        # Find the shortest path to player1's room
        try:
            path = nx.shortest_path(
                self.game.graph, 
                player2.current_room, 
                player1.current_room
            )
            
            # If path exists and is longer than 1 (not same room)
            if len(path) > 1:
                # Move to the next room in the path
                target_room = path[1]
                
                # Update player's room
                player2.current_room = target_room
                
                # Reset grid position to center of the new room
                target_room_obj = self.game.rooms[target_room]
                player2.grid_x = (target_room_obj.grid_size) // 2
                player2.grid_y = (target_room_obj.grid_size) // 2
                
                # Update absolute position
                player2.pos = [
                    player2.grid_x * player2.tile_size + player2.tile_size // 2,
                    player2.grid_y * player2.tile_size + player2.tile_size // 2
                ]
        except nx.NetworkXNoPath:
            # If no path exists, choose a random neighboring room
            available_moves = list(self.game.graph.neighbors(player2.current_room))
            if available_moves:
                target_room = random.choice(available_moves)
                
                # Update player's room
                player2.current_room = target_room
                
                # Reset grid position to center of the new room
                target_room_obj = self.game.rooms[target_room]
                player2.grid_x = (target_room_obj.grid_size) // 2
                player2.grid_y = (target_room_obj.grid_size) // 2
                
                # Update absolute position
                player2.pos = [
                    player2.grid_x * player2.tile_size + player2.tile_size // 2,
                    player2.grid_y * player2.tile_size + player2.tile_size // 2
                ]

    def _get_reward(self, action):
        """
        Calculate the reward based on the current state.
        """
        reward = 0

        previous_distance = self.game.previous_distance_room
        current_distance = nx.shortest_path_length(
            self.game.graph, 
            self.game.player1.current_room, 
            self.game.player2.current_room
        )
        
        # Ricompensa proporzionale all'avvicinamento
        if current_distance < previous_distance:
            reward += 3  # prima era solo +1
        elif current_distance > previous_distance:
            reward -= 1  # punizione per allontanamento

        # Raggiunto il target
        if self.game.check_collision_between_player():
            reward += 50  # era 10 ora più incisivo per favorire l’obiettivo

        reward -= 0.02

        # Penalità per stare fermo
        metrics = self.game.player1.get_movement_metrics()
        if not metrics['is_moving']:
            reward -= 0.5  # più significativa per evitare idle

        return reward

    
    def unauthorized_moves(self, action, player):
        action_map = {
            0: "UP",
            1: "DOWN", 
            2: "LEFT", 
            3: "RIGHT",
            4: "STOP"
        }
        direction = action_map[action]

        if direction == "UP":
            target_room = player.current_room - self.game.NUM_COLS
        elif direction == "DOWN":
            target_room = player.current_room + self.game.NUM_COLS
        elif direction == "LEFT":
            target_room = player.current_room - 1
        elif direction == "RIGHT":
            target_room = player.current_room + 1

        if target_room in self.game.graph.neighbors(player.current_room):
            return False
        else:
            return True

    def render(self, mode='human'):
        """
        Render the environment.
        """
        if mode == 'human':
            if self.screen is None:
                pg.init()
                self.screen = pg.display.set_mode((self.game.WIDTH, self.game.HEIGHT))
                self.clock = pg.time.Clock()
            
            self.game.draw()
            pg.display.flip()
            self.clock.tick(self.metadata['render_fps'])
        
        elif mode == 'rgb_array':
            return pg.surfarray.array3d(self.game.screen)

    def close(self):
        """
        Close the environment and free resources.
        """
        if self.screen is not None:
            pg.quit()
            self.screen = None