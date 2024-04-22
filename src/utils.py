# encoding: utf-8
"""
Utility functions for the game.
"""

import json
import matplotlib.pyplot as plt

def load_game_config(file_path):
    """
    Load game configuration from a json file.

    Parameters:
    file_path (str): The path to the json file.

    Returns:
    dict: The loaded game configuration data.
    """
    with open(file_path, 'r', encoding='utf-8') as file:
        data = json.load(file)
    return data


def make_edges_bidirectional(edges):
    """
    Makes the edges of a graph bidirectional by adding reverse connections.

    Args:
        edges (list): A list of tuples representing the edges of the graph.
                      Each tuple contains a start node and a list of connections.

    Returns:
        list: A list of tuples representing the bidirectional edges of the graph.
              Each tuple contains a start node and a list of connections.

    Example:
        edges = [('A', ['B']), ('B', ['C']), ('C', ['D'])]
        bidirectional_edges = make_edges_bidirectional(edges)
        print(bidirectional_edges)
        # Output: [('A', ['B']), ('B', ['C']), ('C', ['D']), ('B', ['A']), ('C', ['B']), ('D', ['C'])]
    """
    bidirectional_edges = []
    for start, connections in edges:
        for end in connections:
            if (end, [start]) not in edges and (end, start) not in bidirectional_edges:
                bidirectional_edges.append((end, [start]))
    edges.extend(bidirectional_edges)
    return edges

def validate_nodes(valid_nodes):
    """
    Validates the given nodes to ensure they are within the valid range.

    Args:
        valid_nodes (list): A list of nodes to be validated. Each node is represented as a tuple of (x, y) coordinates.

    Raises:
        ValueError: If any of the nodes are outside the valid range.

    Returns:
        bool: True if all nodes are within the valid range.

    """
    for node in valid_nodes:
        if not (0 <= node[0] < 21) or not (0 <= node[1] < 21):
            raise ValueError(f"Node out of valid range: {node}")
    return True


# Function to plot nodes and edges
def plot_board(nodes, edges, tiger_nodes):
    """
    Plot the game board with nodes, edges, and tiger nodes.

    Parameters:
    - nodes (list): List of nodes to be plotted.
    - edges (list): List of edges to be plotted.
    - tiger_nodes (list): List of tiger nodes to be plotted.

    Returns:
    None
    """
    fig, ax = plt.subplots(figsize=(8, 8), dpi=100)
    
    # Plot nodes
    for node in nodes:
        color = 'blue'
        if node in tiger_nodes:
            color = 'red'
        ax.plot(node[1], 20 - node[0], 'o', markersize=10, color=color)
    
    
    # Show Legend:
    ax.plot([], [], 'o', markersize=10, color='blue', label='Valid Nodes')
    ax.plot([], [], 'o', markersize=10, color='red', label='Tiger')
    ax.plot([], [], 'o', markersize=10, color='green', label='Goats')
    ax.legend(loc='upper right')


    # Plot edges
    for edge in edges:
        start_node = edge[0]
        for end_node in edge[1]:
            ax.plot([start_node[1], end_node[1]], [20 - start_node[0], 20 - end_node[0]], '-', color='black')

    # Set limits and aspect
    ax.set_xlim(-1, 21)
    ax.set_ylim(-1, 21)
    ax.set_aspect('equal')
    
    # Set integer ticks on x axis
    ax.set_xticks(range(21))
    
    # Invert and set integer ticks on y axis
    ax.set_yticks(range(21))
    ax.set_yticklabels(range(20, -1, -1))
    
    plt.grid(True)
    plt.show()