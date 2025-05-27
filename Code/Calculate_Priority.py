import networkx as nx
import re
from collections import defaultdict, Counter

# ----------------------------
# File Reading and Parsing
# ----------------------------

def read_from_file(file_path):
    """Reads the entire contents of a .lp instance file."""
    with open(file_path, 'r') as file:
        return file.read()

def parse_input(input_data):
    """
    Parses the .lp input file to extract:
    - Vertices
    - Edges (only cardinal neighbors)
    - Agent start/goal positions
    """
    # Regex patterns
    vertex_pattern = re.compile(r"vertex\(\((\d+),(\d+)\)\)\.")
    agent_pattern = re.compile(r"agent\((\d+)\)\.")
    start_pattern = re.compile(r"start\((\d+),\((\d+),(\d+)\)\)\.")
    goal_pattern = re.compile(r"goal\((\d+),\((\d+),(\d+)\)\)\.")

    # Unique vertex list
    vertex_set = set((int(x), int(y)) for x, y in vertex_pattern.findall(input_data))
    vertices = list(vertex_set)

    # Agent dictionary
    agents = {int(agent_id): {'start': None, 'goal': None} for agent_id in agent_pattern.findall(input_data)}
    for agent_id, x, y in start_pattern.findall(input_data):
        agents[int(agent_id)]['start'] = (int(x), int(y))
    for agent_id, x, y in goal_pattern.findall(input_data):
        agents[int(agent_id)]['goal'] = (int(x), int(y))

    # Generate edges: only 4-neighbor connections (Manhattan distance = 1)
    edges = []
    for x, y in vertex_set:
        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            neighbor = (x + dx, y + dy)
            if neighbor in vertex_set:
                edges.append(((x, y), neighbor))

    return vertices, edges, agents

# ----------------------------
# Graph Construction
# ----------------------------

def build_graph(vertices, edges):
    """Builds and returns a NetworkX graph using given vertices and edges."""
    G = nx.Graph()
    G.add_nodes_from(vertices)
    G.add_edges_from(edges)
    return G

# ----------------------------
# Metric Computation: Static
# ----------------------------

def compute_static_metrics(G, agents):
    bw = nx.betweenness_centrality(G)
    cl = nx.closeness_centrality(G)
    degree = dict(G.degree)

    priority_outputs = {i: [] for i in range(1, 7)}

    for agent_id, data in agents.items():
        start, goal = data['start'], data['goal']
        #Metric 1: OSAP length
        try:
            osap_len = nx.shortest_path_length(G, start, goal)
        except:
            osap_len = 0 #no path
        #Metric 2: Number of shortest paths (inverted)
        try:
            num_paths = len(list(nx.all_shortest_paths(G, start, goal)))
        except:
            num_paths = 0
        #Metric 6: Number of goals within 3 steps +1
        goal_proximity = 1+ sum(
            1 for other in agents.values()
            if other['goal'] != goal and nx.has_path(G, goal, other['goal']) and 
            nx.shortest_path_length(G, goal, other['goal']) <= 3
        )

        metrics = {
            1: osap_len, # Longer path = higher score = higher priority
            2: int(round(100 / max(num_paths, 1))),#less paths = higher score
            3: bw.get(start, 0), #Chokepoint start = higher score
            4: cl.get(start, 0), #More central start = higher score
            5: int(round(100 / max(degree.get(start, 1), 1))), #lower option to move = high score
            6: goal_proximity #higher goal conjection = higher score
        }

        for m_id, score in metrics.items():
            priority_outputs[m_id].append(f"priority({agent_id},{int(round(score))}).")

    for m_id, lines in priority_outputs.items():
        with open(f"priority{m_id}-static.lp", "w") as f:
            f.write('\n'.join(lines))

# ----------------------------
# Metric Computation: k-Paths
# ----------------------------

