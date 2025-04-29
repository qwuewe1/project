# Клетки карты
#  0 – пусто
#  1 – стена
#  2 – выход
# -1 – персонаж
#  3 – огонь
#  4 – сгоревший пол
#  5 – выгоревшая стена
#  6 – горящий персонажЯ

import pygame
import random
import time
from collections import deque
# BG = (219, 183, 107)  # фон
# WALL = (156, 102, 31)  # стена
# EXIT = (25, 255, 102)  # выход
# PL = (102, 127, 255)  # персонаж
# FIRE = (234, 35, 0)  # огонь
# BURN = (60, 60, 60)  # выгоревшая стена
# FLOOR = (100, 100, 100)  # тлеющий пол
#
#цвета
class Colors:
    BG           = (219, 183, 107)   # фон
    WALL         = (156, 102, 31)    # стена
    EXIT         = (25, 255, 102)    # выход
    PLAYER       = (102, 127, 255)   # персонаж
    FIRE         = (234,  35,   0)   # огонь
    BURN         = ( 60,  60,  60)   # выгоревшая стена
    FLOOR        = (100, 100, 100)   # тлеющий пол
    PLAYER_FIRE  = (255, 165,   0)   # горящий


WIDTH, HEIGHT = 30, 30
CELL_SIZE = 25
STEP_DELAY = 0.2

#режим
print("Выберите режим:")
print("1 - авто")
print("2 -  сами")

mode = input()
AUTO_CONTROL = (mode == '1')


wall_burn_time = {}
floor_burn_time = {}
pygame.mixer.init()
pygame.mixer.music.load("schizophrenia1.mp3")
pygame.mixer.music.play(loops=-1)

def create_empty_map(width, height, fill=1):
    # Создаёт пустую карту, залитую значением fill
    return [[fill for _ in range(width)] for _ in range(height)]


