from typing import Dict, List, Tuple


# Relief Centers Configuration
# Format: (center_id, name, supply_capacity)
RELIEF_CENTERS = [
    {
        'id': 0,
        'name': 'Mumbai Relief Center',
        'supply': 500,  # units
        'location': 'Mumbai, Maharashtra'
    },
    {
        'id': 1,
        'name': 'Delhi Relief Hub',
        'supply': 750,  # units
        'location': 'Delhi, NCR'
    },
    {
        'id': 2,
        'name': 'Bangalore Supply Base',
        'supply': 400,  # units
        'location': 'Bangalore, Karnataka'
    },
    {
        'id': 3,
        'name': 'Kolkata Distribution Center',
        'supply': 600,  # units
        'location': 'Kolkata, West Bengal'
    }
]


# Disaster Zones Configuration
# Format: (zone_id, name, demand, priority)
# Priority: 1 = Critical (highest), 2 = High, 3 = Medium, 4 = Low
DISASTER_ZONES = [
    {
        'id': 4,
        'name': 'Uttarakhand Flood Zone',
        'demand': 450,  # units
        'priority': 1,  # Critical
        'description': 'Severe flooding, immediate assistance required',
        'location': 'Uttarakhand'
    },
    {
        'id': 5,
        'name': 'Gujarat Earthquake Region',
        'demand': 600,  # units
        'priority': 1,  # Critical
        'description': 'Major earthquake damage, critical supplies needed',
        'location': 'Gujarat'
    },
    {
        'id': 6,
        'name': 'Kerala Landslide Area',
        'demand': 350,  # units
        'priority': 2,  # High
        'description': 'Multiple landslides, access partially blocked',
        'location': 'Kerala'
    },
    {
        'id': 7,
        'name': 'Odisha Cyclone Zone',
        'demand': 500,  # units
        'priority': 2,  # High
        'description': 'Cyclone aftermath, infrastructure damaged',
        'location': 'Odisha'
    },
    {
        'id': 8,
        'name': 'Rajasthan Drought Area',
        'demand': 300,  # units
        'priority': 3,  # Medium
        'description': 'Long-term drought, water and food supplies needed',
        'location': 'Rajasthan'
    }
]


# Graph Edges - Connections between all nodes
# Format: (node1, node2, distance_in_km)
# This represents the road network connecting relief centers and disaster zones
GRAPH_EDGES = [
    # Connections between Relief Centers (inter-center network)
    (0, 1, 1400),  # Mumbai - Delhi
    (0, 2, 850),   # Mumbai - Bangalore
    (0, 3, 1950),  # Mumbai - Kolkata
    (1, 2, 2150),  # Delhi - Bangalore
    (1, 3, 1450),  # Delhi - Kolkata
    (2, 3, 1880),  # Bangalore - Kolkata
    
    # Mumbai Relief Center to Disaster Zones
    (0, 4, 1650),  # Mumbai - Uttarakhand
    (0, 5, 530),   # Mumbai - Gujarat
    (0, 6, 1160),  # Mumbai - Kerala
    (0, 7, 1900),  # Mumbai - Odisha
    (0, 8, 1150),  # Mumbai - Rajasthan
    
    # Delhi Relief Hub to Disaster Zones
    (1, 4, 320),   # Delhi - Uttarakhand (nearest)
    (1, 5, 950),   # Delhi - Gujarat
    (1, 6, 2700),  # Delhi - Kerala
    (1, 7, 1760),  # Delhi - Odisha
    (1, 8, 570),   # Delhi - Rajasthan
    
    # Bangalore Supply Base to Disaster Zones
    (2, 4, 2450),  # Bangalore - Uttarakhand
    (2, 5, 1420),  # Bangalore - Gujarat
    (2, 6, 560),   # Bangalore - Kerala (nearest)
    (2, 7, 1870),  # Bangalore - Odisha
    (2, 8, 1750),  # Bangalore - Rajasthan
    
    # Kolkata Distribution Center to Disaster Zones
    (3, 4, 1570),  # Kolkata - Uttarakhand
    (3, 5, 2100),  # Kolkata - Gujarat
    (3, 6, 2050),  # Kolkata - Kerala
    (3, 7, 450),   # Kolkata - Odisha (nearest)
    (3, 8, 2020),  # Kolkata - Rajasthan
    
    # Connections between Disaster Zones (for realistic routing)
    (4, 5, 1370),  # Uttarakhand - Gujarat
    (4, 6, 2810),  # Uttarakhand - Kerala
    (4, 7, 1840),  # Uttarakhand - Odisha
    (4, 8, 750),   # Uttarakhand - Rajasthan
    (5, 6, 1880),  # Gujarat - Kerala
    (5, 7, 2200),  # Gujarat - Odisha
    (5, 8, 670),   # Gujarat - Rajasthan
    (6, 7, 1700),  # Kerala - Odisha
    (6, 8, 2300),  # Kerala - Rajasthan
    (7, 8, 2270),  # Odisha - Rajasthan
]


