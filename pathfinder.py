import math, pygame, sys
from heapq import heapify, heappop, heappush

'''
The code, an implementation of the A* algorithm, below was used in my AmadorUAV submission questions
The link to the Github repo is Question 3 of https://github.com/TheErickLiu/AmadorUAV_EA
Modifications were made to accompany the GUI.
'''

class Point:
    def __init__(self, x, y, f_score = 0, g_score = 0, state = 0, parent = None):
        self.x = x
        self.y = y
        self.f_score = f_score # Total distance to the start and to the end
        self.g_score = g_score # distance to the start
        self.state = state # 0 means OPEN, 1 means CLOSED
        self.parent = parent
    
    # Compare function of Point
    def __lt__(self, other):
        return self.f_score < other.f_score

def neighbors(p: Point, obstacles: set, N: int, M: int) -> list:

    '''
    neighbors finds the coordinates of all eligable points next to p.
    :param p: Input point
    :param obstacles: Set of points that can not be visited
    :param N: height of the grid
    :param M: width of the grid
    :return: List of points that can be visited.
    '''

    good_neighbors = []
    
    directions = [(0, 1), (0, -1), (1, 0), (-1, 0), (1, 1), (-1, -1), (1, -1), (-1, 1)]

    for d in directions:
        x, y = p.x + d[0], p.y + d[1]
        if (x, y) in obstacles or y <= 0 or x <= 0 or y >= N or x >= M:
            continue

        # Check for obstacles blocking diagonal movement
        if d[0] != 0 and d[1] != 0:
            if (p.x + d[0], p.y) in obstacles or (p.x, p.y + d[1]) in obstacles:
                continue

        good_neighbors.append((x, y))
    
    return good_neighbors

def retrace_steps(p: Point) -> list:
    '''
    retrace_steps starts from the end and finds the path back to the start.
    :param p: The end point of the path.
    :return: The path from the start point to the end point.
    '''

    current, path = p, []

    while current:
        path.append((current.x, current.y))
        current = current.parent
    
    return path[::-1]

def navigate(p1: tuple, p2: tuple, obstacles: set, N: int, M: int) -> list:

    '''
    navigate implements the A* Algorithm to find the path between two points.
    :param p1: Start point of the path
    :param p2: End Point of the path
    :param obstacles: Set of points that can not be used in the path
    :param N: height of the grid
    :param M: width of the grid
    :return: The path from the start point to the end point.
    '''
    # Candidates for checking the next stop. We use a heap to optimize finding the point with the least distance.
    openpoints = []
    start = Point(p1[0], p1[1])
    heappush(openpoints, start)

    # Dictionary of points that have already been seen
    visited = {p1: start}

    while openpoints:
        current = heappop(openpoints)
        # Marks this point as CLOSED
        current.state = 1

        # If end is successfully reached, then return the path
        if current.x == p2[0] and current.y == p2[1]:
            return retrace_steps(current)
        
        my_neighbors = neighbors(current, obstacles, N, M)
        for n in my_neighbors:
            # Visited neighbor
            if n in visited:
                p = visited[n]
                # Ignores CLOSED neighbors
                if p.state == 1:
                    continue
                
                # g_score using the current point as a stop
                offered_gscore = current.g_score + math.dist(n, (current.x, current.y))

                # Ignores larger g_score because it has a smaller g_score already
                if offered_gscore >= p.g_score:
                    continue

                # Updates this point since there is a better alternative
                p.g_score = offered_gscore
                p.f_score = p.g_score + math.dist(n, p2)
                p.parent = current

                # Reorganizes the openpoints heap because this point has a new f_score
                heapify(openpoints)

            # Brand new neighbor
            else:
                # Create a Point and put it into the heap
                g_score = math.dist((current.x, current.y), n)
                f_score = g_score + math.dist(n, p2)
                p = Point(n[0], n[1], f_score = f_score, g_score = g_score, parent = current)
                visited[(p.x, p.y)] = p
                heappush(openpoints, p)

    # Return empty list if no path is found
    return []

def get_path_to_obstacle(waypoint: tuple, obstacle: tuple, obstacles: set, N: int, M: int) -> list:
    path_to_obstacle = navigate(waypoint, obstacle, obstacles, N, M)
    if path_to_obstacle:
        return path_to_obstacle[:-1]  # Exclude the obstacle point itself
    return []

