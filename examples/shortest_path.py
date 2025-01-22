import networkx as nx
import matplotlib.pyplot as plt
import re

def read_from_file(file_path):
    with open(file_path, 'r') as file:
        return file.read()

def parse_input(input_data):
    """
    Parse the input file generated to extract vertices, edges, and agent info.
    """
    vertices: list[tuple[int, int]] = []  # List of (x, y) coordinates
    edges: list[tuple[tuple[int, int], tuple[int, int]]] = []  # List of ((x1, y1), (x2, y2)) edges
    agents: dict[int, dict[str, tuple[int, int] | None]] = {}  # Agent ID -> {'start': (x, y), 'goal': (x, y) }

    # Creating regex expression objects for vertices, agents, and start/goal
    vertex_pattern = re.compile(r"vertex\(\((\d+),(\d+)\)\)\.")
    agent_pattern = re.compile(r"agent\((\d+)\)\.")
    start_pattern = re.compile(r"start\((\d+),\((\d+),(\d+)\)\)\.")
    goal_pattern = re.compile(r"goal\((\d+),\((\d+),(\d+)\)\)\.")

    # Parse vertices
    vertices = [(int(x), int(y)) for x, y in vertex_pattern.findall(input_data)]

    # Parse agents, starts, and goals
    for agent_id in agent_pattern.findall(input_data):
        agents[int(agent_id)] = {'start': None, 'goal': None}

    for agent_id, x, y in start_pattern.findall(input_data):
        agents[int(agent_id)]['start'] = (int(x), int(y))

    for agent_id, x, y in goal_pattern.findall(input_data):
        agents[int(agent_id)]['goal'] = (int(x), int(y))

    # Generate edges based on |X-X'| + |Y-Y'| = 1
    for (x, y) in vertices:
        for (x_prime, y_prime) in vertices:
            if abs(x - x_prime) + abs(y - y_prime) == 1:  # Manhattan distance = 1
                edges.append(((x, y), (x_prime, y_prime)))

    return vertices, edges, agents

def build_graph(vertices, edges, agents):
    """
    Build a NetworkX graph using the parsed data.
    """
    G = nx.Graph()
    G.add_nodes_from(vertices)
    G.add_edges_from(edges)

    #Add agent information as node attributes
    for agent_id, data in agents.items():
        if data['start'] is not None:
            G.nodes[data['start']]['agent_start'] = agent_id
        if data['goal'] is not None:
            G.nodes[data['goal']]['agent_goal'] = agent_id

    return G

def calculate_shortest_path(G, agents):
    """
    Compute the shortest path length for each agent.
    Returns a dictionary {agent_id: path_length}.
    """

    shortest_paths = {}

    for agent_id, agent_data in agents.items():
        start_node = agent_data['start']
        goal_node = agent_data['goal']
        try:
            path = nx.shortest_path(G, start_node, goal_node)
            shortest_paths[agent_id] = len(path) - 1  # Path length (excluding start node)
        except nx.NetworkXNoPath:
            shortest_paths[agent_id] = float('inf')  # No path found

    return shortest_paths


def calculate_priority_by_paths(G, agents):
    """
    Compute priority based on the number of shortest paths.
    Agents with fewer paths get higher priority.
    Prints priority(agent_id, priority_value).
    """
    num_paths = {}

    # Compute the number of shortest paths for each agent
    for agent_id, agent_data in agents.items():
        start_node = agent_data['start']
        goal_node = agent_data['goal']
        try:
            all_shortest_paths = list(nx.all_shortest_paths(G, start_node, goal_node))
            num_paths[agent_id] = len(all_shortest_paths)  # Count of shortest paths
        except nx.NetworkXNoPath:
            num_paths[agent_id] = 0  # No path found

    # Sort agents by number of shortest paths (ascending order)
    sorted_agents = sorted(num_paths.items(), key=lambda x: x[1])

    # Assign priority (higher priority for fewer paths)
    priority = 100  # Start with a high priority
    previous_num_paths = None

    for agent_id, path_count in sorted_agents:
        if path_count == previous_num_paths:
            curr_priority = priority  # Maintain same priority
        else:
            priority -= 1  # Decrease priority
            curr_priority = priority  

        previous_num_paths = path_count
        print(f"priority({agent_id},{curr_priority}).")  # Output format as requested

    return sorted_agents  # Return sorted agents with their path counts


def calculate_graph_metrics(G, agents):
    """Computes degree and centrality measures for agent start and goal positions."""
    degree = dict(G.degree)
    betweenness = nx.betweenness_centrality(G)
    
    degree_start = [(agent_id, degree[data['start']]) for agent_id, data in agents.items()]
    degree_goal = [(agent_id, degree[data['goal']]) for agent_id, data in agents.items()]
    
    centrality_bw_start = [(agent_id, betweenness[data['start']]) for agent_id, data in agents.items()]
    centrality_bw_goal = [(agent_id, betweenness[data['goal']]) for agent_id, data in agents.items()]
    
    centrality_cl_start = [(agent_id, nx.closeness_centrality(G, data['start'])) for agent_id, data in agents.items()]
    centrality_cl_goal = [(agent_id, nx.closeness_centrality(G, data['goal'])) for agent_id, data in agents.items()]
    
    return degree_start, degree_goal, centrality_bw_start, centrality_bw_goal, centrality_cl_start, centrality_cl_goal

def visualize_graph(G, agents):
    """Visualizes the graph with agent start and goal positions highlighted."""
    node_colors = ['lightblue' for _ in G.nodes]
    for data in agents.values():
        node_colors[list(G.nodes).index(data['start'])] = 'green'
        node_colors[list(G.nodes).index(data['goal'])] = 'red'
    
    pos = {node: node for node in G.nodes()}
    agent_labels = {data['start']: f"S{agent_id}" for agent_id, data in agents.items()}
    agent_labels.update({data['goal']: f"G{agent_id}" for agent_id, data in agents.items()})
    
    plt.figure(figsize=(8, 8))
    nx.draw_networkx_nodes(G, pos, node_color=node_colors, node_size=500)
    nx.draw_networkx_edges(G, pos, edge_color='gray', alpha=0.7)
    nx.draw_networkx_labels(G, {node: (x, y - 0.2) for node, (x, y) in pos.items()}, font_size=10)
    nx.draw_networkx_labels(G, pos, labels=agent_labels, font_color='black', font_size=10, font_weight='bold')
    plt.title("Graph Visualization with Agent Start and Goal Positions")
    plt.show()

input_data = read_from_file("instances\Processed\empty-8-8-random-5.lp")

vertices, edges, agents = parse_input(input_data)
G = build_graph(vertices, edges, agents)
shortest_paths_num = calculate_priority_by_paths(G, agents)
#deg_start, deg_goal, start_bw, goal_bw, start_cl, goal_cl = calculate_graph_metrics(G, agents)
visualize_graph(G, agents)