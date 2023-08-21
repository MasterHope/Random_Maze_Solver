import numpy as np
import random as rand
import cv2 as cv
import math
import networkx as nx
from cv2 import VideoWriter, VideoWriter_fourcc
import threading
import time
import joblib
import calendar

NORTH = 0
SOUTH = 1
EAST = 2
WEST = 3
NORTH_EAST = 4
NORTH_WEST = 5
SOUTH_EAST = 6
SOUTH_WEST = 7
FOUND_PATH = False

FPS=120


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


class LabyrinthDrawSolve:
    def __init__(self, labyrinth: Labyrinth, window_size: int):
        self.labyrinth = labyrinth
        self.window_size = window_size
        self.line_length = math.floor(window_size / labyrinth.get_dimension())

    def create_labyrinth(self):
        grid = self.labyrinth.get_grid()
        line_length = math.floor(self.line_length)
        img = self.create_window()
        x = 0
        y = -line_length
        for row in grid:
            y = y + line_length
            x = 0
            for cell in row:
                if cell.has_wall_north() == True:
                    self.draw_line(img, (x, y), (x + line_length, y))

                if cell.has_wall_south() == True:
                    self.draw_line(
                        img, (x, y + line_length), (x + line_length, line_length + y)
                    )

                if cell.has_wall_west() == True:
                    self.draw_line(img, (x, y), (x, y + line_length))

                if cell.has_wall_east() == True:
                    self.draw_line(
                        img, (x + line_length, y), (x + line_length, y + line_length)
                    )

                x = x + line_length
        self.draw_line(img, (0, 0), (line_length,0),color=(127,255,0))
        self.draw_line(img,(self.labyrinth.dimension*self.line_length,(self.labyrinth.dimension-1)*self.line_length),(self.labyrinth.dimension*self.line_length,self.labyrinth.dimension*self.line_length),(127,255,0))
        return img

    def create_window(self):
        img = np.zeros((self.window_size, self.window_size, 3), np.uint8)
        img.fill(255)
        return img

    def view_window(self, img):
        cv.imshow("Img", img)
        cv.waitKey(0)

    def draw_line(self, img, p1, p2, color=(0,0,0)):
        cv.line(img, p1, p2, color, 1)

    def create_video(self, img, filename="video.avi"):
        # set the video
        fourcc = VideoWriter_fourcc(*"MP42")
        video = VideoWriter(
            filename,
            fourcc,
            float(FPS),
            (self.window_size, self.window_size),
        )
        video.write(img)
        return video

    def init_video_particles(self, file_name="video.avi"):
        img = self.create_labyrinth()
        video = self.create_video(img, file_name)
        return video,img
    
    def find_exit_with_random_particles(self,video, img,color=(0,0,255),lock=None):
        global FOUND_PATH
        
        old_x = rand.randrange(self.line_length)
        old_y = 0

        current_grid_position = (0, 0)
        first_point_delimiter = (0, 0)
        second_point_delimiter = (self.line_length, self.line_length)
        path_particle = [(old_x, old_y)]
        path_grid = [(0, 0)]
        x = old_x
        y = old_y
        direction = self.get_random_point_direction()
        allowed_movements = self.get_allowed_movements(direction)
        #DO
        exit_x = (self.labyrinth.dimension*self.line_length)
        while y not in range((self.labyrinth.dimension-1)*self.line_length, self.labyrinth.dimension*self.line_length) or x != exit_x:
            if(FOUND_PATH==True):
                return 
            if(rand.randrange(1000)<=1):
                direction = self.get_random_point_direction()
                allowed_movements = self.get_allowed_movements(direction)
            if(current_grid_position==self.labyrinth.ending_cell):
                movement_x, movement_y= (1,0)
            else:
                movement_x, movement_y = rand.choice(allowed_movements)
            x += movement_x
            y += movement_y
            if self.is_particle_movement_allowed(
                current_grid_position,
                (x, y),
                first_point_delimiter,
                second_point_delimiter
            ):
                path_particle.append((x, y))     
                (
                    match,
                    new_cell,
                    first_point_delimiter,  
                    second_point_delimiter,
                ) = self.is_particle_go_to_new_cell(
                    current_grid_position,
                    (x, y),
                    first_point_delimiter,
                    second_point_delimiter,
                )
                if match == True:
                    path_grid.append(new_cell)
                    current_grid_position = new_cell
                allowed_movements = self.get_allowed_movements(direction)
            else:
                x -= movement_x
                y -= movement_y
                direction = self.get_random_point_direction()
                allowed_movements = self.get_allowed_movements(direction)
            old_x = x
            old_y = y
        if(lock!=None):
            lock.acquire()
            if(FOUND_PATH==False):
                FOUND_PATH=True
                self.draw_path_particle_final(path_particle, video, img,color)
            lock.release()
        else:
            self.draw_path_particle_final(path_particle, video, img,color)

    def draw_path_particle_final(self, path_particle,video,img, color):
        while(len(path_particle)!=0):
            x,y = path_particle.pop()
            cv.circle(img, (x, y), radius=0, color=color, thickness=-1)
            video.write(img)
        video.release()
            
    
    def get_random_point_direction(self):
        return rand.randrange(8)

    def get_allowed_movements(self,direction):
        if direction==NORTH:
            return [(0,-1),(1,-1),(-1,-1)]
        elif direction == SOUTH:
            return [(0,1),(1,1),(-1,1)]
        elif direction == EAST:
            return [(1,0),(1,1),(1,-1)]
        elif direction == WEST:
            return [(-1,0),(-1,1),(-1,-1)]
        elif direction==NORTH_EAST:
            return [(0,-1),(1,-1),(1,0)]
        elif direction == NORTH_WEST:
            return [(0,-1),(-1,-1),(-1,0)]
        elif direction == SOUTH_EAST:
            return [(0,1),(1,1),(1,0)]
        elif direction == SOUTH_WEST:
            return [(0,1),(-1,1),(-1,0)]

    def is_particle_go_to_new_cell(
        self,
        grid_position,
        tuple_position,
        first_point_delimiter,
        second_point_delimiter
    ):
        
        north_south_grid = grid_position[0]
        east_west_grid = grid_position[1]
        north_south_delimiter_first = first_point_delimiter[1]
        north_south_delimiter_second = second_point_delimiter[1]
        east_west_delimiter_first = first_point_delimiter[0]
        east_west_delimiter_second = second_point_delimiter[0]
        is_going = False
        if self.is_particle_going_north(tuple_position, first_point_delimiter):
            north_south_grid = north_south_grid - 1
            north_south_delimiter_first = north_south_delimiter_first-self.line_length
            north_south_delimiter_second = north_south_delimiter_second -self.line_length
            is_going=True
        if self.is_particle_going_south(tuple_position, second_point_delimiter):
            north_south_grid = north_south_grid + 1
            north_south_delimiter_first = north_south_delimiter_first+self.line_length
            north_south_delimiter_second = north_south_delimiter_second+self.line_length
            is_going=True
        if self.is_particle_going_east(tuple_position, second_point_delimiter):
            east_west_grid=east_west_grid + 1
            east_west_delimiter_first= east_west_delimiter_first+self.line_length
            east_west_delimiter_second=east_west_delimiter_second+self.line_length
            is_going=True
        if self.is_particle_going_west(tuple_position, first_point_delimiter):
            east_west_grid=east_west_grid - 1
            east_west_delimiter_first= east_west_delimiter_first-self.line_length
            east_west_delimiter_second=east_west_delimiter_second-self.line_length
            is_going=True
        return is_going, (north_south_grid,east_west_grid), (east_west_delimiter_first,north_south_delimiter_first), (east_west_delimiter_second,north_south_delimiter_second)


        
    def is_particle_movement_allowed(
        self,
        current_grid_position,
        tuple_particle_position_new,
        first_point_delimiter,
        second_point_delimiter,
    ):
        grid = self.labyrinth.get_grid()
        current_cell = grid[current_grid_position[0], current_grid_position[1]]
        if current_cell.has_wall_north() == True and self.is_particle_going_north(
            tuple_particle_position_new, first_point_delimiter
        ):
            return False
        elif current_cell.has_wall_south() == True and self.is_particle_going_south(
            tuple_particle_position_new, second_point_delimiter
        ):
            return False
        elif current_cell.has_wall_west() == True and self.is_particle_going_west(
            tuple_particle_position_new, first_point_delimiter
        ):
            return False
        elif current_cell.has_wall_east() == True and self.is_particle_going_east(
            tuple_particle_position_new, second_point_delimiter
        ):
            return False
        return self.diagonal_movement_is_possible(
        current_grid_position,
        tuple_particle_position_new,
        first_point_delimiter,
        second_point_delimiter)

    def diagonal_movement_is_possible(self,current_grid_position,
        tuple_particle_position_new,
        first_point_delimiter,
        second_point_delimiter):
        if self.is_particle_going_north(tuple_particle_position_new,first_point_delimiter) == True and self.is_particle_going_west(tuple_particle_position_new,first_point_delimiter):
            element_grid = self.labyrinth.get_grid()[current_grid_position[0]-1][current_grid_position[1]-1]
            if(element_grid.has_wall_south()==True and element_grid.has_wall_east()==True):
                return False
            else:
                return True
        elif self.is_particle_going_north(tuple_particle_position_new,first_point_delimiter) == True and self.is_particle_going_east(tuple_particle_position_new,second_point_delimiter):
            element_grid = self.labyrinth.get_grid()[current_grid_position[0]-1][current_grid_position[1]+1]
            if(element_grid.has_wall_south()==True and element_grid.has_wall_west()==True):
                return False
            else:
                return True
        elif self.is_particle_going_south(tuple_particle_position_new,second_point_delimiter) == True and self.is_particle_going_west(tuple_particle_position_new,first_point_delimiter):
            element_grid = self.labyrinth.get_grid()[current_grid_position[0]+1][current_grid_position[1]-1]
            if(element_grid.has_wall_north()==True and element_grid.has_wall_east()==True):
                return False
            else:
                return True
        elif self.is_particle_going_south(tuple_particle_position_new,second_point_delimiter) == True and self.is_particle_going_east(tuple_particle_position_new,second_point_delimiter):
            element_grid = self.labyrinth.get_grid()[current_grid_position[0]+1][current_grid_position[1]+1]
            if(element_grid.has_wall_north()==True and element_grid.has_wall_west()==True):
                return False
            else:
                return True
        return True

    def is_particle_going_east(
        self, tuple_particle_position_new, second_point_delimiter
    ):
        return tuple_particle_position_new[0] >= second_point_delimiter[0]

    def is_particle_going_west(
        self, tuple_particle_position_new, first_point_delimiter
    ):
        return tuple_particle_position_new[0] <= first_point_delimiter[0]

    def is_particle_going_south(
        self, tuple_particle_position_new, second_point_delimiter
    ):
        return tuple_particle_position_new[1] >= second_point_delimiter[1]

    def is_particle_going_north(
        self, tuple_particle_position_new, first_point_delimiter
    ):
        return tuple_particle_position_new[1] <= first_point_delimiter[1]


