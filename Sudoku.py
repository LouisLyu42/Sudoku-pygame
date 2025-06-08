import random as rd
import pygame
import sys
import copy
#utilizes copy library to prevent accidental corruption/edits to original boards during generation process

def three_by_three(row, column):
    '''finds the top left corner's coordinates that the 3x3 box that a given coordinate (row, column) is in'''
    row_coord = row - row%3
    column_coord = column - column%3
    return row_coord, column_coord


def is_valid(num, board, row, column):
    '''function to verify if a number num placed at a initial 9x9 board at (row, column) leads to a valid sudoku starting board'''
    a, b = three_by_three(row, column)
    #checks if current number is in current row
    for i in board[row]:
        if i == num:
            return False
    #checks if current number is in current column
    for j in board:
        if j[column] == num:
            return False
    #checks if the number is the 3x3 box
    for x in range(a, a+3):
        for y in range(b, b+3):
            if board[x][y] == num:
                return False
    return True


def fill_board(board):
    '''Takes in a 9x9 sudoku board and completely solves/fills it'''
    for i in range(9):
        for j in range(9):
            if board[i][j] == 0:
                nums = list(range(1,10))
                rd.shuffle(nums)
                for num in nums:
                    if is_valid(num, board, i, j):
                        board[i][j] = num
                        if fill_board(board):  # Recurse
                            return True
                        board[i][j] = 0  # Backtrack
                return False  # No valid number found, backtrack
    return True  # Board is completely filled


def count_solutions(board, limit=2):
    '''Counts the number of solutions up to a limit. Stops early for performance.'''
    def solve(b, count):
        if count[0] >= limit:
            return  # Early exit

        for row in range(9):
            for col in range(9):
                if b[row][col] == 0:
                    for num in range(1, 10):
                        if is_valid(num, b, row, col):
                            b[row][col] = num
                            solve(b, count)
                            b[row][col] = 0
                    return
        count[0] += 1

    count = [0]
    solve(copy.deepcopy(board), count)
    return count[0]


def generate_puzzle(clues=30, max_attempts=1000):
    '''Generates a partially filled but valid puzzle with varying difficulty based on amount of clues, has a limit of 1000 attempts at removing numbers during generation to prevent stalling'''
    board = [[0 for _ in range(9)] for _ in range(9)]
    fill_board(board)
    
    attempts = 81 - clues
    tries = 0

    while attempts > 0 and tries < max_attempts:
        row = rd.randint(0, 8)
        col = rd.randint(0, 8)

        if board[row][col] != 0:
            backup = board[row][col]
            board[row][col] = 0

            if count_solutions(board) == 1:
                attempts -= 1
            else:
                board[row][col] = backup
            tries += 1

    return board

print("Generating puzzle...")
board = generate_puzzle(clues=30)
print("Puzzle generated!")


# Initialize Pygame
pygame.init()

# Constants, initialized by ChatGPT to give proper values to fit grid into window, create buttons, generate correct colors on screen, set the font, etc.
WIDTH, HEIGHT = 540, 600
GRID_SIZE = 9
CELL_SIZE = WIDTH // GRID_SIZE
FONT = pygame.font.SysFont("comic sans", 40)
SMALL_FONT = pygame.font.SysFont("comic sans", 20)
BUTTON_WIDTH, BUTTON_HEIGHT = 150, 50
BUTTON_X = (WIDTH - BUTTON_WIDTH) // 2
BUTTON_Y = HEIGHT - BUTTON_HEIGHT - 10  # Just above the bottom of the window
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
LIGHTBLUE = (173, 216, 230)
GRAY = (200, 200, 200)


#booleans to check if solved by user or not
solve_clicked = False
solved_by_user = False




# Fixed positions
fixed = [[num != 0 for num in row] for row in board]

# Screen setup
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Sudoku")


def is_valid_(unit):
    """Checks if an area has 2 of the same number or any number more 9 or less then 1"""
    digits = [d for d in unit if isinstance(d, int)] #isinstance checks if d is an integer
    return len(digits) == len(set(digits)) and all(1 <= d <= 9 for d in digits)

# Selected cell
selected = None

