import heapq
from typing import List, Dict, Tuple


class Graph:
    """
    Graph class to represent the network of relief centers and disaster zones.
    Uses adjacency list representation for efficient storage and traversal.
    """
    
    def __init__(self, num_nodes: int):
        """
        Initialize graph with given number of nodes.
        
        Args:
            num_nodes: Total number of nodes (relief centers + disaster zones)
        """
        self.num_nodes = num_nodes
        self.adjacency_list = {i: [] for i in range(num_nodes)}
    
    def add_edge(self, source: int, destination: int, weight: float):
        """
        Add a bidirectional edge between two nodes.
        
        Args:
            source: Starting node
            destination: Ending node
            weight: Distance/cost between nodes
        """
        # Bidirectional graph (can travel both ways)
        self.adjacency_list[source].append((destination, weight))
        self.adjacency_list[destination].append((source, weight))
    
    def dijkstra(self, start_node: int) -> Tuple[Dict[int, float], Dict[int, int]]:
        """
        Dijkstra's algorithm to find shortest paths from start_node to all other nodes.
        
        Algorithm Steps:
        1. Initialize all distances to infinity except start node (distance = 0)
        2. Use a min-heap priority queue to always process the nearest unvisited node
        3. For each node, update distances to its neighbors if a shorter path is found
        4. Continue until all reachable nodes are processed
        
        Time Complexity: O((V + E) log V) with min-heap
        - Each vertex is inserted and extracted once: O(V log V)
        - Each edge is relaxed once: O(E log V)
        
        Args:
            start_node: The node to start from (relief center)
        
        Returns:
            distances: Dictionary mapping node_id to shortest distance from start_node
            previous: Dictionary mapping node_id to previous node in shortest path
        """
        # Initialize distances to infinity
        distances = {i: float('inf') for i in range(self.num_nodes)}
        distances[start_node] = 0
        
        # Track previous node in shortest path (for path reconstruction)
        previous = {i: None for i in range(self.num_nodes)}
        
        # Priority queue: (distance, node)
        # Min-heap ensures we always process the nearest unvisited node
        priority_queue = [(0, start_node)]
        
        # Set to track visited nodes
        visited = set()
        
        while priority_queue:
            # Extract node with minimum distance
            # Time Complexity: O(log V) for heap extraction
            current_distance, current_node = heapq.heappop(priority_queue)
            
            # Skip if already visited (optimization)
            if current_node in visited:
                continue
            
            visited.add(current_node)
            
            # If current distance is greater than recorded, skip
            if current_distance > distances[current_node]:
                continue
            
            # Explore neighbors
            for neighbor, weight in self.adjacency_list[current_node]:
                distance = current_distance + weight
                
                # Relaxation step: Update if shorter path found
                if distance < distances[neighbor]:
                    distances[neighbor] = distance
                    previous[neighbor] = current_node
                    # Time Complexity: O(log V) for heap insertion
                    heapq.heappush(priority_queue, (distance, neighbor))
        
        return distances, previous
    
    def get_shortest_path(self, start: int, end: int, previous: Dict[int, int]) -> List[int]:
        """
        Reconstruct the shortest path from start to end using previous nodes.
        
        Time Complexity: O(V) in worst case (path length)
        
        Args:
            start: Starting node
            end: Ending node
            previous: Dictionary from dijkstra algorithm
        
        Returns:
            List of nodes representing the shortest path
        """
        path = []
        current = end
        
        # Backtrack from end to start
        while current is not None:
            path.append(current)
            current = previous[current]
        
        # Reverse to get path from start to end
        path.reverse()
        
        # Return path only if it starts from the correct start node
        if path and path[0] == start:
            return path
        else:
            return []  # No path exists


def compute_all_shortest_paths(graph: Graph, relief_centers: List[int], 
                               disaster_zones: List[int]) -> Dict[Tuple[int, int], float]:
    """
    Compute shortest distances from all relief centers to all disaster zones.
    
    Time Complexity: O(R * (V + E) log V)
    where R = number of relief centers
    
    Args:
        graph: The graph representing the network
        relief_centers: List of relief center node IDs
        disaster_zones: List of disaster zone node IDs
    
    Returns:
        Dictionary mapping (center_id, zone_id) to shortest distance
    """
    shortest_distances = {}
    
    # Run Dijkstra from each relief center
    for center in relief_centers:
        distances, _ = graph.dijkstra(center)
        
        # Store distances to each disaster zone
        for zone in disaster_zones:
            shortest_distances[(center, zone)] = distances[zone]
    
    return shortest_distances


if __name__ == "__main__":
    # Test the Dijkstra implementation
    print("Testing Dijkstra's Algorithm")
    print("=" * 50)
    
    # Create a simple test graph
    g = Graph(5)
    g.add_edge(0, 1, 10)
    g.add_edge(0, 2, 5)
    g.add_edge(1, 2, 2)
    g.add_edge(1, 3, 1)
    g.add_edge(2, 3, 9)
    g.add_edge(3, 4, 4)
    
    # Run Dijkstra from node 0
    distances, previous = g.dijkstra(0)
    
    print("Shortest distances from node 0:")
    for node, dist in distances.items():
        print(f"  Node {node}: {dist}")
    
    print("\nShortest path from 0 to 4:")
    path = g.get_shortest_path(0, 4, previous)
    print(f"  Path: {' -> '.join(map(str, path))}")
    print(f"  Distance: {distances[4]}")
