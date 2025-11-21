import sys
from typing import Dict, List
from tabulate import tabulate

# Import project modules
from dijkstra import Graph, compute_all_shortest_paths
from greedy_allocation import ReliefCenter, DisasterZone, GreedyAllocator
from data import (
    RELIEF_CENTERS, DISASTER_ZONES, GRAPH_EDGES,
    get_total_nodes, get_relief_center_ids, get_disaster_zone_ids,
    get_node_name, print_scenario_info
)


def build_graph() -> Graph:
    """
    Build the graph from the data configuration.
    
    Returns:
        Graph object with all nodes and edges
    """
    total_nodes = get_total_nodes()
    graph = Graph(total_nodes)
    
    # Add all edges to the graph
    for source, destination, weight in GRAPH_EDGES:
        graph.add_edge(source, destination, weight)
    
    return graph


def display_distance_matrix(distances: Dict, centers: List[int], zones: List[int]):
    """
    Display shortest distances in a formatted table.
    
    Args:
        distances: Dictionary of shortest distances
        centers: List of relief center IDs
        zones: List of disaster zone IDs
    """
    print("\n" + "=" * 100)
    print("SHORTEST DISTANCES (using Dijkstra's Algorithm)")
    print("=" * 100)
    
    # Prepare table data
    headers = ["Relief Center"] + [get_node_name(z) for z in zones]
    table_data = []
    
    for center in centers:
        row = [get_node_name(center)]
        for zone in zones:
            distance = distances.get((center, zone), float('inf'))
            if distance == float('inf'):
                row.append("∞")
            else:
                row.append(f"{distance:.1f} km")
        table_data.append(row)
    
    print(tabulate(table_data, headers=headers, tablefmt="grid"))
    print()


def display_allocation_results(report: Dict):
    """
    Display allocation results in a formatted manner.
    
    Args:
        report: Report dictionary from GreedyAllocator
    """
    print("\n" + "=" * 100)
    print("ALLOCATION RESULTS")
    print("=" * 100)
    
    # Allocation Details Table
    if report['allocations']:
        print("\n📋 ALLOCATION DETAILS:")
        print("-" * 100)
        
        headers = ["Relief Center", "→", "Disaster Zone", "Supplies Sent", "Distance"]
        table_data = []
        
        for alloc in report['allocations']:
            table_data.append([
                alloc['center'],
                "→",
                alloc['zone'],
                f"{alloc['amount']:.2f} units",
                f"{alloc['distance']:.1f} km"
            ])
        
        print(tabulate(table_data, headers=headers, tablefmt="fancy_grid"))
    else:
        print("\n⚠️  No allocations made!")
    
    # Relief Center Summary
    print("\n\n📦 RELIEF CENTER SUMMARY:")
    print("-" * 100)
    
    headers = ["Center Name", "Initial Supply", "Allocated", "Remaining", "Utilization"]
    table_data = []
    
    for center in report['center_summary']:
        table_data.append([
            center['name'],
            f"{center['initial_supply']:.2f} units",
            f"{center['allocated']:.2f} units",
            f"{center['remaining']:.2f} units",
            f"{center['utilization']:.1f}%"
        ])
    
    print(tabulate(table_data, headers=headers, tablefmt="grid"))
    
    # Disaster Zone Summary
    print("\n\n🚨 DISASTER ZONE SUMMARY:")
    print("-" * 100)
    
    headers = ["Zone Name", "Priority", "Demand", "Received", "Shortage", "Fulfillment"]
    table_data = []
    
    priority_labels = {1: '🔴 Critical', 2: '🟠 High', 3: '🟡 Medium', 4: '🟢 Low'}
    
    for zone in report['zone_summary']:
        fulfillment_status = "✓" if zone['fulfillment'] >= 99.9 else "⚠"
        table_data.append([
            zone['name'],
            priority_labels.get(zone['priority'], f"P{zone['priority']}"),
            f"{zone['demand']:.2f} units",
            f"{zone['received']:.2f} units",
            f"{zone['shortage']:.2f} units",
            f"{fulfillment_status} {zone['fulfillment']:.1f}%"
        ])
    
    print(tabulate(table_data, headers=headers, tablefmt="grid"))


