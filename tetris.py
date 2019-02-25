"""
File Name     :: tetris.py
Description   :: Classic Tetris game created using Pygame module
Dependencies  :: pygame
"""


import pygame
import random
import os
from shapes import shapes, shape_colors

pygame.font.init()

# PYGAME SOUND INIT AND SOUND VARIABLES
pygame.mixer.pre_init(44100, -16, 2, 2048)
pygame.mixer.init()
pygame.init()

end_sound = pygame.mixer.Sound(os.path.join("sound", "gameover.wav"))
rotate_sound = pygame.mixer.Sound(os.path.join("sound", "block-rotate.wav"))
line_drop_sound = pygame.mixer.Sound(os.path.join("sound","line-drop.wav"))
line_removal_sound = pygame.mixer.Sound(os.path.join("sound", "line-removal.wav"))


# GLOBALS VARIABLES
screen_width = 800
screen_height = 700
play_width = 300  # 300 // 10 = 30 width per block
play_height = 600  # 600 // 20 = 20 height per block
block_size = 30

# Top left positions of play area - for start position
top_left_x = (screen_width - play_width) // 2
top_left_y = screen_height - play_height

class Piece(object):
    rows = 20  # Y
    columns = 10  # X
 
    def __init__(self, column, row, shape):
        self.x = column
        self.y = row
        self.shape = shape
        self.color = shape_colors[shapes.index(shape)]  # Color index is the same as shape index
        self.rotation = 0  # number from 0-3

def create_grid(locked_pos={}):
    """Creates list of 20 elements each with sublist of 10 elements that represents grid"""

    grid = [[(0,0,0) for _ in range(10)] for _ in range(20)]

    for i in range(len(grid)):
        for j in range(len(grid[i])):
            if (j, i) in locked_pos:
                c = locked_pos[(j,i)]
                grid[i][j] = c
    return grid


def convert_shape_format(shape):
    """Converts shapes from list to coordinated shapes -> List"""
    positions = []
    format = shape.shape[shape.rotation % len(shape.shape)]

    for i, line in enumerate(format):
        row = list(line)
        for j, column in enumerate(row):
            if column == '0':
                positions.append((shape.x + j, shape.y + i))

    # Offsets position
    for i, pos in enumerate(positions):
        positions[i] = (pos[0] - 2, pos[1] - 4) # Shapes need to start falling outside visible game space

    return positions


def valid_space(shape, grid):
    """Returns if current space is valid -> Bool"""

    accepted_pos = [[(j, i) for j in range(10) if grid[i][j] == (0,0,0)] for i in range(20)]
    # Converts to 1D list
    accepted_pos = [j for sub in accepted_pos for j in sub]

    formatted = convert_shape_format(shape)

    # Checks if shapes are in accepted position e.g. checks if they are touching border
    for pos in formatted:
        if pos not in accepted_pos:
            if pos[1] > -1:
                return False
    return True


def check_lost(positions):
    """Check if any position in the given list is above the screen -> Bool"""
    for pos in positions:
        x, y = pos
        if y < 1:
            pygame.mixer.Sound.play(end_sound)   #Play game over sound
            return True

    return False


def get_shape():
    """Generates a random shape"""
    return Piece(5, 0, random.choice(shapes))   # Column, row, shape


def draw_text_middle(surface, text, size, color):
    """Displays text in the middle of screen"""
    font = pygame.font.SysFont("arial", size, bold=True)
    label = font.render(text, 1, color)

    surface.blit(label, (top_left_x + play_width /2 - (label.get_width()/2), top_left_y + play_height/2 - label.get_height()/2))

def draw_text_bottom(surface, text, size, color):
    """Displays text in the bottom of screen"""
    font = pygame.font.SysFont("arial", size, bold=False)
    label = font.render(text, 1, color)

    surface.blit(label, (top_left_x + play_width / 2 - (label.get_width()/2), top_left_y + play_height / 1.5 - label.get_height()/2))


def draw_grid(surface, grid):
    """"Draws the grid lines"""

    # Start positions, top left corner
    sx = top_left_x
    sy = top_left_y

    for i in range(len(grid)):
        pygame.draw.line(surface, (192, 192, 192), (sx, sy + i*block_size), (sx + play_width, sy + i*block_size))
        for j in range(len(grid[i])):
            pygame.draw.line(surface, (192, 192, 192), (sx + j*block_size, sy),(sx + j*block_size, sy + play_height))


def clear_rows(grid, locked):
    """Checks if row is full, if True - shift every other row above down by one"""

    inc = 0
    # Loops through grid backwards and chech if black color exists in row
    for i in range(len(grid)-1, -1, -1):
        row = grid[i]
        if (0,0,0) not in row:
            inc += 1
            ind = i
            for j in range(len(row)):
                try:
                    # Remove row and play the drop sound
                    del locked[(j, i)]
                    pygame.mixer.Sound.play(line_removal_sound)
                except:
                    continue

    # Shifts every other row above down by one
    if inc > 0:
        for key in sorted(list(locked), key=lambda x: x[1])[::-1]:
            x, y = key
            if y < ind:
                newKey = (x, y + inc)
                locked[newKey] = locked.pop(key)

    return inc


