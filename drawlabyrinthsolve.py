from labyrinth import Labyrinth

import math
import numpy as np
import cv2 as cv
import random as rand
import found_path as fnd
from cv2 import VideoWriter, VideoWriter_fourcc
from directions import *


FPS=120

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
            if(fnd.FOUND_PATH==True):
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
            if(fnd.FOUND_PATH==False):
                fnd.FOUND_PATH=True
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
            if current_grid_position[0]-1 > 0 and current_grid_position[1]-1 > 0:
                element_grid = self.labyrinth.get_grid()[current_grid_position[0]-1][current_grid_position[1]-1]
                if(element_grid.has_wall_south()==True and element_grid.has_wall_east()==True):
                    return False
                else:
                    return True
            else:
                return False
            
        elif self.is_particle_going_north(tuple_particle_position_new,first_point_delimiter) == True and self.is_particle_going_east(tuple_particle_position_new,second_point_delimiter):
            if current_grid_position[0]-1 > 0 and current_grid_position[1]+1 < self.labyrinth.get_dimension():
                element_grid = self.labyrinth.get_grid()[current_grid_position[0]-1][current_grid_position[1]+1]
                if(element_grid.has_wall_south()==True and element_grid.has_wall_west()==True):
                    return False
                else:
                    return True
            else:
                return False
        elif self.is_particle_going_south(tuple_particle_position_new,second_point_delimiter) == True and self.is_particle_going_west(tuple_particle_position_new,first_point_delimiter):
            if current_grid_position[0]+1 < self.labyrinth.get_dimension() and current_grid_position[1]-1 > 0:   
                element_grid = self.labyrinth.get_grid()[current_grid_position[0]+1][current_grid_position[1]-1]
                if(element_grid.has_wall_north()==True and element_grid.has_wall_east()==True):
                    return False
                else:
                    return True
            else:
                return False
        elif self.is_particle_going_south(tuple_particle_position_new,second_point_delimiter) == True and self.is_particle_going_east(tuple_particle_position_new,second_point_delimiter):
            if current_grid_position[0] +1 <self.labyrinth.get_dimension() and current_grid_position[1]+1 < self.labyrinth.get_dimension():
                element_grid = self.labyrinth.get_grid()[current_grid_position[0]+1][current_grid_position[1]+1]
                if(element_grid.has_wall_north()==True and element_grid.has_wall_west()==True):
                    return False
                else:
                    return True
            else:
                return False
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
