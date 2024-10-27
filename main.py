import random

from nicegui import ui


ui.markdown('''
#### Play Queens!
''')

MIN_GRID_SIZE = 4
MAX_GRID_SIZE = 12
DEFAULT_GRID_SIZE = 8

class ButtonState:
    display = [' ', 'X', 'Q']

    def __init__(self):
        self.state = 0
        self.text = self.display[self.state]
    
    def update(self):
        self.state = (self.state + 1) % 3
        self.text = self.display[self.state]

    def set_state(self, state):
        '''
        internal/debug use only!!
        '''
        self.state = state
        self.text = self.display[self.state]

class GameButton(ui.button):
    def __init__(self, button_state, color):
        super().__init__(color=color, on_click=button_state.update)
        self.props("unelevated")
        self.bind_text(button_state).tailwind(f"font-mono size-16 text-xl rounded-none")

class GridSize:
    def __init__(self):
        self.size = 8

    def update(self, value):
        self.size = int(value)


class Grid:
    '''
    Grid design rules:
    - The grid is a square
    - All squares of the same color are connected (along x/y)
    - Don't make an impossible puzzle - maybe start with queen placements, then fill in the colors?
      - Puzzles with multiple solutions are invalid
    '''
    colors = ['red', 'blue', 'green', 'amber', 'purple', 'indigo', 'pink', 'teal', 'deep-orange', 'cyan', 'blue-grey', 'brown']
    assert(len(colors) >= MAX_GRID_SIZE)

    MAX_SOLUTION_ATTEMPTS = 10

    def __init__(self, size=DEFAULT_GRID_SIZE):
        random.seed(0)
        self.size = size
        self.solution_grid = [[]] # Solution grid type is a tuple of (is_queen, color_string)
        self.queens = [] # Queens is a list of (row, col, color)

        self.display_grid = [[]]
        self.create_grid()
        self.grid_ui()

    @ui.refreshable
    def grid_ui(self):
        if len(self.queens) < self.size:
            ui.markdown(f'Failed to generate a valid board after {self.MAX_SOLUTION_ATTEMPTS} attempts. Please report this bug.')
            return

        self.display_grid = [[0 for _ in range(self.size)] for _ in range(self.size)]
        with ui.grid(columns=self.size).classes("gap-1"):
            for i in range(self.size):
                for j in range(self.size):
                    cell = self.solution_grid[i][j]
                    self.display_grid[i][j] = cell[1]
                    button_state = ButtonState()
                    # DISPLAY SOLUTION - THIS IS FOR WHITNEY DEBUG
                    # button_state.set_state(cell[0] + 1)
                    GameButton(button_state, color=self.display_grid[i][j])

    def _create_solution(self):
        # Randomly place queens on the board such that they fulfill the following rules:
        # - No two queens are in the same row
        # - No two queens are in the same column
        # - No queen is directly neighboring another queen in all directions, including diagonals
        
        self.queens = []
        attempts = 0
        while len(self.queens) < self.size: 
            self.solution_grid = [[(0, "") for _ in range(self.size)] for _ in range(self.size)]
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
                    if self.solution_grid[max(0, row - 1)][max(0, col - 1)][0] == 0 and \
                    self.solution_grid[max(0, row - 1)][col][0] == 0 and \
                    self.solution_grid[max(0, row - 1)][min(self.size - 1, col + 1)][0] == 0 and \
                    self.solution_grid[row][max(0, col - 1)][0] == 0 and \
                    self.solution_grid[row][min(self.size - 1, col + 1)][0] == 0 and \
                    self.solution_grid[min(self.size - 1, row + 1)][max(0, col - 1)][0] == 0 and \
                    self.solution_grid[min(self.size - 1, row + 1)][col][0] == 0 and \
                    self.solution_grid[min(self.size - 1, row + 1)][min(self.size - 1, col + 1)][0] == 0:
                        color = self.colors[i]
                        self.solution_grid[row][col] = (1, color)
                        self.queens.append((row, col, color))
                        available_rows.remove(row)
                        available_cols.remove(col)
                        queen_success = True
                        break
                if not queen_success:
                    break
            attempts += 1
            if len(self.queens) < self.size and attempts > self.MAX_SOLUTION_ATTEMPTS:
                print(f'Failed after {attempts} attempts')
                break

    def create_grid(self):
        self._create_solution()
        empty_cells = [(i, j) for (i, row) in enumerate(self.solution_grid) for (j, col) in enumerate(row) if col[0] == 0]
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
                    self.solution_grid[current_row][current_col] = (0, queen_color)
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
                if selected_row > 0 and self.solution_grid[selected_row - 1][selected_col][0] == 0:
                    neighbor_colors.append(self.solution_grid[selected_row - 1][selected_col][1])
                if selected_row < self.size - 1 and self.solution_grid[selected_row + 1][selected_col][0] == 0:
                    neighbor_colors.append(self.solution_grid[selected_row + 1][selected_col][1])
                if selected_col > 0 and self.solution_grid[selected_row][selected_col - 1][0] == 0:
                    neighbor_colors.append(self.solution_grid[selected_row][selected_col - 1][1])
                if selected_col < self.size - 1 and self.solution_grid[selected_row][selected_col + 1][0] == 0:
                    neighbor_colors.append(self.solution_grid[selected_row][selected_col + 1][1])
                neighbor_colors = [color for color in neighbor_colors if color != ""]
                if len(neighbor_colors) > 0:
                    color = random.choice(neighbor_colors)
                    self.solution_grid[selected_row][selected_col] = (0, color)
                    empty_cells.remove((selected_row, selected_col))                

    def update(self, size):
        size_int = size
        if type(size) == str:
            if size.isdigit() and MIN_GRID_SIZE <= int(size) <= MAX_GRID_SIZE:
                size_int = int(size)
            else:
                return
        self.size = size_int
        self.create_grid()
        self.grid_ui.refresh()


ui.page_title('Queens')
ui.input(
    'Grid size',
    placeholder=DEFAULT_GRID_SIZE,
    on_change=lambda e: grid.update(e.value),
    validation=lambda value: f'Must be number between {MIN_GRID_SIZE} and {MAX_GRID_SIZE}' if not value.isdigit() or int(value) < MIN_GRID_SIZE or int(value) > MAX_GRID_SIZE else None
)
grid = Grid()


ui.run()