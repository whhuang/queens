import random

from enum import Enum
from nicegui import ui


#######################
# CONSTANTS 
#######################

MIN_GRID_SIZE = 4
MAX_GRID_SIZE = 12
DEFAULT_GRID_SIZE = 8
MAX_SOLUTION_ATTEMPTS = 10


#######################
# ENUMS 
#######################

class CellStates(Enum):
    CLEARED = 0
    NOT_QUEEN = 1
    QUEEN = 2

def display_cell_states(value: CellStates):
    return [' ', 'X', 'Q'][value.value]

class CellColors(Enum):
    NONE = 0
    RED = 1
    BLUE = 2
    GREEN = 3
    AMBER = 4
    PURPLE = 5
    INDIGO = 6
    PINK = 7
    TEAL = 8
    DEEP_ORANGE = 9
    CYAN = 10
    BLUE_GREY = 11
    BROWN = 12

def cell_color_to_quasar_class(value: CellColors):
    colors = [' ', 'red', 'blue', 'green', 'amber', 'purple', 'indigo', 'pink', 'teal', 'deep-orange', 'cyan', 'blue-grey', 'brown']
    return colors[value.value]

assert(len(CellColors) > MAX_GRID_SIZE)


#######################
# CLASSES 
#######################

class CellState:
    def __init__(self, color: CellColors=CellColors.NONE):
        self.state = CellStates.CLEARED
        self.color = color
        self.text = display_cell_states(self.state)
    
    def update(self):
        self.state = CellStates((self.state.value + 1) % 3)
        self.text = display_cell_states(self.state)

    def set_state(self, state: CellStates, color: CellColors=None):
        self.state = state
        self.text = display_cell_states(self.state)
        if color is not None:
            self.color = color

class GameButton(ui.button):
    def __init__(self, cell_state):
        super().__init__(color=cell_color_to_quasar_class(cell_state.color), on_click=cell_state.update)
        self.props("unelevated")
        self.bind_text(cell_state).tailwind(f"font-mono size-16 text-xl rounded-none")

class Grid:
    def __init__(self, size):
        self.size = size
        self.grid = [[CellState() for _ in range(self.size)] for _ in range(self.size)]

