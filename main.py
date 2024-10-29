from puzzle import *

from nicegui import ui


class GameButton(ui.button):
    def __init__(self, cell_state, size):
        super().__init__(color=cell_color_to_quasar_class(cell_state.color), on_click=cell_state.update)
        self.props("unelevated")

        # Hardcoded button sizes based on grid size...not ideal but it works
        if size == 5:
            self.classes("w-16 h-16 text-xl")
        elif size == 6:
            self.classes("w-[52px] h-[52px] text-xl")
        elif size == 7:
            self.classes("w-11 h-11 text-xl")
        elif size == 8:
            self.classes("w-10 h-10 text-lg")
        elif size == 9:
            self.classes("w-9 h-9 text-lg")
        elif size == 10:
            self.classes("w-8 h-8 text-lg")
        elif size == 11:
            self.classes("w-7 h-7")
        else:
            self.classes("w-[26px] h-[26px] text-sm")
        self.bind_text(cell_state).tailwind(f"font-mono rounded-none py-0 px-0 min-h-0")

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
        with ui.element('div').classes('flex flex-row justify-between my-4'):
            ui.button('⬅️ Prev', on_click=self.decrement_game)
            ui.button('Clear', on_click=self.clear_board, color='grey')
            ui.button('Next ➡️', on_click=self.increment_game)

        # Try to get a unique board
        self.timer = ui.timer(1, self.wait_for_unique_puzzle)
        self.attempts = 0
        self.display_unique()

    @ui.refreshable
    def display_game_metadata(self):
        ui.markdown(f'Grid size: {self.size}, puzzle index: {self.seed}')

    def wait_for_unique_puzzle(self):
        self.seed += 1
        self.puzzle.seed = self.seed
        self.puzzle.create_puzzle()
        self.attempts += 1
        self.display_game_metadata.refresh()
        self.display_board_ui.refresh()
        self.display_unique.refresh()            

    @ui.refreshable
    def display_unique(self):
        self.switch = ui.switch(f'Increment until you get a unique puzzle. Attempts: {self.attempts}').bind_value_to(self.timer, 'active')
        if self.size < 9:
            is_unique = self.puzzle.is_unique_puzzle()
        else:
            is_unique = "N/A (board too large algorithm too dumb)"
        if is_unique is not False:
            self.switch.set_value(False)
            self.timer.deactivate()
        ui.markdown(f'Unique board? {is_unique}')
        print(f'Unique: {is_unique} - Attempt {self.attempts}')

    @ui.refreshable
    def display_board_state(self):
        div_classes = 'rounded-md text-center p-2 mt-6'
        match self.game_state:
            case GridState.NOT_SOLVED:
                with ui.element('div').classes(f'bg-gray-200 {div_classes}'):
                    ui.label('Not solved')
            case GridState.SOLVED:
                with ui.element('div').classes(f'bg-green-200 {div_classes}'):
                    ui.label('Solved!')
            case GridState.ERROR:
                with ui.element('div').classes(f'bg-red-200 {div_classes}'):
                    ui.label('Invalid - see rules')

    def update_state(self):
        self.game_state = self.game_grid.evaluate_puzzle()
        self.display_board_state.refresh()

    @ui.refreshable
    def display_board_ui(self):
        if len(self.puzzle.queens) < self.size:
            ui.markdown(f'Failed to generate a valid board after {MAX_SOLUTION_ATTEMPTS} attempts. Please report this bug.')
            return

        self.game_grid = Grid(self.size)
        gap = "gap-1" if self.size < 8 else "gap-0.5"
        with ui.grid(columns=self.size).classes(f"w-fit place-self-center {gap} my-4").on('click', self.update_state):
            for i in range(self.size):
                for j in range(self.size):
                    cell_state = self.game_grid.grid[i][j]
                    cell_state.set_state(CellStates.CLEARED, self.puzzle.solution_grid.grid[i][j].color)
                    GameButton(cell_state, self.size)
    
    def clear_board(self):
        self.game_grid.clear()
        self.update_state()

    def decrement_game(self):
        self.seed -= 1
        self.recreate_board()

    def increment_game(self):
        self.seed += 1
        self.recreate_board()

    def recreate_board(self, size=None, seed=None):
        self.attempts = 0
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

with ui.element('div').classes('w-full'):
    with ui.element('div').classes('w-fit place-self-center'):
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

        with ui.element('div').classes('flex items-center justify-between'):
            with ui.dropdown_button('Grid size', auto_close=True):
                for i in range(MIN_GRID_SIZE, MAX_GRID_SIZE + 1):
                    ui.item(i, on_click=lambda i=i: board.recreate_board(size=i))
            ui.input(
                'Puzzle number',
                placeholder=0,
                on_change=lambda e: board.recreate_board(seed=e.value),
                validation=lambda value: f'Must be a number' if not value.isdigit() else None
            )
        board = GameBoard()

ui.run()