def get_total_nodes() -> int:
    """
    Get total number of nodes in the graph.
    
    Returns:
        Total number of relief centers + disaster zones
    """
    return len(RELIEF_CENTERS) + len(DISASTER_ZONES)


def get_relief_center_ids() -> List[int]:
    """
    Get list of all relief center node IDs.
    
    Returns:
        List of center IDs
    """
    return [center['id'] for center in RELIEF_CENTERS]


def get_disaster_zone_ids() -> List[int]:
    """
    Get list of all disaster zone node IDs.
    
    Returns:
        List of zone IDs
    """
    return [zone['id'] for zone in DISASTER_ZONES]


def get_node_name(node_id: int) -> str:
    """
    Get the name of a node by its ID.
    
    Args:
        node_id: Node identifier
    
    Returns:
        Name of the node
    """
    # Check relief centers
    for center in RELIEF_CENTERS:
        if center['id'] == node_id:
            return center['name']
    
    # Check disaster zones
    for zone in DISASTER_ZONES:
        if zone['id'] == node_id:
            return zone['name']
    
    return f"Unknown Node {node_id}"


def get_statistics() -> Dict:
    """
    Get summary statistics about the scenario.
    
    Returns:
        Dictionary containing scenario statistics
    """
    total_supply = sum(center['supply'] for center in RELIEF_CENTERS)
    total_demand = sum(zone['demand'] for zone in DISASTER_ZONES)
    
    return {
        'num_centers': len(RELIEF_CENTERS),
        'num_zones': len(DISASTER_ZONES),
        'total_supply': total_supply,
        'total_demand': total_demand,
        'supply_demand_ratio': total_supply / total_demand if total_demand > 0 else 0,
        'num_edges': len(GRAPH_EDGES),
        'is_supply_sufficient': total_supply >= total_demand
    }


def print_scenario_info():
    """Print detailed information about the disaster relief scenario."""
    print("=" * 80)
    print("DISASTER RELIEF DISTRIBUTION SCENARIO")
    print("=" * 80)
    
    print("\n📦 RELIEF CENTERS:")
    print("-" * 80)
    for center in RELIEF_CENTERS:
        print(f"  [{center['id']}] {center['name']}")
        print(f"      Location: {center['location']}")
        print(f"      Supply Capacity: {center['supply']} units")
        print()
    
    print("🚨 DISASTER ZONES:")
    print("-" * 80)
    priority_labels = {1: 'CRITICAL', 2: 'HIGH', 3: 'MEDIUM', 4: 'LOW'}
    for zone in DISASTER_ZONES:
        print(f"  [{zone['id']}] {zone['name']}")
        print(f"      Location: {zone['location']}")
        print(f"      Priority: {priority_labels.get(zone['priority'], 'UNKNOWN')}")
        print(f"      Demand: {zone['demand']} units")
        print(f"      Description: {zone['description']}")
        print()
    
    stats = get_statistics()
    print("📊 SCENARIO STATISTICS:")
    print("-" * 80)
    print(f"  Total Relief Centers: {stats['num_centers']}")
    print(f"  Total Disaster Zones: {stats['num_zones']}")
    print(f"  Total Supply Available: {stats['total_supply']} units")
    print(f"  Total Demand Required: {stats['total_demand']} units")
    print(f"  Supply/Demand Ratio: {stats['supply_demand_ratio']:.2f}")
    print(f"  Supply Sufficient: {'✓ Yes' if stats['is_supply_sufficient'] else '✗ No (Shortage Expected)'}")
    print(f"  Network Edges: {stats['num_edges']}")
    print("=" * 80)


if __name__ == "__main__":
    # Display scenario information
    print_scenario_info()