class Puzzle:
    '''
    Puzzle design rules:
    - The grid is a square
    - All squares of the same color are connected (along x/y)
    - Don't make an impossible puzzle - maybe start with queen placements, then fill in the colors?
      - Puzzles with multiple solutions are invalid
    '''
    def __init__(self, size=DEFAULT_GRID_SIZE):
        random.seed(0)
        # Game setup
        self.size = size
        self.solution_grid = Grid(size)
        self.queens = [] # Queens is a list of (row, col, color_index)
        self.create_random_solution()
        self.create_game()
    
    def create_random_solution(self):
        # Randomly place queens on the board such that they fulfill the following rules:
        # - No two queens are in the same row
        # - No two queens are in the same column
        # - No queen is directly neighboring another queen in all directions, including diagonals
        self.queens = []
        attempts = 0
        while len(self.queens) < self.size: 
            self.solution_grid = Grid(self.size)
            self.queens = []
            available_rows = list(range(self.size))
            available_cols = list(range(self.size))
            for i in range(self.size):
                queen_success = False
                # Create a list of all possible row/column combinations
                options = [(row, col) for row in available_rows for col in available_cols]
                while len(options) > 0:
                    choice = random.randrange(len(options))
                    row, col = options.pop(choice)
                    # Check whether there are any neighboring queens
                    if self.solution_grid.grid[max(0, row - 1)][max(0, col - 1)].state == CellStates.CLEARED and \
                    self.solution_grid.grid[max(0, row - 1)][col].state == CellStates.CLEARED and \
                    self.solution_grid.grid[max(0, row - 1)][min(self.size - 1, col + 1)].state == CellStates.CLEARED and \
                    self.solution_grid.grid[row][max(0, col - 1)].state == CellStates.CLEARED and \
                    self.solution_grid.grid[row][min(self.size - 1, col + 1)].state == CellStates.CLEARED and \
                    self.solution_grid.grid[min(self.size - 1, row + 1)][max(0, col - 1)].state == CellStates.CLEARED and \
                    self.solution_grid.grid[min(self.size - 1, row + 1)][col].state == CellStates.CLEARED and \
                    self.solution_grid.grid[min(self.size - 1, row + 1)][min(self.size - 1, col + 1)].state == CellStates.CLEARED:
                        color = CellColors(i + 1) # Colors are 1-indexed
                        self.solution_grid.grid[row][col].set_state(CellStates.QUEEN, color)
                        self.queens.append((row, col, color))
                        available_rows.remove(row)
                        available_cols.remove(col)
                        queen_success = True
                        break
                if not queen_success:
                    break
            attempts += 1
            if len(self.queens) < self.size and attempts > MAX_SOLUTION_ATTEMPTS:
                print(f'Failed after {attempts} attempts')
                break

    def create_game(self):
        empty_cells = [(i, j) for (i, row) in enumerate(self.solution_grid.grid) for (j, cell) in enumerate(row) if cell.state == CellStates.CLEARED]
        while len(empty_cells) > 0:
            # Start with a random empty space
            selected_row, selected_col = random.choice(empty_cells)
            # Calculate euclidean distance to all queens, use the inverse of the distance as a weight
            queen_weights = []
            for queen in self.queens:
                queen_row, queen_col, _ = queen
                distance = ((queen_row - selected_row) ** 2 + (queen_col - selected_col) ** 2) ** 0.5
                queen_weights.append((1 / distance))
            # Select a random queen based on the weights
            queen_row, queen_col, queen_color = random.choices(self.queens, queen_weights)[0]
            # Draw a line of empty cells from the queen to the current selected cell
            # If we get "stuck" or reach the selected cell, continue on to the next empty cell selection.
            prev_row, prev_col = queen_row, queen_col
            empty_cells_removed = 0
            while True:
                # 1. Determine all empty cells that are adjacent to the queen in the direction of the selected cell
                cell_options = []
                if selected_row < prev_row and (prev_row - 1, prev_col) in empty_cells:
                    cell_options.append((prev_row - 1, prev_col))
                elif selected_row > prev_row and (prev_row + 1, prev_col) in empty_cells:
                    cell_options.append((prev_row + 1, prev_col))
                if selected_col < prev_col and (prev_row, prev_col - 1) in empty_cells:
                    cell_options.append((prev_row, prev_col - 1))
                elif selected_col > prev_col and (prev_row, prev_col + 1) in empty_cells:
                    cell_options.append((prev_row, prev_col + 1))
                # 2. Select a random cell and color it the same as the queen. If we have reached the selected cell or have no more options, break the loop
                if len(cell_options) > 0:
                    current_row, current_col = random.choice(cell_options)
                    self.solution_grid.grid[current_row][current_col].set_state(CellStates.CLEARED, queen_color)
                    empty_cells.remove((current_row, current_col))
                    empty_cells_removed += 1
                    if current_row == selected_row and current_col == selected_col:
                        break
                    prev_row, prev_col = current_row, current_col
                else:
                    break
            if empty_cells_removed == 0:
                # There is no path between this cell and our selected queen, so let's continue with a different strategy.
                # Check all neighbors of the selected cell and color them the same as one of its direct (non-diagonal) neighbors
                neighbor_colors = []
                if selected_row > 0 and self.solution_grid.grid[selected_row - 1][selected_col].state == CellStates.CLEARED:
                    neighbor_colors.append(self.solution_grid.grid[selected_row - 1][selected_col].color)
                if selected_row < self.size - 1 and self.solution_grid.grid[selected_row + 1][selected_col].state == CellStates.CLEARED:
                    neighbor_colors.append(self.solution_grid.grid[selected_row + 1][selected_col].color)
                if selected_col > 0 and self.solution_grid.grid[selected_row][selected_col - 1].state == CellStates.CLEARED:
                    neighbor_colors.append(self.solution_grid.grid[selected_row][selected_col - 1].color)
                if selected_col < self.size - 1 and self.solution_grid.grid[selected_row][selected_col + 1].state == CellStates.CLEARED:
                    neighbor_colors.append(self.solution_grid.grid[selected_row][selected_col + 1].color)
                neighbor_colors = [color for color in neighbor_colors if color != CellColors.NONE]
                if len(neighbor_colors) > 0:
                    color = random.choice(neighbor_colors)
                    self.solution_grid.grid[selected_row][selected_col].set_state(CellStates.CLEARED, color)
                    empty_cells.remove((selected_row, selected_col))

    def create_unique_game():
        unique_solution = False
        while not unique_solution:
            self.create_grid()
            # Brute force grid solve

            unique_solution = True