def find_path(waypoints: list, polygons: list, N: int, M: int):
    
    '''
    find_path calls navigate to get segments between the waypoints and then puts them together into one path.
    :param waypoints: Points that need to be visited
    :param polygons: Points of polygons that can not be visited
    :param N: height of the grid
    :param M: width of the grid
    :returns: A path to all the waypoints in order, including the obstacle points blocking the path, and a boolean indicating if the path is direct
    '''

    obstacles = polygons

    final_path = []

    for i in range(len(waypoints) - 1):
        # finds the path between the current and the next waypoint
        path_segment = navigate(waypoints[i], waypoints[i + 1], obstacles, N, M)

        if not path_segment:  # if no path is found
            obstacle_point = None
            min_distance = float('inf')
            for obstacle in obstacles:
                dist = math.dist(waypoints[i], obstacle) + math.dist(obstacle, waypoints[i + 1])
                if dist < min_distance:
                    min_distance = dist
                    obstacle_point = obstacle

            if obstacle_point:
                # Add the path to the obstacle and the obstacle point itself
                path_to_obstacle = get_path_to_obstacle(waypoints[i], obstacle_point, obstacles, N, M)
                final_path.extend(path_to_obstacle)
                final_path.append(obstacle_point)
            return final_path, False
        else:
            # Only includes the first point if it is from the first path segment;
            # it has been included in the previous path.
            if i == 0:
                final_path.extend(path_segment)
            else:
                final_path.extend(path_segment[1:])
    
    return final_path, True
'''
The code below used to make the grid was created by this stack overflow forem
https://stackoverflow.com/questions/33963361/how-to-make-a-grid-in-pygame
Other edits made to it are made by me.
'''

background = (10, 10, 40)
border = (30, 30, 60)
waypoint = (0, 255, 0)
obstacle = (255, 255, 255)
route = (143, 212, 242)
route_unavailable = (232, 66, 51)
width, height = 20, 20
margin = 1
last_key = "a"

grid = []
for row in range(40):
    grid.append([])
    for column in range(60):
        grid[row].append(0)

pygame.init()

WINDOW_SIZE = [1260, 840]
screen = pygame.display.set_mode(WINDOW_SIZE)

pygame.display.set_caption("'a' = waypoint, 's' = obstacle, 'd' = erase, 'f' = start, 'backspace' = clear, 'x' = end game")

done = False
clock = pygame.time.Clock()
last_grid_changed = 0, 0
draw = True
waypoints_grid = []

def draw(row: int, column: int, last_key):
    if last_key == "a":
        waypoints_grid.append((row, column))
        #print("Waypoint Added", waypoints)
        grid[row][column] = 1
    elif last_key == "d":
        if grid[row][column] == 1:
            waypoints_grid.remove((row, column))
            #print("Waypoint removed", waypoints)
        grid[row][column] = 0
    elif last_key == "s":
        if grid[row][column] == 1:
            waypoints_grid.remove((row, column))
            #print("Waypoint removed", waypoints)
        grid[row][column] = 2

def gui_to_obstacles():
    border = []
    for r in range(40):
        for c in range(60):
            if grid[r][c] == 2:
                border.append((r, c))
    return border
   
def main(waypoints):
    polygons = gui_to_obstacles()
    N, M = 40, 60
    return find_path(waypoints, polygons, N, M)

while not done:
    for event in pygame.event.get():
        if event.type == pygame.KEYDOWN:
            if event.type == pygame.QUIT:
                done = True

            if event.key == pygame.K_a:
                last_key = "a"
            elif event.key == pygame.K_s:
                last_key = "s"
            elif event.key == pygame.K_d:
                last_key = "d"
            elif event.key == pygame.K_f:
                if len(waypoints_grid) <= 1:
                    print("Can't do that, you need more than one waypoint!")
                else:
                    path = main(waypoints_grid)
                    if len(path) == 0:
                        print("Waypoints are too far apart")
                    else:
                        for i in path:
                            if i in waypoints_grid:
                                continue
                            elif grid[i[0]][i[1]] == 2:
                                grid[i[0]][i[1]] = 4
                                path_index = path.index(i)
                                while i not in waypoints_grid and path_index > 0:
                                    path_index -= 1
                                    i = path[path_index]
                                    grid[i[0]][i[1]] = 4
                                break
                            else:
                                grid[i[0]][i[1]] = 3
                                #print(i[0], i[1])
            elif event.key == pygame.K_BACKSPACE:
                for r in range(40):
                    for c in range(60):
                        grid[r][c] = 0
                waypoints_grid.clear()

            elif event.key == pygame.K_x:
                pygame.quit()
                print("Thanks for Playing!")

        elif pygame.mouse.get_pressed()[0]:
            pos = pygame.mouse.get_pos()
            column = pos[0] // (width + margin)
            row = pos[1] // (height + margin)

            if last_grid_changed[0] == 0 and last_grid_changed[1] == 0:
                last_grid_changed = row, column
            elif row == last_grid_changed[0] and column == last_grid_changed[1]:
                continue
            else:
                last_grid_changed = row, column

            draw(row, column, last_key)

    screen.fill(background)

    for row in range(40):
        for column in range(60):
            color = border
            if grid[row][column] == 1:
                color = waypoint
            elif grid[row][column] == 2:
                color = obstacle
            elif grid[row][column] == 3:
                color = route
            elif grid[row][column] == 4:
                color = route_unavailable
            pygame.draw.rect(screen, color, [(margin + width) * column + margin, (margin + height) * row + margin, width, height])
    clock.tick(60)

    pygame.display.flip()
pygame.quit()