def draw_next_shape(shape, surface):
    """Display the next falling shape on the right side of the screen"""

    font = pygame.font.SysFont('arial', 30)
    label = font.render('Next Shape', 1, (255, 255, 255))

    sx = top_left_x + play_width + 50
    sy = top_left_y + play_height/2 - 100
    format = shape.shape[shape.rotation % len(shape.shape)]

    for i, line in enumerate(format):
        row = list(line)
        for j, column in enumerate(row):
            if column == '0':
                pygame.draw.rect(surface, shape.color, (sx + j*block_size, sy + i*block_size, block_size, block_size), 0)

    surface.blit(label, (sx + 10, sy - 30))


def update_score(new_score):
    """Updates max score in file"""

    score = max_score()

    with open('scores.txt', 'w') as f:
        if int(score) > new_score:
            f.write(str(score))
        else:
            f.write(str(new_score))


def max_score():
    """Reads max score from file"""

    with open('scores.txt', 'r') as f:
        lines = f.readlines()
        score = lines[0].strip()

    return score


def draw_window(surface, grid, score=0, last_score = 0):
    """Draws main game window"""

    surface.fill((0, 0, 0))

    pygame.font.init()
    font = pygame.font.SysFont('arial', 60)
    label = font.render('Tetris', 1, (255, 255, 255))

    surface.blit(label, (top_left_x + play_width / 2 - (label.get_width() / 2), 30))

    # current score
    font = pygame.font.SysFont('arial', 30)
    label = font.render('Score: ' + str(score), 1, (255,255,255))
    sx = top_left_x + play_width + 50
    sy = top_left_y + play_height/2 - 100
    surface.blit(label, (sx + 20, sy + 160))
    
    # last score
    label = font.render('High Score: ' + last_score, 1, (255,255,255))
    sx = top_left_x - 200
    sy = top_left_y + 200
    surface.blit(label, (sx + 20, sy + 160))

    for i in range(len(grid)):
        for j in range(len(grid[i])):
            pygame.draw.rect(surface, grid[i][j], (top_left_x + j*block_size, top_left_y + i*block_size, block_size, block_size), 0)

    pygame.draw.rect(surface, (255, 0, 0), (top_left_x, top_left_y, play_width, play_height), 5)

    draw_grid(surface, grid)


def main(win):
    """Main function"""
    last_score = max_score()
    locked_positions = {}
    grid = create_grid(locked_positions)

    change_piece = False
    run = True
    current_piece = get_shape()
    next_piece = get_shape()
    clock = pygame.time.Clock()
    fall_time = 0
    fall_speed = 0.27
    level_time = 0
    score = 0

    while run:
        grid = create_grid(locked_positions)    # Constantly checks occupied grid spaces
        fall_time += clock.get_rawtime()
        level_time += clock.get_rawtime()
        clock.tick()

        # Changes speed of falling piece every 5s
        if level_time/1000 > 5:
            level_time = 0
            if level_time > 0.12:
                level_time -= 0.005

        # Auto move the piece one space down
        if fall_time/1000 > fall_speed:
            fall_time = 0
            current_piece.y += 1
            # Checks if piece hit another one or bottom of the screen
            if not(valid_space(current_piece, grid)) and current_piece.y > 0:
                current_piece.y -= 1
                pygame.mixer.Sound.play(line_drop_sound)   # Play shape touchdown sound
                change_piece = True

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False     # Breaks out of while loop
                pygame.display.quit()

            # Controls
            # If key is pressed check which one
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT or event.key == pygame.K_a:
                    current_piece.x -= 1
                    if not(valid_space(current_piece, grid)):
                        current_piece.x += 1

                if event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                    current_piece.x += 1
                    if not(valid_space(current_piece, grid)):
                        current_piece.x -= 1

                if event.key == pygame.K_DOWN or event.key == pygame.K_s:
                    current_piece.y += 1
                    if not(valid_space(current_piece, grid)):
                        current_piece.y -= 1

                if event.key == pygame.K_UP or event.key == pygame.K_w:
                    # rotate shape
                    current_piece.rotation += 1
                    pygame.mixer.Sound.play(rotate_sound)
                    if not(valid_space(current_piece, grid)):
                        current_piece.rotation -= 1
                
                if event.key == pygame.K_ESCAPE:
                    run = False

        shape_pos = convert_shape_format(current_piece)

        # Add color of piece to the grid for drawing
        for i in range(len(shape_pos)):
            x, y = shape_pos[i]
            if y > -1:  # If we are not above the screen
                grid[y][x] = current_piece.color

        # If piece hits ground
        if change_piece:
            for pos in shape_pos:
                p = (pos[0], pos[1])
                locked_positions[p] = current_piece.color
            current_piece = next_piece
            next_piece = get_shape()
            change_piece = False
            score += clear_rows(grid, locked_positions) * 10

        # Draws all elements
        draw_window(win, grid, score, last_score)
        draw_next_shape(next_piece, win)
        pygame.display.update()

        # Check for loose condition
        if check_lost(locked_positions):
            draw_text_middle(win, "GAME OVER!", 80, (255, 255, 255))
            pygame.display.update()
            pygame.time.delay(1500)
            run = False
            update_score(score)


def main_menu(win):
    """Start manu popup"""

    run = True
    while run:
        win.fill((0,0,0))
        draw_text_middle(win, 'Press Any Key To Play', 60, (255, 255, 255))
        draw_text_bottom(win, 'Use arrow keys or WASD to play', 40, (255, 255, 255))
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.KEYDOWN:
                main(win)

    pygame.display.quit()


win = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption('Tetris')
main_menu(win)