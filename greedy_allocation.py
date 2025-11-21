from typing import List, Dict, Tuple


class ReliefCenter:
    """Represents a relief center with available supplies."""
    
    def __init__(self, center_id: int, name: str, supply: float):
        """
        Initialize a relief center.
        
        Args:
            center_id: Unique identifier
            name: Name of the center
            supply: Available supplies (in units)
        """
        self.center_id = center_id
        self.name = name
        self.initial_supply = supply
        self.remaining_supply = supply
        self.allocations = []  # List of (zone, amount, distance)
    
    def allocate(self, zone_id: int, zone_name: str, amount: float, distance: float):
        """
        Allocate supplies to a disaster zone.
        
        Args:
            zone_id: ID of the disaster zone
            zone_name: Name of the disaster zone
            amount: Amount to allocate
            distance: Distance to the zone
        """
        self.remaining_supply -= amount
        self.allocations.append({
            'zone_id': zone_id,
            'zone_name': zone_name,
            'amount': amount,
            'distance': distance
        })
    
    def __str__(self):
        return f"{self.name} (ID: {self.center_id}, Supply: {self.initial_supply})"


class DisasterZone:
    """Represents a disaster zone with demand and priority."""
    
    def __init__(self, zone_id: int, name: str, demand: float, priority: int):
        """
        Initialize a disaster zone.
        
        Args:
            zone_id: Unique identifier
            name: Name of the zone
            demand: Required supplies (in units)
            priority: Priority level (1=highest, higher number=lower priority)
        """
        self.zone_id = zone_id
        self.name = name
        self.initial_demand = demand
        self.remaining_demand = demand
        self.priority = priority
        self.allocations = []  # List of (center, amount, distance)
    
    def receive(self, center_id: int, center_name: str, amount: float, distance: float):
        """
        Receive supplies from a relief center.
        
        Args:
            center_id: ID of the relief center
            center_name: Name of the relief center
            amount: Amount received
            distance: Distance from the center
        """
        self.remaining_demand -= amount
        self.allocations.append({
            'center_id': center_id,
            'center_name': center_name,
            'amount': amount,
            'distance': distance
        })
    
    def is_fulfilled(self) -> bool:
        """Check if demand is fully met."""
        return self.remaining_demand <= 0.001  # Small epsilon for floating point
    
    def __str__(self):
        return f"{self.name} (ID: {self.zone_id}, Demand: {self.initial_demand}, Priority: {self.priority})"


