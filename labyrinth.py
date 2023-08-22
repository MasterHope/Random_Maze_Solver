from labyrinthcell import LabyrinthCell
import numpy as np


class Labyrinth:
    def __init__(
        self, dimension: int
    ):
        self.dimension = dimension
        self.grid = np.empty((dimension, dimension), dtype=LabyrinthCell)
        self.starting_cell = (0,0)
        self.ending_cell = (dimension - 1, dimension - 1)

    def get_grid(self):
        return self.grid

    def get_dimension(self):
        return self.dimension

    def get_ending_cell(self):
        return self.ending_cell
