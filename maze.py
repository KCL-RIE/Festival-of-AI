from modified_pyamaze import maze, agent, COLOR
import signal
import sys 


m = maze()
m.CreateMaze(loadMaze = 'Maze.csv', theme = 'light')  # Adjust the x and y values as needed

a = agent(m, 10, 10, footprints=True, shape='arrow')
print(m.path)
m.tracePath({a:m.path})
m.run()