class GreedyAllocator:
    """
    Greedy algorithm for allocating relief supplies.
    
    Strategy:
    1. Sort disaster zones by priority (highest priority first)
    2. For each zone, allocate from the nearest available center
    3. Continue until all demands are met or supplies exhausted
    """
    
    def __init__(self, centers: List[ReliefCenter], zones: List[DisasterZone],
                 distances: Dict[Tuple[int, int], float]):
        """
        Initialize the allocator.
        
        Args:
            centers: List of relief centers
            zones: List of disaster zones
            distances: Dictionary mapping (center_id, zone_id) to distance
        """
        self.centers = {c.center_id: c for c in centers}
        self.zones = {z.zone_id: z for z in zones}
        self.distances = distances
        self.total_distance_covered = 0
        self.total_supplies_delivered = 0
    
    def allocate_resources(self) -> Dict:
        """
        Execute the greedy allocation algorithm.
        
        Algorithm Steps:
        1. Sort zones by priority (highest first), then by demand (highest first)
        2. For each zone in sorted order:
           a. While zone has remaining demand:
              - Find nearest center with available supply
              - Allocate as much as possible from that center
              - Update supplies and demands
        
        Time Complexity: O(Z log Z + Z * R * A)
        where Z = zones, R = centers, A = allocations per zone (usually small)
        
        Returns:
            Dictionary containing allocation results and statistics
        """
        # Step 1: Sort zones by priority (ascending), then by demand (descending)
        # Time Complexity: O(Z log Z)
        sorted_zones = sorted(
            self.zones.values(),
            key=lambda z: (z.priority, -z.initial_demand)
        )
        
        print("Allocation Order (by priority and demand):")
        print("-" * 50)
        for i, zone in enumerate(sorted_zones, 1):
            print(f"{i}. {zone.name} - Priority: {zone.priority}, Demand: {zone.initial_demand}")
        print()
        
        # Step 2: Allocate resources to each zone
        # Time Complexity: O(Z * R) for finding nearest center for each zone
        for zone in sorted_zones:
            while zone.remaining_demand > 0.001:  # Small epsilon for floating point
                # Find nearest center with available supply
                nearest_center = self._find_nearest_available_center(zone.zone_id)
                
                if nearest_center is None:
                    # No more supplies available
                    print(f"⚠️  Warning: Cannot fully fulfill {zone.name} "
                          f"(shortage: {zone.remaining_demand:.2f} units)")
                    break
                
                # Calculate allocation amount
                amount = min(
                    zone.remaining_demand,
                    nearest_center.remaining_supply
                )
                
                # Get distance
                distance = self.distances[(nearest_center.center_id, zone.zone_id)]
                
                # Perform allocation
                nearest_center.allocate(zone.zone_id, zone.name, amount, distance)
                zone.receive(nearest_center.center_id, nearest_center.name, amount, distance)
                
                # Update statistics
                self.total_supplies_delivered += amount
                self.total_distance_covered += distance
                
                print(f"✓ Allocated {amount:.2f} units from {nearest_center.name} "
                      f"to {zone.name} (distance: {distance:.2f} km)")
        
        return self._generate_report()
    
    def _find_nearest_available_center(self, zone_id: int) -> ReliefCenter:
        """
        Find the nearest relief center with available supply.
        
        Time Complexity: O(R) where R = number of centers
        
        Args:
            zone_id: ID of the disaster zone
        
        Returns:
            Nearest center with supply, or None if no supply available
        """
        nearest_center = None
        min_distance = float('inf')
        
        for center in self.centers.values():
            if center.remaining_supply > 0.001:  # Has supply available
                distance = self.distances[(center.center_id, zone_id)]
                if distance < min_distance:
                    min_distance = distance
                    nearest_center = center
        
        return nearest_center
    
    def _generate_report(self) -> Dict:
        """
        Generate a comprehensive allocation report.
        
        Returns:
            Dictionary containing all allocation details and statistics
        """
        report = {
            'allocations': [],
            'center_summary': [],
            'zone_summary': [],
            'statistics': {
                'total_distance': self.total_distance_covered,
                'total_delivered': self.total_supplies_delivered,
                'total_demand': sum(z.initial_demand for z in self.zones.values()),
                'total_supply': sum(c.initial_supply for c in self.centers.values()),
                'fulfillment_rate': 0,
                'efficiency': 0
            }
        }
        
        # Allocation details
        for zone in self.zones.values():
            for alloc in zone.allocations:
                report['allocations'].append({
                    'center': alloc['center_name'],
                    'center_id': alloc['center_id'],
                    'zone': zone.name,
                    'zone_id': zone.zone_id,
                    'amount': alloc['amount'],
                    'distance': alloc['distance']
                })
        
        # Center summary
        for center in self.centers.values():
            total_allocated = center.initial_supply - center.remaining_supply
            report['center_summary'].append({
                'name': center.name,
                'id': center.center_id,
                'initial_supply': center.initial_supply,
                'allocated': total_allocated,
                'remaining': center.remaining_supply,
                'utilization': (total_allocated / center.initial_supply * 100) if center.initial_supply > 0 else 0
            })
        
        # Zone summary
        for zone in self.zones.values():
            total_received = zone.initial_demand - zone.remaining_demand
            report['zone_summary'].append({
                'name': zone.name,
                'id': zone.zone_id,
                'priority': zone.priority,
                'demand': zone.initial_demand,
                'received': total_received,
                'shortage': zone.remaining_demand,
                'fulfillment': (total_received / zone.initial_demand * 100) if zone.initial_demand > 0 else 0
            })
        
        # Calculate statistics
        total_demand = report['statistics']['total_demand']
        if total_demand > 0:
            report['statistics']['fulfillment_rate'] = \
                (self.total_supplies_delivered / total_demand) * 100
        
        # Efficiency: supplies delivered per km (higher is better)
        if self.total_distance_covered > 0:
            report['statistics']['efficiency'] = \
                self.total_supplies_delivered / self.total_distance_covered
        
        return report


if __name__ == "__main__":
    # Test the greedy allocation algorithm
    print("Testing Greedy Allocation Algorithm")
    print("=" * 50)
    
    # Create sample data
    centers = [
        ReliefCenter(0, "Center A", 100),
        ReliefCenter(1, "Center B", 150)
    ]
    
    zones = [
        DisasterZone(2, "Zone 1", 80, priority=1),
        DisasterZone(3, "Zone 2", 120, priority=2)
    ]
    
    # Sample distances
    distances = {
        (0, 2): 10,  # Center A to Zone 1
        (0, 3): 25,  # Center A to Zone 2
        (1, 2): 15,  # Center B to Zone 1
        (1, 3): 8    # Center B to Zone 2
    }
    
    allocator = GreedyAllocator(centers, zones, distances)
    report = allocator.allocate_resources()
    
    print("\nAllocation Summary:")
    print(f"Total Delivered: {report['statistics']['total_delivered']:.2f}")
    print(f"Total Distance: {report['statistics']['total_distance']:.2f} km")
    print(f"Fulfillment Rate: {report['statistics']['fulfillment_rate']:.2f}%")
