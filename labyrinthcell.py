class LabyrinthCell:
    def __init__(
        self, wall_north: bool, wall_south: bool, wall_east: bool, wall_west: bool
    ):
        self.wall_north = wall_north
        self.wall_south = wall_south
        self.wall_west = wall_west
        self.wall_east = wall_east

    def set_wall_north(self, wall_north):
        self.wall_north = wall_north

    def set_wall_south(self, wall_south):
        self.wall_south = wall_south

    def set_wall_west(self, wall_west):
        self.wall_west = wall_west

    def set_wall_east(self, wall_east):
        self.wall_east = wall_east

    def has_wall_north(self):
        return self.wall_north

    def has_wall_south(self):
        return self.wall_south

    def has_wall_west(self):
        return self.wall_west

    def has_wall_east(self):
        return self.wall_east

