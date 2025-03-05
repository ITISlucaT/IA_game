import pygame as pg
from typing import Dict, Tuple, List

class Room:
    def __init__(self, x: int, y: int, size: int, room_number: int, tile_size: int):
        self.tile_size = tile_size
        self.grid_size = size // tile_size
        self.x = x
        self.y = y
        self.size = size
        self.room_number = room_number
        # Dizionario per tenere traccia delle porte e delle loro posizioni
        self.doors: Dict[str, Dict] = {
            'right': {'exists': False, 'range': (0, 0)},
            'bottom': {'exists': False, 'range': (0, 0)},
            'left': {'exists': False, 'range': (0, 0)},
            'top': {'exists': False, 'range': (0, 0)}
        }

    def setup_doors(self, num_cols: int, num_rows: int, neighbours: list) -> None:
        """Configura le porte basandosi sulla posizione della stanza nel labirinto."""
        door_size = self.size // 8  # Dimensione della porta (1/8 della stanza)
        door_start = (self.size // 2) - (door_size // 2)
        door_end = (self.size // 2) + (door_size // 2)

        # Porta destra
        if (self.room_number + 1) in neighbours:
            self.doors['right'] = {
                'exists': True,
                'range': (door_start, door_end)
            }

        # Porta in basso
        if (self.room_number + num_cols) in neighbours:
            self.doors['bottom'] = {
                'exists': True,
                'range': (door_start, door_end)
            }

        # Porta sinistra
        if (self.room_number - 1) in neighbours:
            self.doors['left'] = {
                'exists': True,
                'range': (door_start, door_end)
            }

        # Porta in alto
        if (self.room_number - num_cols) in neighbours:
            self.doors['top'] = {
                'exists': True,
                'range': (door_start, door_end)
            }
    def can_pass_through(self, grid_x: int, grid_y: int, direction: str) -> bool:
        """
        Verifica se il giocatore può passare attraverso una porta nella direzione specificata.
        
        Args:
            grid_x (int): Posizione X del giocatore nella griglia della stanza.
            grid_y (int): Posizione Y del giocatore nella griglia della stanza.
            direction (str): Direzione del movimento ('right', 'left', 'top', 'bottom').
        
        Returns:
            bool: True se il giocatore è allineato con una porta, False altrimenti.
        """
        if not self.doors[direction]['exists']:
            return False  # Non c'è una porta in questa direzione

        # Ottieni l'intervallo della porta
        door_start, door_end = self.doors[direction]['range']
        tile_size = self.size // self.grid_size

        # Converti le coordinate della porta in coordinate della griglia
        door_start_grid = door_start // tile_size
        door_end_grid = door_end // tile_size

        # Controlla se il giocatore è allineato con la porta
        if direction in ['right', 'left']:
            # Porte a destra/sinistra: il giocatore deve essere allineato verticalmente
            return door_start_grid <= grid_y <= door_end_grid
        else:
            # Porte in alto/basso: il giocatore deve essere allineato orizzontalmente
            return door_start_grid <= grid_x <= door_end_grid

    def draw(self, surface, num_cols: int, num_rows: int, colors: Dict):
        """Disegna la stanza con le sue porte."""
        self._draw_grid(surface, colors['black'])
        # Disegna il bordo della stanza
        pg.draw.rect(surface, colors['green'], (self.x, self.y, self.size, self.size), 1)
        
        # Disegna il numero della stanza
        font = pg.font.SysFont(None, 36)
        text = font.render(str(self.room_number), True, colors['black'])
        surface.blit(text, (self.x + 30, self.y + 30))

        # Assicurati che le porte siano configurate
        if not any(door['exists'] for door in self.doors.values()):
            self.setup_doors(num_cols, num_rows)

        # Disegna le porte
        self._draw_doors(surface, colors)

    def _draw_grid(self, surface, color):
        """Disegna la griglia delle tile nella stanza"""
        for x in range(0, self.size, self.tile_size):
            pg.draw.line(surface, color, (self.x + x, self.y), (self.x + x, self.y + self.size))
        for y in range(0, self.size, self.tile_size):
            pg.draw.line(surface, color, (self.x, self.y + y), (self.x + self.size, self.y + y))


    def _draw_doors(self, surface, colors: Dict):
        """Disegna le porte della stanza."""
        # Porta destra
        if self.doors['right']['exists']:
            door_start, door_end = self.doors['right']['range']
            pg.draw.rect(surface, colors['white'],
                        (self.x + self.size, self.y + door_start, 10, door_end - door_start))
            pg.draw.line(surface, colors['red'],
                        (self.x + self.size, self.y + door_start),
                        (self.x + self.size, self.y + door_end), 5)

        # Porta in basso
        if self.doors['bottom']['exists']:
            door_start, door_end = self.doors['bottom']['range']
            pg.draw.rect(surface, colors['white'],
                        (self.x + door_start, self.y + self.size, door_end - door_start, 10))
            pg.draw.line(surface, colors['red'],
                        (self.x + door_start, self.y + self.size),
                        (self.x + door_end, self.y + self.size), 5)

    def get_door_positions(self) -> Dict[str, Tuple[int, int, int, int]]:
        """
        Restituisce le posizioni delle porte per il rilevamento delle collisioni.
        Returns:
            Dict[str, Tuple[int, int, int, int]]: Dizionario con posizioni delle porte
        """
        door_positions = {}
        for direction, door in self.doors.items():
            if door['exists']:
                if direction == 'right':
                    door_positions[direction] = (
                        self.x + self.size,
                        self.y + door['range'][0],
                        10,
                        door['range'][1] - door['range'][0]
                    )
                elif direction == 'bottom':
                    door_positions[direction] = (
                        self.x + door['range'][0],
                        self.y + self.size,
                        door['range'][1] - door['range'][0],
                        10
                    )
                elif direction == 'left':
                    door_positions[direction] = (
                        self.x - 10,
                        self.y + door['range'][0],
                        10,
                        door['range'][1] - door['range'][0]
                    )
                elif direction == 'top':
                    door_positions[direction] = (
                        self.x + door['range'][0],
                        self.y - 10,
                        door['range'][1] - door['range'][0],
                        10
                    )
        return door_positions