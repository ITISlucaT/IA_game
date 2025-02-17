import pygame as pg
from typing import Dict, Tuple, List

class Room:
    def __init__(self, x: int, y: int, size: int, room_number: int):
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
        col = self.room_number % num_cols
        row = self.room_number // num_rows

        # Porta destra
        if (self.room_number + 1) in neighbours:
            door_start = self.size // 4
            door_end = self.size * 3 // 4
            self.doors['right'] = {
                'exists': True,
                'range': (door_start, door_end)
            }

        # Porta in basso
        if (self.room_number + num_cols) in neighbours:
            door_start = self.size // 4
            door_end = self.size * 3 // 4
            self.doors['bottom'] = {
                'exists': True,
                'range': (door_start, door_end)
            }

        # Porta sinistra (se non è la prima colonna)
        if (self.room_number - 1) in neighbours:
            door_start = self.size // 4
            door_end = self.size * 3 // 4
            self.doors['left'] = {
                'exists': True,
                'range': (door_start, door_end)
            }

        # Porta in alto (se non è la prima riga)
        if (self.room_number - num_cols) in neighbours:
            door_start = self.size // 4
            door_end = self.size * 3 // 4
            self.doors['top'] = {
                'exists': True,
                'range': (door_start, door_end)
            }

    def can_pass_through(self, position: Tuple[int, int], direction: str) -> bool:
        """
        Verifica se è possibile passare attraverso una porta in una data posizione e direzione.
        
        Args:
            position: Tuple[int, int] - Posizione relativa nella stanza (x, y)
            direction: str - Direzione del movimento ('right', 'left', 'top', 'bottom')
            
        Returns:
            bool: True se il passaggio è consentito, False altrimenti
        """
        if not self.doors[direction]['exists']:
            return False

        x, y = position
        door_range = self.doors[direction]['range']

        if direction in ['right', 'left']:
            return door_range[0] <= y <= door_range[1]
        else:  # top or bottom
            return door_range[0] <= x <= door_range[1]

    def draw(self, surface, num_cols: int, num_rows: int, colors: Dict):
        """Disegna la stanza con le sue porte."""
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