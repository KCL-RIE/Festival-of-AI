from modified_pyamaze import maze 
import signal
import sys 


m = maze()
m.CreateMaze(loadMaze = 'Maze.csv', theme = 'light')  # Adjust the x and y values as needed

m.run()