#main functions

def show_video(file_name):
    capture = cv.VideoCapture(file_name)
    while capture.isOpened():
        result, frame = capture.read()
        if result == True:
            frame = cv.resize(frame,(512,512))
            cv.imshow(file_name, frame)
            if(cv.waitKey(1) & 0xFF == ord('q')):
                break
        else:
            break
    capture.release()
    cv.destroyAllWindows()


def sequential_program(labyrinth_grid_dimension, width_height_pixels, file_name):
    global FOUND_PATH
    lab = Labyrinth(labyrinth_grid_dimension)
    GenerateLabyrinth.generateLabyrinth(lab)
    draw_solve = LabyrinthDrawSolve(lab, width_height_pixels)
    video, img = draw_solve.init_video_particles(file_name)
    draw_solve.find_exit_with_random_particles(video,img)
    FOUND_PATH=False

def parallel_program(labyrinth_grid_dimension, width_height_pixels,number_of_threads, file_name):
    global FOUND_PATH
    lab = Labyrinth(labyrinth_grid_dimension)
    GenerateLabyrinth.generateLabyrinth(lab)
    draw_solve = LabyrinthDrawSolve(lab, width_height_pixels)
    img = draw_solve.create_labyrinth()
    video = draw_solve.create_video(img,file_name)
    lock = threading.Lock()
    joblib.Parallel(n_jobs=number_of_threads, prefer="threads")(
    joblib.delayed(draw_solve.find_exit_with_random_particles)(video, img,(rand.randrange(256),rand.randrange(256),rand.randrange(256)),lock) for _ in range(number_of_threads))
    FOUND_PATH = False
    print(FOUND_PATH)



