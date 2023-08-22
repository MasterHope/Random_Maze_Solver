import random as rand
import cv2 as cv
import threading
import time
import joblib
import calendar
from labyrinth import Labyrinth
from directions import *
from generatelabyrinth import GenerateLabyrinth
from drawlabyrinthsolve import LabyrinthDrawSolve
import found_path as fnd

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
    lab = Labyrinth(labyrinth_grid_dimension)
    GenerateLabyrinth.generateLabyrinth(lab)
    draw_solve = LabyrinthDrawSolve(lab, width_height_pixels)
    video, img = draw_solve.init_video_particles(file_name)
    draw_solve.find_exit_with_random_particles(video,img)
    fnd.FOUND_PATH=False

def parallel_program(labyrinth_grid_dimension, width_height_pixels,number_of_threads, file_name):
    lab = Labyrinth(labyrinth_grid_dimension)
    GenerateLabyrinth.generateLabyrinth(lab)
    draw_solve = LabyrinthDrawSolve(lab, width_height_pixels)
    img = draw_solve.create_labyrinth()
    video = draw_solve.create_video(img,file_name)
    lock = threading.Lock()
    joblib.Parallel(n_jobs=number_of_threads, prefer="threads")(
    joblib.delayed(draw_solve.find_exit_with_random_particles)(video, img,(rand.randrange(256),rand.randrange(256),rand.randrange(256)),lock) for _ in range(number_of_threads))
    fnd.FOUND_PATH=False



print("... Welcome to labyrinth particle solver program! ...")
labyrinth_grid_dimension = -1
def create_file_name_with_timestamp(file_name):
    current_GMT = time.gmtime()
    time_stamp = str(calendar.timegm(current_GMT))
    file_name = "".join(["video/",file_name, time_stamp,".avi"])
    print(file_name)
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
    