class GameBoard:
    '''
    Game board that contains the game state and renders UI elements
    '''

    class GameState(Enum):
        NOT_INITIALIZED = 0
        READY = 1
        IN_PROGRESS = 2
        SUCCESS = 3
        ERROR = 4

    def __init__(self, size=DEFAULT_GRID_SIZE):
        # Game setup
        self.size = size
        self.puzzle = Puzzle(self.size)

        # Game play
        self.game_state = self.GameState.NOT_INITIALIZED
        self.display_grid = [[]]
        self.display_board_state()
        self.display_board_ui()
        self.update_state()

    @ui.refreshable
    def display_board_state(self):
        ui.markdown(f'Game state: {str(self.game_state)}')

    def _evaluate_state(self):
        # Evaluate the current state of the game based on the user inputs
        # If self.queens is not fully populated, the game is not initialized
        if len(self.puzzle.queens) < self.size:
            self.game_state = self.GameState.NOT_INITIALIZED
            return
        # Now iterate through the display grid and check:
        # - If all 0's, the game is ready
        # - If any of the following rules are violated, the game is in error:
        #   - No two queens are in the same row
        #   - No two queens are in the same column
        #   - No queen is directly neighboring another queen in all directions, including diagonals
        # - If there are no errors and all queens are placed, the game is successful
        # - Otherwise, the game is in progress
        self.game_state = self.GameState.READY
        game_queens = []
        for i in range(self.size):
            for j in range(self.size):
                if self.display_grid[i][j].state != CellStates.CLEARED:
                    self.game_state = self.GameState.IN_PROGRESS
                if self.display_grid[i][j].state == CellStates.QUEEN:
                    game_queens.append((i, j))
        # Check if the queen placements are valid
        for queen in game_queens:
            row, col = queen
            for other_queen in game_queens:
                if queen == other_queen:
                    continue
                other_row, other_col = other_queen
                if row == other_row or col == other_col or (abs(row - other_row) <= 1 and abs(col - other_col) <= 1):
                    self.game_state = self.GameState.ERROR
                    return
        # If game state is valid and all queens are placed, the game is successful
        if len(game_queens) == self.size:
            self.game_state = self.GameState.SUCCESS
    
    def update_state(self):
        self._evaluate_state()
        self.display_board_state.refresh()

    @ui.refreshable
    def display_board_ui(self):
        if len(self.puzzle.queens) < self.size:
            ui.markdown(f'Failed to generate a valid board after {MAX_SOLUTION_ATTEMPTS} attempts. Please report this bug.')
            return

        self.display_grid = [[None for _ in range(self.size)] for _ in range(self.size)]
        with ui.grid(columns=self.size).classes("gap-1").on('click', self.update_state):
            for i in range(self.size):
                for j in range(self.size):
                    cell = self.puzzle.solution_grid.grid[i][j]
                    button_state = CellState(cell.color)
                    self.display_grid[i][j] = button_state
                    # DISPLAY SOLUTION - THIS IS FOR WHITNEY DEBUG
                    # button_state.set_state(cell[0] + 1)
                    GameButton(button_state)
    
    def clear_board(self):
        for i in range(self.size):
            for j in range(self.size):
                button = self.display_grid[i][j]
                button.set_state(CellStates.CLEARED)
        self.update_state()               

    def recreate_board(self, size):
        size_int = size
        if type(size) == str:
            if size.isdigit() and MIN_GRID_SIZE <= int(size) <= MAX_GRID_SIZE:
                size_int = int(size)
            else:
                return
        self.size = size_int
        self.puzzle = Puzzle(self.size)
        self.display_board_ui.refresh()


#######################
# RENDER PAGE
#######################

ui.markdown('''
#### Play Queens!
''')
ui.page_title('Queens')
ui.input(
    'Grid size',
    placeholder=DEFAULT_GRID_SIZE,
    on_change=lambda e: board.recreate_board(e.value),
    validation=lambda value: f'Must be number between {MIN_GRID_SIZE} and {MAX_GRID_SIZE}' if not value.isdigit() or int(value) < MIN_GRID_SIZE or int(value) > MAX_GRID_SIZE else None
)
board = GameBoard()
ui.button('Clear', on_click=board.clear_board)

ui.run()