def draw_grid():
    """Draws a grid on the pygame window for the sudoku puzzle"""
    for x in range(GRID_SIZE + 1):
        width = 3 if x % 3 == 0 else 1
        pygame.draw.line(screen, BLACK, (x * CELL_SIZE, 0), (x * CELL_SIZE, WIDTH), width)
        pygame.draw.line(screen, BLACK, (0, x * CELL_SIZE), (WIDTH, x * CELL_SIZE), width)

def draw_solve_button():
    pygame.draw.rect(screen, LIGHTBLUE, (BUTTON_X, BUTTON_Y, BUTTON_WIDTH, BUTTON_HEIGHT))
    text = SMALL_FONT.render("Solve", True, BLACK)
    text_rect = text.get_rect(center=(BUTTON_X + BUTTON_WIDTH // 2, BUTTON_Y + BUTTON_HEIGHT // 2))
    screen.blit(text, text_rect)

def draw_numbers():
    """Display the initial numbers as black on the screen and all other numbers entered as gray for ease of use"""
    for i in range(GRID_SIZE):
        for j in range(GRID_SIZE):
            num = board[i][j]
            if num != 0:
                color = BLACK if fixed[i][j] else GRAY
                text = FONT.render(str(num), True, color)
                screen.blit(text, (j * CELL_SIZE + 20, i * CELL_SIZE + 10))


def draw_selected():
    """Function for showing what box the user is currently selecting for ease of use"""
    if selected:
        row, col = selected
        pygame.draw.rect(screen, LIGHTBLUE, (col * CELL_SIZE, row * CELL_SIZE, CELL_SIZE, CELL_SIZE))

 
def place_number(key):
    """Function for placing a number inputted by the user into a selected column by user"""
    if selected and not fixed[selected[0]][selected[1]]:
        board[selected[0]][selected[1]] = key


def is_valid_sodoku(board):
    """Checks if a finished Sudoku Board is correct or not"""
    #checks each row
    for row in board: 
        if not is_valid_(row):
            return False
    #checks each column
    for col in range(9):
        column = [board[row][col] for row in range(9)]
        if not is_valid_(column):
            return False
    #checks each 3x3 square 
    for sub_row in range(3):
        for sub_col in range(3):
            subgrid = []
            for row in range(sub_row * 3, (sub_row + 1) * 3):
                for col in range(sub_col * 3, (sub_col + 1) * 3):
                    subgrid.append(board[row][col])
            if not is_valid_(subgrid):
                return False
    return True

# Game loop
running = True
while running:
    
    #initialize window
    screen.fill(WHITE)
    draw_selected()
    draw_grid()
    draw_numbers()
    draw_solve_button()
    pygame.display.flip()
    pygame.time.wait(100)
    
    #filters through user inputs
    for event in pygame.event.get():
        #closes the window if the user presses x on the window
        if event.type == pygame.QUIT:
            running = False

        #selects the cell the user is clicking on
        if event.type == pygame.MOUSEBUTTONDOWN:
            x, y = pygame.mouse.get_pos()
            if x < WIDTH and y < WIDTH:
                selected = (y // CELL_SIZE, x // CELL_SIZE)
             # Check if clicked on "Solve" button
            elif BUTTON_X <= x <= BUTTON_X + BUTTON_WIDTH and BUTTON_Y <= y <= BUTTON_Y + BUTTON_HEIGHT:
                fill_board(board) #solves the puzzle
                solve_clicked = True #solved by computer

        #allows the user to enter and delete numbers when they type on the keyboard
        if event.type == pygame.KEYDOWN:
            if selected and event.unicode in '123456789':
                place_number(int(event.unicode))
                solved_by_user = True # solved by user
            elif event.key == pygame.K_BACKSPACE or event.key == pygame.K_DELETE:
                place_number(0)

        if is_valid_sodoku(board) and solved_by_user: 
            win_text = FONT.render("You win!!!!!", True, (0, 0, 0))
            screen.blit(win_text, (150, 537))
pygame.quit()
sys.exit()

#FOOTNOTES
# read through and used the copy, sys, and pygame libraries' documentation to help us understand how to use them properly to create this game
