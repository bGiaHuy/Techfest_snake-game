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
            # Check if this position collides with the snake's body.
            # Note: We exclude the tail segment as an obstacle since it will move out of the way,
            # unless the snake is about to eat food and grow.
            # To be safe, we treat all body segments except the head as obstacles.
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
    
    # We treat the body of the snake as obstacles
    body_set = set(snake_body[:-1])  # Exclude tail since it moves, but keep the rest
    
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

def get_survival_move(start, snake_body):
    """
    Fallback mechanism when no path to the food exists.
    Evaluates all adjacent safe cells and selects the one that leads to the
    largest amount of reachable open space (using flood fill).
    Returns:
        Next direction as a (dx, dy) tuple, or None if no move is safe.
    """
    valid_neighbors = get_valid_neighbors(start, snake_body)
    if not valid_neighbors:
        return None  # No safe moves (Game Over)
        
    best_neighbor = None
    max_reachable = -1
    
    for neighbor in valid_neighbors:
        # Simulate moving to this neighbor and count space
        # We can pass the updated snake body to make flood fill more accurate,
        # but just standard snake_body is sufficient.
        space = count_reachable_cells(neighbor, snake_body)
        if space > max_reachable:
            max_reachable = space
            best_neighbor = neighbor
            
    if best_neighbor:
        # Convert absolute coordinates back to a direction offset
        dx = best_neighbor[0] - start[0]
        dy = best_neighbor[1] - start[1]
        return (dx, dy)
        
    return None
