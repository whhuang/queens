from puzzle import Grid

import unittest

class TestPuzzle(unittest.TestCase):

    def test_is_unique_puzzle(self):
        unique_game = [
            [1, 1, 1, 1, 2, 2, 2, 1],
            [1, 3, 1, 1, 2, 2, 2, 1],
            [4, 4, 4, 1, 2, 2, 2, 1],
            [4, 4, 4, 1, 1, 1, 1, 1],
            [4, 4, 4, 1, 1, 1, 5, 5],
            [6, 6, 1, 1, 1, 1, 5, 5],
            [6, 6, 1, 7, 7, 1, 8, 1],
            [1, 1, 1, 7, 7, 1, 1, 1]
        ]
        grid = Grid.grid_from_2d_color_index_array(unique_game)
        self.assertTrue(grid.is_unique_puzzle())

if __name__ == '__main__':
    unittest.main()