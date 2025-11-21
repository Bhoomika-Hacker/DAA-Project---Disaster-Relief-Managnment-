"""
Network Visualization Module
Author: Design and Analysis of Algorithms Project
Purpose: Visualize the relief distribution network using matplotlib and networkx

This module creates visual representations of:
1. Network topology (relief centers and disaster zones)
2. Shortest path connections
3. Allocation flows with color coding
"""

import matplotlib.pyplot as plt
import networkx as nx
from typing import List, Dict
from data import (
    RELIEF_CENTERS, DISASTER_ZONES, GRAPH_EDGES,
    get_node_name
)


def visualize_network(graph_obj, center_ids: List[int], zone_ids: List[int], 
                     allocations: List[Dict]):
    """
    Create a visual representation of the relief distribution network.
    
    Args:
        graph_obj: Graph object from dijkstra module
        center_ids: List of relief center node IDs
        zone_ids: List of disaster zone node IDs
        allocations: List of allocation dictionaries
    """
    # Create a NetworkX graph
    G = nx.Graph()
    
    # Add nodes
    for center in RELIEF_CENTERS:
        G.add_node(center['id'], 
                  name=center['name'],
                  node_type='center',
                  supply=center['supply'])
    
    for zone in DISASTER_ZONES:
        G.add_node(zone['id'],
                  name=zone['name'],
                  node_type='zone',
                  demand=zone['demand'],
                  priority=zone['priority'])
    
    # Add edges from graph data
    for source, dest, weight in GRAPH_EDGES:
        G.add_edge(source, dest, weight=weight)
    
    # Create allocation edges (for highlighting)
    allocation_edges = set()
    for alloc in allocations:
        allocation_edges.add((alloc['center_id'], alloc['zone_id']))
    
    # Set up the plot
    plt.figure(figsize=(16, 12))
    
    # Use spring layout for better visualization
    pos = nx.spring_layout(G, k=2, iterations=50, seed=42)
    
    # Draw different node types with different colors
    center_nodes = [n for n in G.nodes() if n in center_ids]
    zone_nodes = [n for n in G.nodes() if n in zone_ids]
    
    # Draw relief centers (blue, square)
    nx.draw_networkx_nodes(G, pos, nodelist=center_nodes,
                          node_color='#3498db',
                          node_shape='s',
                          node_size=2000,
                          label='Relief Centers')
    
    # Draw disaster zones with priority-based colors
    zone_colors = []
    for zone_id in zone_nodes:
        priority = G.nodes[zone_id]['priority']
        if priority == 1:
            zone_colors.append('#e74c3c')  # Red - Critical
        elif priority == 2:
            zone_colors.append('#e67e22')  # Orange - High
        elif priority == 3:
            zone_colors.append('#f39c12')  # Yellow - Medium
        else:
            zone_colors.append('#27ae60')  # Green - Low
    
    nx.draw_networkx_nodes(G, pos, nodelist=zone_nodes,
                          node_color=zone_colors,
                          node_shape='o',
                          node_size=1500,
                          label='Disaster Zones')
    
    # Draw all edges (thin, gray)
    all_edges = [e for e in G.edges() if e not in allocation_edges and 
                 (e[1], e[0]) not in allocation_edges]
    nx.draw_networkx_edges(G, pos, edgelist=all_edges,
                          width=0.5,
                          alpha=0.3,
                          edge_color='gray',
                          style='dashed')
    
    # Draw allocation edges (thick, green)
    active_allocation_edges = [(a['center_id'], a['zone_id']) for a in allocations]
    nx.draw_networkx_edges(G, pos, edgelist=active_allocation_edges,
                          width=3,
                          alpha=0.8,
                          edge_color='#27ae60',
                          style='solid')
    
    # Draw labels
    labels = {node: get_node_name(node).replace(' ', '\n') for node in G.nodes()}
    nx.draw_networkx_labels(G, pos, labels,
                           font_size=8,
                           font_weight='bold',
                           font_color='white')
    
    # Add title and legend
    plt.title('Disaster Relief Distribution Network\n' + 
              'Blue Squares = Relief Centers | Circles = Disaster Zones (by Priority)\n' +
              'Green Lines = Active Allocations | Gray Dashed = Available Routes',
              fontsize=14, fontweight='bold', pad=20)
    
    # Create custom legend
    from matplotlib.lines import Line2D
    legend_elements = [
        Line2D([0], [0], marker='s', color='w', markerfacecolor='#3498db', 
               markersize=12, label='Relief Centers'),
        Line2D([0], [0], marker='o', color='w', markerfacecolor='#e74c3c', 
               markersize=10, label='Critical Priority Zones'),
        Line2D([0], [0], marker='o', color='w', markerfacecolor='#e67e22', 
               markersize=10, label='High Priority Zones'),
        Line2D([0], [0], marker='o', color='w', markerfacecolor='#f39c12', 
               markersize=10, label='Medium Priority Zones'),
        Line2D([0], [0], color='#27ae60', linewidth=3, label='Active Allocations'),
        Line2D([0], [0], color='gray', linewidth=1, linestyle='--', 
               alpha=0.5, label='Available Routes')
    ]
    plt.legend(handles=legend_elements, loc='upper left', fontsize=10)
    
    plt.axis('off')
    plt.tight_layout()
    
    # Save the figure
    filename = 'relief_distribution_network.png'
    plt.savefig(filename, dpi=300, bbox_inches='tight', facecolor='white')
    print(f"   Visualization saved as '{filename}'")
    
    # Show the plot
    plt.show()


