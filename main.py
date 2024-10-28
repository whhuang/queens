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
        self.puzzle = Puzzle(self.size)

        # Game play
        self.game_state = GridState.NOT_SOLVED
        self.game_grid = Grid(self.size)
        self.display_board_state()
        self.display_board_ui()
        self.update_state()

        # Try to get a unique board
        self.timer = ui.timer(1, self.wait_for_unique_puzzle)
        self.switch = ui.switch('Refresh until you get a unique puzzle').bind_value_to(self.timer, 'active')
        self.attempts = 0
        self.display_attempts()

    def wait_for_unique_puzzle(self):
        self.puzzle.create_puzzle(self.attempts)
        self.attempts += 1
        print(f'Unique: {self.puzzle.is_unique_puzzle()} - Attempt {self.attempts}')
        self.display_board_ui.refresh()
        self.display_attempts.refresh()
        if self.puzzle.is_unique_puzzle():
            self.switch.set_value(False)
            self.timer.deactivate()

    @ui.refreshable
    def display_attempts(self):
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