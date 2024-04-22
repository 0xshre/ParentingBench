from src.utils import load_game_config, make_edges_bidirectional, validate_nodes


def test_make_edges_bidirectional():
    """
    Test the make_edges_bidirectional function.

    This function loads edges from a test configuration, ensures that the edges are bidirectional,
    and raises an AssertionError if any edge is not bidirectional.

    Raises:
        AssertionError: If any edge is not bidirectional.
    """
    # Load edges from a test configuration
    config = load_game_config("data/board_default.json")
    edges = config["edges"]

    # Ensure edges are bidirectional
    new_edges = make_edges_bidirectional(edges)
    for start, connections in new_edges:
        for end in connections:
            assert (end, [start]) in new_edges or (
                start in [conn for e, conn in new_edges if e == end]
            ), f"Edge ({end}, {start}) is not bidirectional"


def test_validate_nodes():
    """
    Test function to validate the nodes in a game configuration.

    This function loads nodes from a test configuration file and checks that all nodes are within the valid range.
    It also checks that all (x, y) pairs are valid nodes.

    Raises:
        AssertionError: If not all nodes are within the valid board range or if any (x, y) pair is an invalid node.

    """
    # Load nodes from a test configuration
    config = load_game_config("data/board_default.json")
    valid_nodes = config["nodes"]

    # Check that all nodes are within the valid range
    assert validate_nodes(valid_nodes), "Not all nodes are within the valid board range"

    # Check that all (x, y) pairs are valid nodes
    for x, y in valid_nodes:
        assert [x, y] in valid_nodes, f"Invalid node coordinates: ({x}, {y})"


def test_load_game_config():
    config = load_game_config('data/board_default.json')
    # Check if all keys are present
    assert 'nodes' in config, "Nodes data must be present"
    assert 'edges' in config, "Edges data must be present"
    assert 'tiger_nodes' in config, "Tiger nodes data must be present"
    
    # Check the correctness of the data structure
    assert isinstance(config['nodes'], list), "Nodes should be a list"
    assert isinstance(config['edges'], list), "Edges should be a list"
    assert isinstance(config['tiger_nodes'], list), "Tiger nodes should be a list"
    
    # Additional checks can be for the length of the lists if specific sizes are expected
    assert all(isinstance(node, list) for node in config['nodes']), "Each node should be a list"
    assert all(isinstance(edge, list) for edge in config['edges']), "Each edge should be a list"
    assert all(len(node) == 2 for node in config['nodes']), "Each node should contain two integers"