def visualize_allocation_flow(allocations: List[Dict]):
    """
    Create a bar chart showing allocation flow from centers to zones.
    
    Args:
        allocations: List of allocation dictionaries
    """
    if not allocations:
        print("No allocations to visualize.")
        return
    
    # Aggregate allocations by center
    center_allocations = {}
    for alloc in allocations:
        center = alloc['center']
        if center not in center_allocations:
            center_allocations[center] = 0
        center_allocations[center] += alloc['amount']
    
    # Create bar chart
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
    
    # Chart 1: Allocations by Center
    centers = list(center_allocations.keys())
    amounts = list(center_allocations.values())
    colors = ['#3498db', '#9b59b6', '#1abc9c', '#e67e22']
    
    ax1.barh(centers, amounts, color=colors[:len(centers)])
    ax1.set_xlabel('Supplies Allocated (units)', fontsize=12)
    ax1.set_title('Supplies Distributed by Relief Center', fontsize=14, fontweight='bold')
    ax1.grid(axis='x', alpha=0.3)
    
    # Chart 2: Allocations by Zone
    zone_allocations = {}
    for alloc in allocations:
        zone = alloc['zone']
        if zone not in zone_allocations:
            zone_allocations[zone] = 0
        zone_allocations[zone] += alloc['amount']
    
    zones = list(zone_allocations.keys())
    zone_amounts = list(zone_allocations.values())
    priority_colors = ['#e74c3c', '#e67e22', '#f39c12', '#27ae60', '#95a5a6']
    
    ax2.barh(zones, zone_amounts, color=priority_colors[:len(zones)])
    ax2.set_xlabel('Supplies Received (units)', fontsize=12)
    ax2.set_title('Supplies Received by Disaster Zone', fontsize=14, fontweight='bold')
    ax2.grid(axis='x', alpha=0.3)
    
    plt.tight_layout()
    
    # Save the figure
    filename = 'allocation_flow.png'
    plt.savefig(filename, dpi=300, bbox_inches='tight', facecolor='white')
    print(f"   Allocation flow chart saved as '{filename}'")
    
    plt.show()


def visualize_distance_vs_allocation(allocations: List[Dict]):
    """
    Create a scatter plot showing relationship between distance and allocation.
    
    Args:
        allocations: List of allocation dictionaries
    """
    if not allocations:
        print("No allocations to visualize.")
        return
    
    distances = [alloc['distance'] for alloc in allocations]
    amounts = [alloc['amount'] for alloc in allocations]
    centers = [alloc['center'] for alloc in allocations]
    
    # Create scatter plot
    plt.figure(figsize=(10, 6))
    
    # Color code by center
    unique_centers = list(set(centers))
    colors_map = {'Mumbai Relief Center': '#3498db', 
                  'Delhi Relief Hub': '#9b59b6',
                  'Bangalore Supply Base': '#1abc9c',
                  'Kolkata Distribution Center': '#e67e22'}
    
    for center in unique_centers:
        center_distances = [d for d, c in zip(distances, centers) if c == center]
        center_amounts = [a for a, c in zip(amounts, centers) if c == center]
        plt.scatter(center_distances, center_amounts, 
                   label=center, 
                   color=colors_map.get(center, '#95a5a6'),
                   s=150, alpha=0.7, edgecolors='black', linewidth=1.5)
    
    plt.xlabel('Distance (km)', fontsize=12)
    plt.ylabel('Supplies Allocated (units)', fontsize=12)
    plt.title('Supply Allocation vs. Distance\nGreedy Algorithm Prefers Nearby Centers', 
             fontsize=14, fontweight='bold')
    plt.legend(loc='best', fontsize=10)
    plt.grid(True, alpha=0.3)
    
    # Save the figure
    filename = 'distance_vs_allocation.png'
    plt.savefig(filename, dpi=300, bbox_inches='tight', facecolor='white')
    print(f"   Distance vs. allocation chart saved as '{filename}'")
    
    plt.show()


if __name__ == "__main__":
    print("This module is meant to be imported and used by main.py")
    print("Run: python main.py")