print("... Welcome to labyrinth particle solver program! ...")
labyrinth_grid_dimension = -1
def create_file_name_with_timestamp(file_name):
    current_GMT = time.gmtime()
    time_stamp = str(calendar.timegm(current_GMT))
    file_name = "".join([file_name, time_stamp,".avi"])
    return file_name

while(labyrinth_grid_dimension<=0):
    labyrinth_grid_dimension_aux = input("Choice the dimension of the grid of the labyrinth - we reccomend to use small grid to make sure the program ends ")
    if(labyrinth_grid_dimension_aux.isnumeric()):
        if(int(labyrinth_grid_dimension_aux) <= 0):
            print("The grid value should be higher than zero... Try to insert a different number")
        else:
            labyrinth_grid_dimension = int(labyrinth_grid_dimension_aux)
    else:
        print("The dimension of the grid must be numeric. Try to insert a different value...")
    while True:
                choice = input("Do you want to run parallel or sequential version? --- Type '1' for sequential or '2' for parallel or 'Any Key' to close ")
                if choice == "1" or choice == "2":
                    if choice == "1" :
                        print("...Sequential program is running... When the program ends, a video will open. Press q to close the video...")
                        start_time = time.time()
                        file_name = create_file_name_with_timestamp("sequential_path")
                        sequential_program(labyrinth_grid_dimension,256,file_name)
                        print("Time in seconds sequential program:",time.time()- start_time)
                        show_video(file_name)
                    elif choice=="2":
                        num_threads = -1
                        while num_threads<=-1:
                            num_threads_aux = input("Insert number of threads to use ")
                            if num_threads_aux.isnumeric() == False:
                                print("Number of threads must be a number... Try insert a different value...")
                            else:
                                if(int(num_threads_aux)<=0):
                                    print("Number of threads must be a positive number... Try insert a different value...")
                                else:
                                    num_threads = int(num_threads_aux)
                        print("...Parallel program is running... When the program ends, a video will open. Press q to close the video...")
                        start_time = time.time()
                        file_name = create_file_name_with_timestamp("parallel_path")
                        parallel_program(int(labyrinth_grid_dimension),256,num_threads, file_name)
                        print("Time in seconds parallel program:",time.time()- start_time)
                        show_video(file_name)
                else:
                    print("...GoodBye!...")
                    break
    

