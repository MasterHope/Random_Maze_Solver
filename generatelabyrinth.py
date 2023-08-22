import random as rand
import networkx as nx
from labyrinth import Labyrinth
from labyrinthcell import LabyrinthCell
from directions import *

class GenerateLabyrinth:
    @staticmethod
    def generateLabyrinth(labyrinth: Labyrinth):
        grid = labyrinth.get_grid()
        dimension = labyrinth.get_dimension()
        for i in range(0, dimension):
            for j in range(0, dimension):
                grid[i][j] = LabyrinthCell(True, True, True, True)
        possible_positions = GenerateLabyrinth.generate_all_possible_positions(
            dimension
        )
        cells_in_maze = {(int(dimension / 2), int(dimension / 2))}
        while len(cells_in_maze) != dimension * dimension:
            path_closed = False
            path = []
            tuple_position = possible_positions.pop()
            row = tuple_position[0]
            column = tuple_position[1]
            while path_closed == False:
                avaiable_directions = [NORTH, SOUTH, EAST, WEST]
                if len(path) != 0:
                    GenerateLabyrinth.remove_short_cycles(path, avaiable_directions)
                direction = GenerateLabyrinth.get_random_direction(
                    dimension, row, column, avaiable_directions
                )
                if direction == -1:
                    found_direction = False
                    # recover previous configuration
                    while found_direction == False:
                        last_direction = path.pop()
                        row, column = GenerateLabyrinth.update_row_column_reverse_path(
                            last_direction, row, column
                        )
                        for _ in range(1, 4):
                            direction = (last_direction + 1) % 4
                            if GenerateLabyrinth.is_a_possible_direction(
                                direction, row, column, dimension
                            ):
                                found_direction = True
                else:
                    row, column = GenerateLabyrinth.update_row_column(
                        direction, row, column
                    )
                path.append(direction)
                if (row, column) in cells_in_maze:
                    GenerateLabyrinth.add_all_cells_to_maze(
                        row, column, path, cells_in_maze, grid, possible_positions
                    )
                    path_closed = True
        grid[dimension-1][dimension-1].wall_east = False

    @staticmethod
    def remove_short_cycles(path, avaiable_directions):
        last_direction = path[len(path) - 1]
        if last_direction == NORTH:
            avaiable_directions.remove(SOUTH)
        elif last_direction == SOUTH:
            avaiable_directions.remove(NORTH)
        if last_direction == WEST:
            avaiable_directions.remove(EAST)
        elif last_direction == EAST:
            avaiable_directions.remove(WEST)

    @staticmethod
    def get_random_direction(dimension, row, column, avaiable_directions):
        direction = -1
        while (
            direction not in avaiable_directions
            and len(avaiable_directions) != 0
            and GenerateLabyrinth.is_a_possible_direction(
                direction, row, column, dimension
            )
            == False
        ):
            direction = rand.choice(avaiable_directions)
            avaiable_directions.remove(direction)
        return direction

    @staticmethod
    def generate_all_possible_positions(dimension: int):
        positions = set()
        for i in range(0, dimension):
            for j in range(0, dimension):
                positions.add((i, j))
        return positions

    @staticmethod
    def add_all_cells_to_maze(
        row, column, path, cells_in_maze, grid, possible_positions
    ):
        g = nx.DiGraph()
        first_node = (row, column)
        g.add_node(first_node)
        while len(path) != 0:
            direction = path.pop()
            new_row, new_column = GenerateLabyrinth.update_row_column_reverse_path(
                direction, row, column
            )
            g.add_node((new_row, new_column))
            g.add_edge((new_row, new_column), (row, column), weight=direction)
            row = new_row
            column = new_column

        g = nx.minimum_spanning_arborescence(g)
        
        for edge in g.edges(data=True):
            direction = g.get_edge_data(edge[0], edge[1])["weight"]

            GenerateLabyrinth.set_walls(grid, edge[0][0], edge[0][1], direction)
            cells_in_maze.add(edge[0])
            cells_in_maze.add(edge[1])
            if edge[0] in possible_positions:
                possible_positions.remove(edge[0])
            if edge[1] in possible_positions:
                possible_positions.remove(edge[1])
        
    @staticmethod
    def set_walls(grid, row, column, direction):
        if direction == NORTH:
            grid[row][column].set_wall_north(False)
            if row - 1 >= 0:
                grid[row - 1][column].set_wall_south(False)
        elif direction == SOUTH:
            grid[row][column].set_wall_south(False)
            if row + 1 < grid.shape[0]:
                grid[row + 1][column].set_wall_north(False)
        elif direction == WEST:
            grid[row][column].set_wall_west(False)
            if column - 1 >= 0:
                grid[row][column - 1].set_wall_east(False)
        elif direction == EAST:
            grid[row][column].set_wall_east(False)
            if column + 1 < grid.shape[0]:
                grid[row][column + 1].set_wall_west(False)

    @staticmethod
    def update_row_column_reverse_path(last_direction: int, row: int, column: int):
        if last_direction == NORTH:
            row = row + 1
        elif last_direction == SOUTH:
            row = row - 1
        elif last_direction == WEST:
            column = column + 1
        elif last_direction == EAST:
            column = column - 1
        return row, column

    @staticmethod
    def update_row_column(last_direction: int, row: int, column: int):
        if last_direction == NORTH:
            row = row - 1
        elif last_direction == SOUTH:
            row = row + 1
        elif last_direction == WEST:
            column = column - 1
        elif last_direction == EAST:
            column = column + 1
        return row, column

    @staticmethod
    def is_a_possible_direction(direction, row, column, dimension):
        if direction == NORTH:
            if row - 1 >= 0:
                return True
        elif direction == SOUTH:
            if row + 1 < dimension:
                return True
        elif direction == WEST:
            if column - 1 >= 0:
                return True
        elif direction == EAST:
            if column + 1 < dimension:
                return True
        return False

