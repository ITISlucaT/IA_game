import pygame
import random

# Inizializza pygame
pygame.init()

# Costanti
WIDTH, HEIGHT = 640, 480
CELL_SIZE = 40
ROWS, COLS = HEIGHT // CELL_SIZE, WIDTH // CELL_SIZE
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
PLAYER1_COLOR = (0, 255, 0)
PLAYER2_COLOR = (0, 0, 255)
ENEMY_COLOR = (255, 0, 0)
MOVE_DELAY = 10

# Creazione finestra
display = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Two Player Maze Game")

def generate_maze():
    return [[0 for _ in range(COLS)] for _ in range(ROWS)]

def valid_spawn(maze, x, y):
    return maze[y][x] == 0

def place_entities(maze, count):
    entities = []
    while len(entities) < count:
        x, y = random.randint(0, COLS - 1), random.randint(0, ROWS - 1)
        if valid_spawn(maze, x, y) and (x, y) not in entities:
            entities.append((x, y))
    return entities

def draw_maze():
    display.fill(WHITE)

def move_enemy(enemy):
    directions = [(0, 1), (0, -1), (1, 0), (-1, 0)]
    dx, dy = random.choice(directions)
    new_x, new_y = enemy[0] + dx, enemy[1] + dy
    if 0 <= new_x < COLS and 0 <= new_y < ROWS:
        return (new_x, new_y)
    return enemy

def main():
    clock = pygame.time.Clock()
    maze = generate_maze()

    player1 = (0, ROWS - 1)
    player2 = (COLS - 1, ROWS - 1)
    move_counter = 0

    enemies = place_entities(maze, 3)
    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        keys = pygame.key.get_pressed()
        move_counter += 1
        if move_counter >= MOVE_DELAY:
            move_counter = 0
            
            # Movimento Player 1 (WASD)
            px1, py1 = player1
            if keys[pygame.K_a] and px1 > 0:
                px1 -= 1
            if keys[pygame.K_d] and px1 < COLS - 1:
                px1 += 1
            if keys[pygame.K_w] and py1 > 0:
                py1 -= 1
            if keys[pygame.K_s] and py1 < ROWS - 1:
                py1 += 1
            player1 = (px1, py1)

            # Movimento Player 2 (Frecce)
            px2, py2 = player2
            if keys[pygame.K_LEFT] and px2 > 0:
                px2 -= 1
            if keys[pygame.K_RIGHT] and px2 < COLS - 1:
                px2 += 1
            if keys[pygame.K_UP] and py2 > 0:
                py2 -= 1
            if keys[pygame.K_DOWN] and py2 < ROWS - 1:
                py2 += 1
            player2 = (px2, py2)

            # Movimento Nemici
            enemies = [move_enemy(e) for e in enemies]

            # Controllo collisione con i nemici
            enemies = [e for e in enemies if e != player1 and e != player2]

        # Disegna
        draw_maze()
        pygame.draw.rect(display, PLAYER1_COLOR, (player1[0] * CELL_SIZE, player1[1] * CELL_SIZE, CELL_SIZE, CELL_SIZE))
        pygame.draw.rect(display, PLAYER2_COLOR, (player2[0] * CELL_SIZE, player2[1] * CELL_SIZE, CELL_SIZE, CELL_SIZE))
        for enemy in enemies:
            pygame.draw.rect(display, ENEMY_COLOR, (enemy[0] * CELL_SIZE, enemy[1] * CELL_SIZE, CELL_SIZE, CELL_SIZE))
        
        pygame.display.flip()
        clock.tick(30)
    
    pygame.quit()

if __name__ == '__main__':
    main()