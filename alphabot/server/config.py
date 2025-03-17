import yaml
import os

def load_config(config_path: str = None) -> dict:
    if not config_path:
        config_path = os.path.join(os.path.dirname(__file__), 'config.yaml')
    
    try:
        with open(config_path, 'r') as file:
            config = yaml.safe_load(file)
            return config
    except FileNotFoundError:
        print("Config file not found:", config_path)
        return {
            'display': {
                'width': 1600,
                'height': 900,
                'caption': "Labirinto"
            },
            'maze': {
                'min_rows': 3,
                'max_rows': 7,
                'min_cols': 4,
                'max_cols': 8
            },
            'colors': {
                'white': [255, 255, 255],
                'black': [0, 0, 0],
                'green': [0, 255, 0],
                'red': [255, 0, 0],
                'blue': [0, 0, 255]
            },
            'player': {
                'speed': 5,
                'size': 10
            }
        }