def display_summary_report(report: Dict):
    """
    Display final summary report with key statistics.
    
    Args:
        report: Report dictionary from GreedyAllocator
    """
    stats = report['statistics']
    
    print("\n\n" + "=" * 100)
    print("📊 FINAL SUMMARY REPORT")
    print("=" * 100)
    
    # Key Metrics
    print("\n🎯 KEY METRICS:")
    print("-" * 100)
    
    metrics = [
        ["Total Supply Available", f"{stats['total_supply']:.2f} units"],
        ["Total Demand Required", f"{stats['total_demand']:.2f} units"],
        ["Total Supplies Delivered", f"{stats['total_delivered']:.2f} units"],
        ["Total Distance Covered", f"{stats['total_distance']:.2f} km"],
        ["Overall Fulfillment Rate", f"{stats['fulfillment_rate']:.2f}%"],
        ["Distribution Efficiency", f"{stats['efficiency']:.4f} units/km"],
    ]
    
    print(tabulate(metrics, tablefmt="fancy_grid", colalign=("left", "right")))
    
    # Performance Analysis
    print("\n\n📈 PERFORMANCE ANALYSIS:")
    print("-" * 100)
    
    fulfillment_rate = stats['fulfillment_rate']
    
    if fulfillment_rate >= 100:
        performance = "✓ EXCELLENT - All demands fully met!"
        color = "🟢"
    elif fulfillment_rate >= 90:
        performance = "✓ GOOD - Most demands fulfilled"
        color = "🟡"
    elif fulfillment_rate >= 70:
        performance = "⚠ FAIR - Significant shortage exists"
        color = "🟠"
    else:
        performance = "✗ POOR - Critical shortage"
        color = "🔴"
    
    print(f"\n{color} Performance Rating: {performance}")
    print(f"   Fulfillment: {fulfillment_rate:.2f}%")
    
    # Calculate unmet demand
    unmet_demand = stats['total_demand'] - stats['total_delivered']
    if unmet_demand > 0.01:
        print(f"\n⚠️  WARNING: {unmet_demand:.2f} units of demand unmet!")
        print(f"   Recommendation: Arrange additional supplies or prioritize critical zones")
    else:
        print(f"\n✓ SUCCESS: All disaster zones received required supplies!")
    
    # Efficiency insights
    if stats['efficiency'] > 0:
        avg_distance = stats['total_distance'] / len(report['allocations']) if report['allocations'] else 0
        print(f"\n📍 Average delivery distance: {avg_distance:.2f} km")
        print(f"   Efficiency rating: {stats['efficiency']:.4f} units per km traveled")
    
    print("\n" + "=" * 100)


def display_time_complexity_analysis():
    """Display time complexity analysis of the algorithms used."""
    print("\n\n" + "=" * 100)
    print("⏱️  TIME COMPLEXITY ANALYSIS")
    print("=" * 100)
    
    analysis = [
        ["Algorithm", "Time Complexity", "Description"],
        ["-" * 40, "-" * 30, "-" * 60],
        ["Dijkstra's Algorithm\n(with Min-Heap)", "O((V + E) log V)", 
         "V = vertices, E = edges\nRun once for each relief center"],
        ["", "", ""],
        ["All Shortest Paths", "O(R × (V + E) log V)", 
         "R = number of relief centers\nComputes paths from all centers"],
        ["", "", ""],
        ["Greedy Allocation\n(Sorting)", "O(Z log Z)", 
         "Z = number of disaster zones\nSort zones by priority and demand"],
        ["", "", ""],
        ["Greedy Allocation\n(Assignment)", "O(Z × R)", 
         "For each zone, find nearest center\nUsually small constant iterations"],
        ["", "", ""],
        ["Overall Complexity", "O(R × (V + E) log V + Z log Z + Z × R)", 
         "Dominated by Dijkstra's algorithm\nHighly efficient for realistic scenarios"],
    ]
    
    for row in analysis:
        print(f"{row[0]:<42} {row[1]:<32} {row[2]}")
    
    print("\n💡 PRACTICAL PERFORMANCE:")
    print("-" * 100)
    print("For this scenario:")
    print(f"  • Vertices (V): {get_total_nodes()}")
    print(f"  • Edges (E): {len(GRAPH_EDGES)}")
    print(f"  • Relief Centers (R): {len(get_relief_center_ids())}")
    print(f"  • Disaster Zones (Z): {len(get_disaster_zone_ids())}")
    print(f"\n  ➜ Dijkstra runs: {len(get_relief_center_ids())} times")
    print(f"  ➜ Expected excellent performance even for much larger networks")
    print("=" * 100)