def compute_kpath_metrics_updated(G, agents, k=5):
    """
    Computes MAPF metrics 7–12 using up to k-shortest paths.
    
    """
    priority_outputs = {i: [] for i in range(7, 13)}
    k_paths_by_agent = {} # Dictionary to store each agent's k shortest paths
    node_heatmap = Counter() # Counts how often each node appears across all agents' k-paths (9)
    edge_heatmap = Counter() #Counts how often each edge is used across all agents' k-paths (10)
    conflict_score = defaultdict(int) # Counts conflicts for each agent (7)

    # Step 1: Collect k-shortest paths and update node/edge heatmaps
    for agent_id, data in agents.items(): #Loop through all agents
        start, goal = data['start'], data['goal'] #Get the start and goal node for the current agent
        try:
            # Fallback to all shortest paths as a proxy for k-shortest equal-cost paths
            k_paths = list(nx.all_shortest_paths(G, start, goal))[:k]
        except nx.NetworkXNoPath:
            k_paths = []
        k_paths_by_agent[agent_id] = k_paths

        for path in k_paths:
            for node in path:
                node_heatmap[node] += 1 #1 / len(k_paths) ???
            for i in range(len(path) - 1):
                edge = tuple(sorted((path[i], path[i + 1])))
                edge_heatmap[edge] += 1 #1 / len(k_paths) ???

    # Step 2: Global node and edge time maps for vertex and swap conflict detection
    global_node_time_map = defaultdict(list)  # (t, node) → list of agent_ids
    global_edge_time_map = defaultdict(list)  # (t, edge) → list of (agent_id, edge)

    for agent_id, paths in k_paths_by_agent.items():
        for path in paths:
            for t in range(len(path)): # at step t
                global_node_time_map[(t, path[t])].append(agent_id) #vertex conflict
                if t < len(path) - 1:
                    move = (path[t], path[t + 1])
                    global_edge_time_map[(t, move)].append((agent_id, move)) #swap conflict
    

    # Metric 7: Projected Conflict Score (Vertex + Swap Conflicts)
    # Step 3: Count vertex conflicts
    for (t, node), agents_here in global_node_time_map.items():
        if len(agents_here) > 1:
            n_conflicts = len(agents_here) - 1
            for agent_id in agents_here:
                conflict_score[agent_id] += n_conflicts  # vertex conflict

    
    for (t, (u, v)), movers in global_edge_time_map.items():
        reverse_edge = (v, u)
        reverse_movers = global_edge_time_map.get((t, reverse_edge), [])
        for agent_a, _ in movers:
            for agent_b, _ in reverse_movers:
                if agent_a < agent_b:  # avoid double-counting
                    conflict_score[agent_a] += 1 #swap conflict
                    conflict_score[agent_b] += 1 #swap conflict

    # Precompute node sets per agent
    agent_node_sets = {
        aid: {node for path in paths for node in path}
        for aid, paths in k_paths_by_agent.items()
    }

    # Step 4: Compute metrics per agent
    for agent_id, paths in k_paths_by_agent.items():
        # Metric 8: Average conflict potential - node overlap with other agents' paths
        # combine the nodes from all other agents
        other_nodes = set().union(*[ # unpacking operator
            nodes for aid, nodes in agent_node_sets.items() if aid != agent_id
        ])
        conflict_score_sum = sum(
            1 for path in paths for node in path if node in other_nodes
        )
        avg_conflict = conflict_score_sum / max(len(paths), 1)

        # Metric 9: Node congestion score
        node_overlap_score = sum(node_heatmap[n] for path in paths for n in path) #Higher score - agent travels through busy areas

        # Metric 10: Edge congestion score (average per path)
        shared_edges = sum(
            edge_heatmap[tuple(sorted((path[i], path[i + 1]))) ] #(A,B) and (B,A) are treated the same
            for path in paths for i in range(len(path) - 1)
        )
        avg_shared_edges = shared_edges / max(len(paths), 1)

        # Metric 11: Agent overlap count (set intersection method)
        current_nodes = agent_node_sets[agent_id]
        overlapping_agents = {
            other_id for other_id, other_nodes in agent_node_sets.items()
            if other_id != agent_id and current_nodes & other_nodes # intersection
        }
        agent_overlap_count = len(overlapping_agents) #Collects all agents who share at least one node

        # Metric 12: Inverse of number of alternative routes
        num_kpaths = len(paths)
        alt_route_score = 1 / max(num_kpaths, 1)

        metrics = {
            7: conflict_score[agent_id],
            8: avg_conflict,
            9: node_overlap_score,
            10: avg_shared_edges,
            11: agent_overlap_count,
            12: alt_route_score
        }

        for m_id, score in metrics.items():
            priority_outputs[m_id].append(f"priority({agent_id},{int(round(score))}).")

    # Step 5: Write output files
    for m_id, lines in priority_outputs.items():
        with open(f"priority{m_id}-kpath.lp", "w") as f:
            f.write('\n'.join(lines))


input_data = read_from_file("path_to_instance.lp")
vertices, edges, agents = parse_input(input_data)
G = build_graph(vertices, edges)
compute_static_metrics(G, agents)
compute_kpath_metrics_updated(G, agents, k=5)
