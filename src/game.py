from utils import load_game_config, plot_board

data = load_game_config('data/board_default.json')

nodes = data['nodes']
edges = data['edges']
tiger_nodes = data['tiger_nodes']

plot_board(nodes, edges, tiger_nodes)