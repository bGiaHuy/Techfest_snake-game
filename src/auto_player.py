import heapq
import itertools
from collections import deque
from src.config import GRID_COLS, GRID_ROWS

# Generate a fixed Hamiltonian Cycle for the 28x28 grid
def _generate_hamiltonian_cycle(cols, rows):
    cycle = []
    # Go down Column 0
    for y in range(rows):
        cycle.append((0, y))
        
    # Serpentine for columns 1 to cols-1
    for x in range(1, cols):
        if x % 2 == 1:
            # Odd columns go UP (from rows-1 down to 1)
            for y in reversed(range(1, rows)):
                cycle.append((x, y))
        else:
            # Even columns go DOWN (from 1 up to rows-1)
            for y in range(1, rows):
                cycle.append((x, y))
                
    # Go left along row 0 back to (0,0)
    for x in reversed(range(1, cols)):
        cycle.append((x, 0))
        
    return cycle

HAMILTONIAN_CYCLE = _generate_hamiltonian_cycle(GRID_COLS, GRID_ROWS)
# Map pos -> index in cycle
CYCLE_INDEX = {pos: idx for idx, pos in enumerate(HAMILTONIAN_CYCLE)}
V_SIZE = len(HAMILTONIAN_CYCLE)

def get_valid_neighbors(pos, snake_body):
    """
    Returns a list of valid, unblocked grid positions adjacent to the given position.
    """
    x, y = pos
    neighbors = []
    directions = [(0, -1), (0, 1), (-1, 0), (1, 0)]
    
    for dx, dy in directions:
        nx, ny = x + dx, y + dy
        if 0 <= nx < GRID_COLS and 0 <= ny < GRID_ROWS:
            if (nx, ny) not in snake_body[:-1]:
                neighbors.append((nx, ny))
                
    return neighbors

def heuristic(a, b):
    # Manhattan distance heuristic
    return abs(a[0] - b[0]) + abs(a[1] - b[1])

def find_shortest_path(start, target, snake_body):
    """
    Runs A* (A-Star) search to find the shortest path from start to target.
    Returns:
        List of (x, y) coordinates from start to target (inclusive), or None if no path exists.
    """
    if start == target:
        return [start]
        
    # Priority queue stores tuples of (f_score, counter, current_node)
    counter = itertools.count()
    queue = []
    heapq.heappush(queue, (0, next(counter), start))
    
    came_from = {}
    g_score = {start: 0}
    body_set = set(snake_body[:-1])
    
    while queue:
        _, _, current = heapq.heappop(queue)
        
        if current == target:
            path = [current]
            while current in came_from:
                current = came_from[current]
                path.append(current)
            path.reverse()
            return path
            
        for dx, dy in [(0, -1), (0, 1), (-1, 0), (1, 0)]:
            neighbor = (current[0] + dx, current[1] + dy)
            
            if 0 <= neighbor[0] < GRID_COLS and 0 <= neighbor[1] < GRID_ROWS:
                if neighbor not in body_set:
                    tentative_g_score = g_score[current] + 1
                    if neighbor not in g_score or tentative_g_score < g_score[neighbor]:
                        came_from[neighbor] = current
                        g_score[neighbor] = tentative_g_score
                        f_score = tentative_g_score + heuristic(neighbor, target)
                        heapq.heappush(queue, (f_score, next(counter), neighbor))
                        
    return None

def count_reachable_cells(start, snake_body):
    """
    Performs a flood fill (BFS) from start to count the number of reachable cells.
    Used as a survival heuristic to choose the direction with the most open space.
    """
    queue = deque([start])
    visited = {start}
    body_set = set(snake_body[:-1])
    count = 0
    
    while queue:
        current = queue.popleft()
        count += 1
        
        for dx, dy in [(0, -1), (0, 1), (-1, 0), (1, 0)]:
            neighbor = (current[0] + dx, current[1] + dy)
            if 0 <= neighbor[0] < GRID_COLS and 0 <= neighbor[1] < GRID_ROWS:
                if neighbor not in visited and neighbor not in body_set:
                    visited.add(neighbor)
                    queue.append(neighbor)
                    
    return count

