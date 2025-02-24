import gymnasium as gym
from gymnasium import spaces
import numpy as np
from src.core.Game import MazeGame  # Assumendo che MazeGame sia definito in un file separato

class MazeEnv(gym.Env):
    metadata = {"render_modes": ["human"]}

    def __init__(self):
        super().__init__()
        self.game = MazeGame()
        
        size = max(self.game.NUM_ROWS, self.game.NUM_COLS)  # Definisci la size del tuo spazio
        self.observation_space = spaces.Dict(
            {
                "agent": spaces.Box(0, size - 1, shape=(2,), dtype=int),
                "target": spaces.Box(0, size - 1, shape=(2,), dtype=int),
            }
        )

        self.action_space = spaces.Discrete(4)  # Azioni: su, giù, sinistra, destra
        self.score = 0

    def step(self, action):
        if action == 0:
            self.game.player1.move("UP", self.game.NUM_COLS, self.game.NUM_ROOMS, self.game.rooms[self.game.player1.current_room])
        elif action == 1:
            self.game.player1.move("DOWN", self.game.NUM_COLS, self.game.NUM_ROOMS, self.game.rooms[self.game.player1.current_room])
        elif action == 2:
            self.game.player1.move("LEFT", self.game.NUM_COLS, self.game.NUM_ROOMS, self.game.rooms[self.game.player1.current_room])
        elif action == 3:
            self.game.player1.move("RIGHT", self.game.NUM_COLS, self.game.NUM_ROOMS, self.game.rooms[self.game.player1.current_room])
            
        
        done = self.game.check_collision_between_player()  # Fine episodio se i giocatori si incontrano
        
        reward = 0

        if self.game.check_collision_with_wall(self.game.player1):
            reward += -0.3
        if self.game.player_getting_closer():
            reward += 1
        else:
            reward += -1
        if self.game.player_changing_room():
            reward += 0.5
        if done:
            reward += 10

        self.score += reward

        return self._get_obs(), reward, done, False, {}

    def reset(self, seed=None, options=None):
        super().reset(seed=seed)
        self.game = MazeGame()
        return self._get_obs(), {}

    def _get_obs(self):
        return {
            "agent": np.array([self.game.player1.pos[0], self.game.player1.pos[1]], dtype=int),
            "target": np.array([self.game.player2.pos[0], self.game.player2.pos[1]], dtype=int),
        }

    def render(self):
        self.game.draw()

    def close(self):
        pass