def mazecreate(width, height):
    #создаем лабиринт
    maze = create_empty_map(width, height, fill=1)

    start_x, start_y = 1, 1
    maze[start_y][start_x] = 0

    stack = [(start_x, start_y)]
    visited = {(start_x, start_y)}
    directions = [(0, -2), (0, 2), (-2, 0), (2, 0)]

    while stack:
        x, y = stack[-1]
        random.shuffle(directions)

        for dx, dy in directions:
            nx, ny = x + dx, y + dy
            if 1 <= nx < width - 1 and 1 <= ny < height - 1 and (nx, ny) not in visited:
                maze[y + dy // 2][x + dx // 2] = 0  # ломаем стену между клетками
                maze[ny][nx] = 0
                visited.add((nx, ny))
                stack.append((nx, ny))
                break
        else:
            stack.pop()

    return maze


def placeexits(maze, count):
    #ставим выходы
    exits = []
    w, h = len(maze[0]), len(maze)
    while len(exits) < count:
        if random.choice([True, False]):  # горизонтальная сторона
            x = random.randrange(1, w-1, 2)
            y = 0 if random.choice([True, False]) else h-1
        else:                             # вертикальная сторона
            y = random.randrange(1, h-1, 2)
            x = 0 if random.choice([True, False]) else w-1
        if maze[y][x] == 1:
            maze[y][x] = 2
            exits.append((x, y))
    return exits


def placefire(game_map, count=2):
    #поджигаем рандом клетки
    h, w = len(game_map), len(game_map[0])
    for _ in range(count):
        while True:
            fx, fy = random.randint(1, w - 2), random.randint(1, h - 2)
            if game_map[fy][fx] == 0:
                game_map[fy][fx] = 3
                wall_burn_time[(fx, fy)] = 4  # время горения
                break



def auto(game_map, x0, y0):
    #автоматически передвигаемя
    h, w = len(game_map), len(game_map[0])
    PASSABLE = {0, 2, 4, 5, -1}  #можно идти
    dirs = [(-1,0), (1,0), (0,-1), (0,1)]

    q = deque([(x0, y0)])
    prev = { (x0, y0): None }

    while q:
        x, y = q.popleft()
        if game_map[y][x] == 2:  #выход
            break
        for dx, dy in dirs:
            nx, ny = x + dx, y + dy
            if 0 <= nx < w and 0 <= ny < h and game_map[ny][nx] in PASSABLE and (nx, ny) not in prev:
                prev[(nx, ny)] = (x, y)
                q.append((nx, ny))
    else:
        return x0, y0

    cell = (x, y)
    while prev[cell] != (x0, y0) and prev[cell] is not None:
        cell = prev[cell]
    return cell


def show(screen, game_map, player_pos):
    screen.fill(Colors.BG)
    for y, row in enumerate(game_map):
        for x, cell in enumerate(row):
            rect = (x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE)
            if cell == 1:
                pygame.draw.rect(screen, Colors.WALL, rect)
            elif cell == 2:
                pygame.draw.rect(screen, Colors.EXIT, rect)
            elif cell == 3:
                pygame.draw.rect(screen, Colors.FIRE, rect)
            elif cell == 4:
                pygame.draw.rect(screen, Colors.FLOOR, rect)
            elif cell == 5:
                pygame.draw.rect(screen, Colors.BURN, rect)
            elif cell == -1:
                pygame.draw.rect(screen, Colors.PLAYER, rect)
            elif cell == 6:
                pygame.draw.rect(screen, Colors.PLAYER_FIRE, rect)


def spreadfire(game_map):
    h, w = len(game_map), len(game_map[0])
    new_fires = []
    for y in range(h):
        for x in range(w):
            if game_map[y][x] == 3:
                for dx, dy in [(-1,0),(1,0),(0,-1),(0,1)]:
                    nx, ny = x+dx, y+dy
                    if 0 <= nx < w and 0 <= ny < h and game_map[ny][nx] == 0 and random.random() < 0.2:
                        new_fires.append((nx, ny))
    for x, y in new_fires:
        game_map[y][x] = 3


def main():
    game_map = mazecreate(WIDTH, HEIGHT)
    placeexits(game_map, 3)
    placefire(game_map, 3)


    player_x, player_y = 1, 1
    game_map[player_y][player_x] = -1

    pygame.init()
    screen = pygame.display.set_mode((WIDTH * CELL_SIZE, HEIGHT * CELL_SIZE))
    pygame.display.set_caption("Эвакуация")
    clock = pygame.time.Clock()

    running = True
    victory = False

    PASSABLE = {0, 2, 4, 5}

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        #управление
        if AUTO_CONTROL:
            newx, newy = auto(game_map, player_x, player_y)
            # time.sleep(5)
            time.sleep(1)
        else:
            keys = pygame.key.get_pressed()
            newx, newy = player_x, player_y
            if keys[pygame.K_LEFT]  or keys[pygame.K_a]: newx -= 1
            if keys[pygame.K_RIGHT] or keys[pygame.K_d]: newx += 1
            if keys[pygame.K_UP]    or keys[pygame.K_w]: newy -= 1
            if keys[pygame.K_DOWN]  or keys[pygame.K_s]: newy += 1

        # не выходим за карту
        newx = max(0, min(newx, WIDTH-1))
        newy = max(0, min(newy, HEIGHT-1))

        next_cell = game_map[newy][newx]
        if next_cell == 2:
            victory = True
            running = False
        elif next_cell in PASSABLE:
            game_map[player_y][player_x] = 0
            player_x, player_y = newx, newy
            game_map[player_y][player_x] = -1

        #огонь
        spreadfire(game_map)

        #рендерим
        show(screen, game_map, (player_x, player_y))
        pygame.display.flip()

        clock.tick(60)
        time.sleep(STEP_DELAY)

    pygame.quit()
    if victory:
        pygame.mixer.init()
        print("Вы спаслись\n")
        pygame.mixer.music.load("victory.mp3")
        pygame.mixer.music.stop()
        pygame.mixer.music.load("victory.mp3")
        pygame.mixer.music.play(loops=1)
    else:
        print("Вы не спаслись(\n")
        pygame.mixer.init()
        pygame.mixer.music.load("burn.mp3")
        pygame.mixer.music.stop()
        pygame.mixer.music.load("burn.mp3")
        pygame.mixer.music.play(loops=1)


main()