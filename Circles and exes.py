import sys
import random
import pygame
from pygame.locals import *
import pygame_widgets
import colorsys

from pygame_widgets.slider import Slider
from pygame_widgets.textbox import TextBox

# Initialize Pygame
pygame.init()

ss=9
# Set up display
global rows, cols
rows, cols = ss, ss  # 9x9 grid
global square_size 
square_size= 100   # Size of each square
width, height = cols * square_size, rows * square_size
win = pygame.display.set_mode((width, height + 80), pygame.RESIZABLE)  # Increased height for buttons
pygame.display.set_caption("Houssam's 9x9 circles vs Xs")





# Colors
GRID_COLOR = (0, 0, 0)  # Thin border color for grid
SHAPE_BORDER_COLOR = (0, 0, 0)  # Thick border color for shapes
OUTER_BORDER_COLOR = (0, 0, 0)  # Thick border color for outer square board
SHAPE_FILL_COLOR = None  # No fill color for shapes



def generate_pastel_colors(n):
    pastel_colors = set()
    
    while len(pastel_colors) < n:
        h = random.random()  # Random hue
        s = 0.5 + random.random() * 0.2  # Low to moderate saturation
        l = 0.5 + random.random() * 0.2  # High lightness
        r, g, b = colorsys.hls_to_rgb(h, l, s)
        color = (int(r * 255), int(g * 255), int(b * 255))
        pastel_colors.add(color)
    
    return list(pastel_colors)




COLORS = generate_pastel_colors(rows)
# Directions for adjacent squares (up, down, left, right)
DIRECTIONS = [(0, 1), (1, 0), (0, -1), (-1, 0)]

def is_safe(board, row, col):
    # Check if the queen can be placed at board[row][col]
    for i in range(row):
        if board[i] == col or \
           board[i] - i == col - row or \
           board[i] + i == col + row:
            return False
    return True

def solve_n_queens(n):
    board = [-1] * n  # -1 indicates no queen is placed in that row
    solutions = []
    def place_queens(row):
        if row == n:
            solutions.append(board[:])
            return
        cols = list(range(n))
        random.shuffle(cols)
        for col in cols:
            if is_safe(board, row, col):
                board[row] = col
                place_queens(row + 1)
                board[row] = -1

    place_queens(0)
    return solutions

def generate_n_queen_positions(n):
    solutions = solve_n_queens(n)
    if solutions:
        return random.choice(solutions)
    else:
        return None

def print_board(positions):
    board_size = len(positions)
    board = [['.' for _ in range(board_size)] for _ in range(board_size)]
    for row, col in enumerate(positions):
        board[row][col] = 'Q'
    for row in board:
        print(' '.join(row))




def generate_random_shape_sizes(total_size, num_shapes):
    # Generate random partition points
    partition_points = sorted(random.sample(range(1, total_size), num_shapes - 1))
    
    # Calculate shape sizes based on partition points
    shape_sizes = [partition_points[0]] + \
                  [partition_points[i] - partition_points[i - 1] for i in range(1, len(partition_points))] + \
                  [total_size - partition_points[-1]]
    
    return shape_sizes

# Generate random contiguous shapes
def generate_shapes(num_shapes, rows, cols):
    queens = generate_n_queen_positions(rows)

    while True:
        grid = [[-1 for _ in range(cols)] for _ in range(rows)]
        shapes = [[] for _ in range(num_shapes)]
        shape_sizes = generate_random_shape_sizes(rows*cols,rows)#[(rows * cols) // num_shapes] * num_shapes*
        for i in range((rows * cols) % num_shapes):
            shape_sizes[i] += 1

        occupied = set()
        success = True

        for c,r in enumerate(queens):
            occupied.add((c,r))

        for shape_index, shape_size in enumerate(shape_sizes):
            #print ("generating shape %d" %shape_index)
            tries = 0
            while len(shapes[shape_index]) < shape_size and tries < 20:
                #print ("shape %d,  size: %d/%d" %(shape_index, len(shapes[shape_index]), shape_size))
                if not shapes[shape_index]:
                    x= shape_index
                    y= queens[shape_index]
                    shapes[shape_index].append((x, y))
                    grid[y][x] = shape_index
                else:
                    # Expand the shape from an existing square
                    x, y = random.choice(shapes[shape_index])
                    random.shuffle(DIRECTIONS)
                    for dx, dy in DIRECTIONS:
                        nx, ny = x + dx, y + dy
                        if 0 <= nx < cols and 0 <= ny < rows and (nx, ny) not in occupied:
                            shapes[shape_index].append((nx, ny))
                            grid[ny][nx] = shape_index
                            occupied.add((nx, ny))
                            break
                    else:
                        tries += 1

            if len(shapes[shape_index]) < shape_size:
                success = False
                break

        if success:
            return shapes, grid  # Return both shapes and grid

