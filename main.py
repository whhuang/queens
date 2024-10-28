from puzzle import *

from nicegui import ui


class GameButton(ui.button):
    def __init__(self, cell_state):
        super().__init__(color=cell_color_to_quasar_class(cell_state.color), on_click=cell_state.update)
        self.props("unelevated")
        self.bind_text(cell_state).tailwind(f"font-mono size-16 text-xl rounded-none")

class GameBoard:
    '''
    Game board that contains the game state and renders UI elements
    '''

    def __init__(self, size=DEFAULT_GRID_SIZE):
        # Game setup
        self.size = size
        self.seed = 0
        self.puzzle = Puzzle(self.size)
        self.display_game_metadata()

        # Game play
        self.game_state = GridState.NOT_SOLVED
        self.game_grid = Grid(self.size)
        self.display_board_state()
        self.display_board_ui()
        self.update_state()
        with ui.row():
            ui.button('Clear', on_click=self.clear_board)
            ui.button('Next', on_click=self.increment_game)

        # Try to get a unique board
        self.timer = ui.timer(1, self.wait_for_unique_puzzle)
        self.switch = ui.switch('Increment until you get a unique puzzle').bind_value_to(self.timer, 'active')
        self.attempts = 0
        self.display_unique()

    @ui.refreshable
    def display_game_metadata(self):
        ui.markdown(f'Grid size: {self.size}, puzzle index: {self.seed}')

    def wait_for_unique_puzzle(self):
        self.puzzle.create_puzzle(self.attempts)
        self.attempts += 1
        print(f'Unique: {self.puzzle.is_unique_puzzle()} - Attempt {self.attempts}')
        self.display_board_ui.refresh()
        self.display_unique.refresh()
        if self.puzzle.is_unique_puzzle():
            self.switch.set_value(False)
            self.timer.deactivate()

    @ui.refreshable
    def display_unique(self):
        ui.markdown(f'Unique board? {self.puzzle.is_unique_puzzle()}. Attempt {self.attempts}')

    @ui.refreshable
    def display_board_state(self):
        ui.markdown(f'Game state: {str(self.game_state)}')

    def update_state(self):
        self.game_state = self.game_grid.evaluate_puzzle()
        self.display_board_state.refresh()

    @ui.refreshable
    def display_board_ui(self):
        if len(self.puzzle.queens) < self.size:
            ui.markdown(f'Failed to generate a valid board after {MAX_SOLUTION_ATTEMPTS} attempts. Please report this bug.')
            return

        self.game_grid = Grid(self.size)
        with ui.grid(columns=self.size).classes("gap-1").on('click', self.update_state):
            for i in range(self.size):
                for j in range(self.size):
                    cell_state = self.game_grid.grid[i][j]
                    cell_state.set_state(CellStates.CLEARED, self.puzzle.solution_grid.grid[i][j].color)
                    GameButton(cell_state)
    
    def clear_board(self):
        self.game_grid.clear()
        self.update_state()

    def increment_game(self):
        self.seed += 1
        self.recreate_board()

    def recreate_board(self, size=None, seed=None):
        if size is not None:
            size_int = size
            if type(size) == str:
                if size.isdigit() and MIN_GRID_SIZE <= int(size) <= MAX_GRID_SIZE:
                    size_int = int(size)
                else:
                    return
            self.size = size_int
        if seed is not None:
            if type(seed) == str:
                if seed.isdigit():
                    self.seed = int(seed)
                else:
                    return
            self.seed = seed
        self.puzzle = Puzzle(self.size, self.seed)
        self.display_game_metadata.refresh()
        self.display_board_ui.refresh()
        self.display_unique.refresh()


#######################
# RENDER PAGE
#######################

ui.page_title('Queens')

ui.markdown('''
#### Play Queens!
''')

with ui.expansion('How to play', icon='info'):
    ui.markdown('''
##### Rules

- There is one and only one queen per row, column, and color
- No queen can be within 1 square (including diagonals) of another queen
- Place all queens to solve the puzzle
''')

with ui.row():
    ui.input(
        'Grid size',
        placeholder=DEFAULT_GRID_SIZE,
        on_change=lambda e: board.recreate_board(size=e.value),
        validation=lambda value: f'Must be number between {MIN_GRID_SIZE} and {MAX_GRID_SIZE}' if not value.isdigit() or int(value) < MIN_GRID_SIZE or int(value) > MAX_GRID_SIZE else None
    )
    ui.input(
        'Puzzle number',
        placeholder=0,
        on_change=lambda e: board.recreate_board(seed=e.value),
        validation=lambda value: f'Must be a number' if not value.isdigit() else None
    )
board = GameBoard()

ui.run()