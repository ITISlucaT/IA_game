import gymnasium as gym
from gymnasium import spaces
import numpy as np
import pygame as pg
from src.core.Game import MazeGame
import networkx as nx

class MazeEnv(gym.Env):
    metadata = {'render.modes': ['human', 'rgb_array'], 'render_fps': 60}

    def __init__(self):
        super(MazeEnv, self).__init__()
        
        # Inizializza il gioco
        self.game = MazeGame()
        
        # Definisci lo spazio delle azioni (discreto)
        self.action_space = spaces.Discrete(4)  # 0: UP, 1: DOWN, 2: LEFT, 3: RIGHT
        
        # Definisci lo spazio delle osservazioni (stato)
        # Esempio: posizione del giocatore, posizione del target, stato delle porte
        self.observation_space = spaces.Box(
            low=0, high=1, shape=(self.game.NUM_ROOMS * 2 + 4,), dtype=np.float32
        )
        
        # Inizializza lo stato
        self.state = self._get_state()
        
        # Variabili per il rendering
        self.screen = None
        self.clock = None

    def _get_state(self):
        """
        Ottieni lo stato corrente del gioco.
        Restituisce un array numpy che rappresenta lo stato.
        """
        # Esempio: posizione del giocatore, posizione del target, stato delle porte
        player_room = self.game.player1.current_room
        target_room = self.game.player2.current_room
        

        # Combina tutto in un unico array
        state = np.array([player_room, target_room], dtype=np.float32)
        return state

    def reset(self, seed=None, options=None):
        """
        Resetta l'ambiente e restituisce lo stato iniziale.
        """
        super().reset(seed=seed)
        
        # Resetta il gioco
        self.game = MazeGame()
        
        # Ottieni lo stato iniziale
        self.state = self._get_state()
        
        return self.state, {}

    def step(self, action):
        """
        Esegue un'azione e restituisce:
        - next_state: il nuovo stato
        - reward: la ricompensa ottenuta
        - done: se l'episodio è terminato
        - info: informazioni aggiuntive
        """
        # Esegui l'azione nel gioco
        self._take_action(action)
        
        # Ottieni il nuovo stato
        next_state = self._get_state()
        
        # Calcola la ricompensa
        reward = self._get_reward()
        
        # Controlla se l'episodio è terminato
        done = self.game.check_collision_between_player() or self.game.timer(1)
        
        # Info aggiuntive (opzionale)
        info = {}
        
        return next_state, reward, done, False, info

    def _take_action(self, action):
        """
        Esegue l'azione nel gioco.
        """
        # Mappa l'azione a una direzione
        action_map = {
            0: "UP",
            1: "DOWN",
            2: "LEFT",
            3: "RIGHT"
        }
        direction = action_map[action]
        
        # Esegui il movimento del giocatore
        current_room = self.game.rooms[self.game.player1.current_room]
        self.game.player1.move(direction, self.game.NUM_COLS, self.game.NUM_ROOMS, current_room)

    def _get_reward(self):
        """
        Calcola la ricompensa in base allo stato corrente.
        """
        reward = 0
        
        # Ricompensa positiva per avvicinarsi al target
        previous_distance = self.game.previous_distance_room
        current_distance = nx.shortest_path_length(
            self.game.graph, 
            self.game.player1.current_room, 
            self.game.player2.current_room
        )
        
        if current_distance < previous_distance:
            reward += 1  # Ricompensa per avvicinarsi
        # elif current_distance > previous_distance:
        #     reward -= 1  # Penalità per allontanarsi
        
        # Ricompensa per raggiungere il target
        if self.game.check_collision_between_player():
            reward += 10
        
        # Penalità per il tempo
        reward -= 0.1  # Piccola penalità per ogni passo

        metrics = self.game.player1.get_movement_metrics()
        
        # Penalize idle time
        idle_penalty = -0.1 * metrics['idle_time']
        
        # Reward movement
        reward  += 0.5 if metrics['is_moving'] else -0.2
        
        return reward

    def render(self, mode='human'):
        """
        Renderizza l'ambiente.
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
        Chiude l'ambiente e libera le risorse.
        """
        if self.screen is not None:
            pg.quit()
            self.screen = None