# Draw shapes on the board
def draw_shapes(win, shapes, grid, circles):
    for i, shape in enumerate(shapes):
        color = COLORS[i % len(COLORS)]
        for (x, y) in shape:
            pygame.draw.rect(win, color, (x * square_size, y * square_size, square_size, square_size))


        # Draw thicker border around the shape
        for (x, y) in shape:
            # Check adjacent cells
            if x == 0 or grid[y][x - 1] != grid[y][x]:
                pygame.draw.line(win, SHAPE_BORDER_COLOR, (x * square_size, y * square_size),
                                 (x * square_size, (y + 1) * square_size), 3)  # Left border
            if x == cols - 1 or grid[y][x + 1] != grid[y][x]:
                pygame.draw.line(win, SHAPE_BORDER_COLOR, ((x + 1) * square_size, y * square_size),
                                 ((x + 1) * square_size, (y + 1) * square_size), 3)  # Right border
            if y == 0 or grid[y - 1][x] != grid[y][x]:
                pygame.draw.line(win, SHAPE_BORDER_COLOR, (x * square_size, y * square_size),
                                 ((x + 1) * square_size, y * square_size), 3)  # Top border
            if y == rows - 1 or grid[y + 1][x] != grid[y][x]:
                pygame.draw.line(win, SHAPE_BORDER_COLOR, (x * square_size, (y + 1) * square_size),
                                 ((x + 1) * square_size, (y + 1) * square_size), 3)  # Bottom border

    # Draw grid lines
    for row in range(rows + 1):
        pygame.draw.line(win, GRID_COLOR, (0, row * square_size), (width, row * square_size), 1)
    for col in range(cols + 1):
        pygame.draw.line(win, GRID_COLOR, (col * square_size, 0), (col * square_size, height), 1)

# Function to draw buttons
def draw_button(win, text, x, y, width, height, inactive_color, active_color, action=None):
    mouse = pygame.mouse.get_pos()
    click = pygame.mouse.get_pressed()

    if x < mouse[0] < x + width and y < mouse[1] < y + height:
        pygame.draw.rect(win, active_color, (x, y, width, height))
        if click[0] == 1 and action:
            action()
    else:
        pygame.draw.rect(win, inactive_color, (x, y, width, height))

    font = pygame.font.Font(None, 30)
    text_surface = font.render(text, True, (255, 255, 255))
    text_rect = text_surface.get_rect()
    text_rect.center = (x + width / 2, y + height / 2)
    win.blit(text_surface, text_rect)

# Function for restarting the game
def restart_game():
    main(shapes, grid)

# Function for options menu
def options_menu():
    global run_options 
    run_options = True
    slider = Slider(win, 400, 100, 800, 40, min=0, max=99, step=1)
    output = TextBox(win, 475, 200, 50, 50, fontSize=30)
    win.fill((0, 255, 255, 50))  # Semi-transparent background
    output.disable()  # Act as label instead of textbox

    while run_options:
        output.setText(slider.getValue())
        events=pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            
            pygame_widgets.update(events)
            pygame.display.update()
        
        draw_button(win, "Return", 100, 100, 200, 50, (200, 0, 0), (255, 0, 0), return_to_game)
        pygame.display.flip()

# Function to return to the game from options menu
def return_to_game():
    run_options=False


