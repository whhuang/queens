import random

from enum import Enum
from itertools import permutations


#######################
# CONSTANTS 
#######################

MIN_GRID_SIZE = 5
MAX_GRID_SIZE = 12
DEFAULT_GRID_SIZE = 5
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

class GridState(Enum):
    NOT_SOLVED = 0
    SOLVED = 1
    ERROR = 2


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

class Grid:
    def __init__(self, size):
        self.size = size
        self.grid = [[CellState() for _ in range(self.size)] for _ in range(self.size)]

    # For testing purposes
    def grid_from_2d_color_index_array(array):
        grid = Grid(len(array))
        for i, row in enumerate(array):
            for j, cell in enumerate(row):
                grid.grid[i][j].set_state(CellStates.CLEARED, cell)
        return grid

    # For testing purposes
    def display(self):
        print('\n'.join(['|'.join([f'{cell.color}:{cell.text}' for cell in row]) for row in self.grid]))
        print('\n')

    def clear(self):
        for row in self.grid:
            for cell in row:
                cell.set_state(CellStates.CLEARED)
    
    def copy_clear(self):
        new_grid = Grid(self.size)
        for i in range(self.size):
            for j in range(self.size):
                new_grid.grid[i][j].set_state(CellStates.CLEARED, self.grid[i][j].color)
        return new_grid

    def evaluate_puzzle(self):
        # Evaluate the state of the grid according to the rules of Queens
        # Iterate through the display grid and check:
        # - If any of the following rules are violated, the game is in error:
        #   - No two queens are in the same row
        #   - No two queens are in the same column
        #   - No queen is directly neighboring another queen in all directions, including diagonals
        #   - No two queens are the same color
        # - If there are no errors and all queens are placed, the game is successful
        # - Otherwise, the game is by default not solved
        game_queens = []
        for i in range(self.size):
            for j in range(self.size):
                if self.grid[i][j].state == CellStates.QUEEN:
                    game_queens.append((i, j, self.grid[i][j].color))
        # Check if the queen placements are valid
        for queen in game_queens:
            row, col, color = queen
            for other_queen in game_queens:
                if queen == other_queen:
                    continue
                other_row, other_col, other_color = other_queen
                if row == other_row or col == other_col or (abs(row - other_row) <= 1 and abs(col - other_col) <= 1) or color == other_color:
                    return GridState.ERROR
        # If game state is valid and all queens are placed, the game is successful
        if len(game_queens) == self.size:
            return GridState.SOLVED
        return GridState.NOT_SOLVED

    def is_unique_puzzle(self):
        # Brute force grid solve in the dumbest way possible. TODO: optimize this (ignore neighbors, unique colors)
        attempted_solution_grid = self.copy_clear()
        valid_solutions = 0
        for perm in permutations(range(self.size)):                
            for row, col in enumerate(perm):
                attempted_solution_grid.grid[row][col].set_state(CellStates.QUEEN)
            if attempted_solution_grid.evaluate_puzzle() == GridState.SOLVED:
                valid_solutions += 1
                if valid_solutions > 1:
                    break
            attempted_solution_grid.clear()
        if valid_solutions == 1:
            return True
        return False

class Puzzle:
    '''
    Puzzle design rules:
    - The grid is a square
    - All squares of the same color are connected (along x/y)
    - Don't make an impossible puzzle - maybe start with queen placements, then fill in the colors?
      - Puzzles with multiple solutions are invalid
    '''
    def __init__(self, size=DEFAULT_GRID_SIZE, seed=0):
        self.size = size
        self.seed = seed
        self.solution_grid = Grid(size)
        self.queens = [] # Queens is a list of (row, col, color_index)
        self.create_puzzle()
    
    def _create_random_solution(self):
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

    def create_puzzle(self):
        random.seed(self.seed)
        self._create_random_solution()
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
        
    def is_unique_puzzle(self):
        return self.solution_grid.is_unique_puzzle()