def is_path_safe(snake_body, path_to_food):
    """
    Checks if following the path_to_food preserves a path to the tail.
    This prevents the AI from taking short-term shortcuts that lead to dead ends.
    """
    virtual_body = list(snake_body)
    for step in path_to_food[1:]:
        virtual_body.insert(0, step)
        if step != path_to_food[-1]:
            virtual_body.pop()
            
    tail_path = find_shortest_path(virtual_body[0], virtual_body[-1], virtual_body)
    return tail_path is not None

def follow_tail_move(head, snake_body):
    """
    Finds a step that moves toward the tail while keeping a path to the tail open.
    This is used as a defensive wandering state.
    """
    valid_neighbors = get_valid_neighbors(head, snake_body)
    if not valid_neighbors:
        return None
        
    best_move = None
    max_space = -1
    
    for neighbor in valid_neighbors:
        virtual_body = [neighbor] + snake_body[:-1]
        path_to_tail = find_shortest_path(neighbor, virtual_body[-1], virtual_body)
        if path_to_tail is not None:
            space = count_reachable_cells(neighbor, virtual_body)
            if space > max_space:
                max_space = space
                best_move = neighbor
                
    if best_move:
        dx = best_move[0] - head[0]
        dy = best_move[1] - head[1]
        return (dx, dy)
        
    return None

def get_survival_move(start, snake_body):
    """
    Fallback mechanism when no path to the food exists.
    Evaluates all adjacent safe cells and selects the one that leads to the
    largest amount of reachable open space (using flood fill).
    """
    valid_neighbors = get_valid_neighbors(start, snake_body)
    if not valid_neighbors:
        return None
        
    best_neighbor = None
    max_reachable = -1
    
    for neighbor in valid_neighbors:
        space = count_reachable_cells(neighbor, snake_body)
        if space > max_reachable:
            max_reachable = space
            best_neighbor = neighbor
            
    if best_neighbor:
        dx = best_neighbor[0] - start[0]
        dy = best_neighbor[1] - start[1]
        return (dx, dy)
        
    return None

def get_ai_move(head, food_pos, snake_body):
    """
    Main AI Solver entrypoint.
    Decides the best next move and returns the planned path for visualization.
    Returns:
        tuple: ((dx, dy), planned_path)
    """
    # 1. Try to find a path to the food
    path_to_food = find_shortest_path(head, food_pos, snake_body)
    
    if path_to_food and len(path_to_food) > 1:
        # Verify if it's safe (can reach its own tail after eating)
        if is_path_safe(snake_body, path_to_food):
            next_cell = path_to_food[1]
            dx = next_cell[0] - head[0]
            dy = next_cell[1] - head[1]
            return (dx, dy), path_to_food
            
    # 2. Fallback 1: Follow the Hamiltonian Cycle
    if head in CYCLE_INDEX:
        h_idx = CYCLE_INDEX[head]
        next_cell = HAMILTONIAN_CYCLE[(h_idx + 1) % V_SIZE]
        
        # Verify that the next cell along the cycle is safe and is adjacent
        if next_cell not in snake_body[:-1]:
            dx = next_cell[0] - head[0]
            dy = next_cell[1] - head[1]
            
            # Trace the cycle path from head to food for drawing (max 50 cells)
            f_idx = CYCLE_INDEX.get(food_pos, 0)
            path_cycle = []
            curr_idx = h_idx
            for _ in range(min(50, (f_idx - curr_idx) % V_SIZE + 1)):
                path_cycle.append(HAMILTONIAN_CYCLE[curr_idx])
                curr_idx = (curr_idx + 1) % V_SIZE
            return (dx, dy), path_cycle
            
    # 3. Fallback 2: Follow the tail defensively
    tail_move = follow_tail_move(head, snake_body)
    if tail_move:
        path_to_tail = find_shortest_path(head, snake_body[-1], snake_body)
        return tail_move, (path_to_tail if path_to_tail else [])
        
    # 4. Fallback 3: survive by picking the direction with the most space
    survival_move = get_survival_move(head, snake_body)
    if survival_move:
        return survival_move, []
        
    # 5. No safe move (r.i.p)
    return (0, 0), []