def draw_queens(win, circles, square_size, rows, cols):
    s=0
    for c in range(cols):
            for r in range(rows):  
                if circles[c][r]:
                    pygame.draw.circle(win, (10, 0, 0), ((c + 0.5) * square_size, (r + 0.5) * square_size), square_size // 4)
                    s+=1
    if s==rows:
        font = pygame.font.Font(None, 30)
        text_surface = font.render("You Win!", True, (255, 255, 255))
        text_rect = text_surface.get_rect()
        text_rect.center = (width / 2, height / 2)
        win.blit(text_surface, text_rect)

def draw_exes(win, square_size, rows, cols, shapes, circles):
    exes = [[False for _ in range(cols)] for _ in range(rows)]  # Track where x should be drawn
    for grid_x in range (cols):
        for grid_y in range (rows):
            if circles[grid_x][grid_y]:
            #updating exes
                for cc in range (cols):
                    if cc != grid_x:
                        exes [cc][grid_y]=True
                for rr in range (rows):
                    if rr != grid_y:
                        exes [grid_x][rr]=True
                 #diagonals               
                if grid_x ==0:
                    if grid_y ==0:
                        exes[grid_x+1][grid_y+1]=True
                    elif grid_y ==rows-1:
                        exes[grid_x+1][grid_y-1]=True
                    else:
                        exes[grid_x+1][grid_y+1]=True
                        exes[grid_x+1][grid_y-1]=True
                elif grid_x ==rows-1:
                    if grid_y ==0:
                        exes[grid_x-1][grid_y+1]=True
                    elif grid_y ==rows-1:
                        exes[grid_x-1][grid_y-1]=True
                    else:
                        exes[grid_x-1][grid_y+1]=True
                        exes[grid_x-1][grid_y-1]=True
                else:
                    if grid_y ==0:
                        exes[grid_x+1][grid_y+1]=True
                        exes[grid_x-1][grid_y+1]=True
                    elif grid_y ==rows-1:
                        exes[grid_x+1][grid_y-1]=True
                        exes[grid_x-1][grid_y-1]=True
                    else:
                        exes[grid_x+1][grid_y+1]=True
                        exes[grid_x+1][grid_y-1]=True
                        exes[grid_x-1][grid_y-1]=True
                        exes[grid_x-1][grid_y+1]=True


                for shape in shapes:
                    for (c, r) in shape:
                        if circles[c][r]:
                            for (c, r) in shape:
                                if not circles[c][r]:
                                    exes[c][r]=True
                            break 


    for c in range(cols):
        for r in range(rows):
              
            if exes[c][r]:
                pygame.draw.line(win, (0, 0, 0), ((c + 0.2) * square_size, (r + 0.2) * square_size),
                                        ((c + 0.8) * square_size, (r + 0.8) * square_size), 3)
                pygame.draw.line(win, (0, 0, 0), ((c + 0.8) * square_size, (r + 0.2) * square_size),
                                        ((c + 0.2) * square_size, (r + 0.8) * square_size), 3)
    return exes    
# Main loop


def close_game():
    global run
    run = False

def new_game():
    global shapes, grid
    shapes, grid = generate_shapes(rows, rows, cols)  # Generate 9 shapes to fill the 9x9 grid
    main(shapes, grid)


def main(shapes, grid):
    global run
    clock = pygame.time.Clock()
    run = True
    circles = [[False for _ in range(cols)] for _ in range(rows)]  # Track where circles should be drawn
    exes = [[False for _ in range(cols)] for _ in range(rows)]  # Track where x should be drawn
    while run:
        clock.tick(60)
        win.fill((255, 255, 255))  # Fill background with white

        draw_shapes(win, shapes, grid, circles)
        draw_queens(win, circles, square_size, rows,cols)
        exes=draw_exes(win,square_size,rows,cols, shapes, circles)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                x, y = event.pos
                grid_x = x // square_size
                grid_y = y // square_size
                if 0 <= grid_x < cols and 0 <= grid_y < rows and not exes[grid_x][grid_y]:
                    if not circles[grid_x][grid_y]:
                        circles[grid_x][grid_y] = True
                    else:
                        circles[grid_x][grid_y] = False

        draw_button(win, "Restart", 20, height+20, 120, 50, (0, 200, 0), (0, 255, 0), restart_game)
        draw_button(win, "Options", 160, height+20, 120, 50, (200, 0, 0), (255, 0, 0), options_menu)                        
        draw_button(win, "Close", 300, height+20, 120, 50, (200, 0, 0), (255, 0, 0), close_game)  
        draw_button(win, "New Game", 440, height+20, 120, 50, (200, 0, 0), (255, 0, 0), new_game)  
        pygame.display.flip()

    pygame.quit()
    sys.exit()


shapes, grid = generate_shapes(rows, rows, cols)  # Generate 9 shapes to fill the 9x9 grid

if __name__ == "__main__":
    main(shapes, grid)

