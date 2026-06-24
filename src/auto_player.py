from collections import deque
from src.config import GRID_COLS, GRID_ROWS

def get_valid_neighbors(pos, snake_body):
    """
    Returns a list of valid, unblocked grid positions adjacent to the given position.
    """
    x, y = pos
    neighbors = []
    # Up, Down, Left, Right
    directions = [(0, -1), (0, 1), (-1, 0), (1, 0)]
    
    for dx, dy in directions:
        nx, ny = x + dx, y + dy
        if 0 <= nx < GRID_COLS and 0 <= ny < GRID_ROWS:
            # Exclude body segments as obstacles. The tail segment moves out of the way
            # unless the snake grows, so we exclude snake_body[-1] when it's not eating.
            # To be safe, we treat all body segments except the last one as obstacles.
            if (nx, ny) not in snake_body[:-1]:
                neighbors.append((nx, ny))
                
    return neighbors

def find_shortest_path(start, target, snake_body):
    """
    Runs a Breadth-First Search (BFS) to find the shortest path from start to target.
    Returns:
        List of (x, y) coordinates from start to target (inclusive), or None if no path exists.
    """
    if start == target:
        return [start]
        
    queue = deque([[start]])
    visited = {start}
    
    # Treat body segments as obstacles, excluding the tail segment since it will move
    body_set = set(snake_body[:-1])
    
    while queue:
        path = queue.popleft()
        current = path[-1]
        
        if current == target:
            return path
            
        for dx, dy in [(0, -1), (0, 1), (-1, 0), (1, 0)]:
            neighbor = (current[0] + dx, current[1] + dy)
            
            if 0 <= neighbor[0] < GRID_COLS and 0 <= neighbor[1] < GRID_ROWS:
                if neighbor not in visited and neighbor not in body_set:
                    visited.add(neighbor)
                    new_path = list(path)
                    new_path.append(neighbor)
                    queue.append(new_path)
                    
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
        # Only pop if we are not at the final step (eating the food)
        if step != path_to_food[-1]:
            virtual_body.pop()
            
    # Check if there is a path from the new head to the new tail in the simulated state
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
        # Simulate moving to this neighbor (since it is not food, tail moves)
        virtual_body = [neighbor] + snake_body[:-1]
        
        # Check if the neighbor can reach the tail
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
            
    # 2. If no safe path to food, follow the tail defensively
    tail_move = follow_tail_move(head, snake_body)
    if tail_move:
        path_to_tail = find_shortest_path(head, snake_body[-1], snake_body)
        return tail_move, (path_to_tail if path_to_tail else [])
        
    # 3. Fallback: survive by picking the direction with the most space
    survival_move = get_survival_move(head, snake_body)
    if survival_move:
        return survival_move, []
        
    # 4. No safe move (r.i.p)
    return (0, 0), []