def main():
    """Main execution function."""
    print("\n")
    print("╔" + "=" * 98 + "╗")
    print("║" + " " * 98 + "║")
    print("║" + " OPTIMAL DISASTER RELIEF DISTRIBUTION SYSTEM ".center(98) + "║")
    print("║" + " Using Greedy Algorithms and Shortest Path Analysis ".center(98) + "║")
    print("║" + " " * 98 + "║")
    print("╚" + "=" * 98 + "╝")
    
    # Step 1: Display scenario information
    print_scenario_info()
    
    input("\nPress Enter to start computing shortest paths using Dijkstra's algorithm...")
    
    # Step 2: Build graph and compute shortest paths
    print("\n🔄 Building graph and computing shortest paths...")
    graph = build_graph()
    
    center_ids = get_relief_center_ids()
    zone_ids = get_disaster_zone_ids()
    
    # Compute all shortest paths using Dijkstra's algorithm
    shortest_distances = compute_all_shortest_paths(graph, center_ids, zone_ids)
    
    print("✓ Shortest paths computed successfully!")
    
    # Display distance matrix
    display_distance_matrix(shortest_distances, center_ids, zone_ids)
    
    input("Press Enter to start greedy resource allocation...")
    
    # Step 3: Create relief centers and disaster zones
    print("\n🔄 Initializing relief centers and disaster zones...")
    
    centers = [
        ReliefCenter(c['id'], c['name'], c['supply'])
        for c in RELIEF_CENTERS
    ]
    
    zones = [
        DisasterZone(z['id'], z['name'], z['demand'], z['priority'])
        for z in DISASTER_ZONES
    ]
    
    # Step 4: Run greedy allocation
    print("\n🔄 Executing greedy allocation algorithm...\n")
    allocator = GreedyAllocator(centers, zones, shortest_distances)
    report = allocator.allocate_resources()
    
    # Step 5: Display results
    display_allocation_results(report)
    
    # Step 6: Display summary report
    display_summary_report(report)
    
    # Step 7: Display complexity analysis
    display_time_complexity_analysis()
    
    # Step 8: Offer visualization
    print("\n\n" + "=" * 100)
    print("📊 VISUALIZATION")
    print("=" * 100)
    print("\nWould you like to see a graphical visualization of the network?")
    print("(Requires matplotlib and networkx)")
    
    response = input("\nGenerate visualization? (y/n): ").strip().lower()
    
    if response == 'y':
        try:
            from visualization import visualize_network
            print("\n🔄 Generating network visualization...")
            visualize_network(graph, center_ids, zone_ids, report['allocations'])
            print("✓ Visualization generated successfully!")
        except ImportError as e:
            print(f"\n⚠️  Could not generate visualization: {e}")
            print("   Install required packages: pip install matplotlib networkx")
        except Exception as e:
            print(f"\n⚠️  Error generating visualization: {e}")
    
    print("\n\n" + "=" * 100)
    print("✓ Simulation completed successfully!")
    print("=" * 100)
    print("\nThank you for using the Disaster Relief Distribution System!")
    print("Project: Design and Analysis of Algorithms\n")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Simulation interrupted by user.")
        sys.exit(0)
    except Exception as e:
        print(f"\n\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
