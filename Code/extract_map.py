import os
import sys

def grid_to_vertices(grid) -> list:
    """
    Converts a grid map to vertices in the format vertex((row, col)).

    Args:
        grid (List[str]): List of strings representing the grid map.

    Returns:
        List[str]: List of vertices in the format vertex((row, col)).
    """
    vertices: list = []
    rows: int = len(grid)
    cols: int = len(grid[0])

    for row in range(rows):
        for col in range(cols):
            if grid[row][col] == '.':  # Only consider open cells
                vertices.append(f"vertex(({row},{col})).")
        vertices.append("")
    vertices.append("")
    
    return vertices

def read_file(file_path, num=0) -> list[str]:
    """
    Reads the grid data from the file starting from the specified line number.
    
    Args:
        file_path (str): Path to the .map or .scen file.
        num (int): Line number to start reading from (default 0).
        
    Returns:
        list[str]: A list of strings representing the data.
    """
    with open(file_path, 'r') as file:
        lines = file.readlines()
        # Process lines starting from the 'num' line (index num)
        data: list[str] = [line.strip() for line in lines[num:]]  # Remove (\n) trailing newlines
        return data

def extract_scen_data(scen_file_path: str, max_agents: int, increment: int) -> list[list[str]]:
    """
    Extract start and goal positions for agents from the .scen file in increments.
    
    Args:
        scen_file_path (str): Path to the .scen file.
        max_agents (int): Maximum number of agents to extract.
        increment (int): Increment step for the number of agents.
        
    Returns:
        list[list[str]]: A list of lists, where each inner list contains agent data for a specific increment.
    """
    scen_data = read_file(scen_file_path, 1)
    all_agent_data = []
    
    # Adjust max_agents to the next multiple of increment if necessary
    if max_agents % increment != 0:
        max_agents = max_agents + increment - (max_agents % increment)
    
    # Extract agents in increments
    for i in range(increment, max_agents + 1, increment):
        agent_data = []
        for j in range(i):
            if j >= len(scen_data):
                break
            parts = scen_data[j].split()
            agent_id = j + 1
            start_row, start_col = int(parts[4]), int(parts[5])
            goal_row, goal_col = int(parts[6]), int(parts[7])
            
            agent_data.append(f"agent({agent_id}).")
            agent_data.append(f"start({agent_id},({start_row},{start_col})).")
            agent_data.append(f"goal({agent_id},({goal_row},{goal_col})).")
        all_agent_data.append(agent_data)
    
    return all_agent_data

def write_lp_file(output_path: str, vertices: list, agent_data: list):
    """
    Write the vertices and agent data into an .lp file.
    
    Args:
        output_path (str): Path to the output .lp file.
        vertices (list): List of vertices in the format vertex((row, col)).
        agent_data (list): List of agent start and goal data.
    """
    with open(output_path, 'w') as file:
        # Write vertices
        for vertex in vertices:
            file.write(vertex + "\n")
        
        # Write agent start and goal data

        for i,agent in enumerate(agent_data,start=1):
            file.write(agent + "\n")
            if i % 3 == 0:
                file.write("\n")

        
        # Add the edge rule at the end
        file.write("edge((X,Y),(X',Y')) :- vertex((X,Y)), vertex((X',Y')), |X-X'|+|Y-Y'|=1.\n")

# Main function to combine the map and scen data into one .lp file
def combine_map_and_scen(map_file_path: str, scen_folder_path: str, output_folder_path: str, increment: int, max_agents: int):
    # Read the map data and convert to vertices
    grid = read_file(map_file_path, num=4)  # Adjust starting line for the map
    vertices = grid_to_vertices(grid)
    
    # Process each .scen file in the scen_folder_path
    for scen_filename in os.listdir(scen_folder_path):
        if scen_filename.endswith(".scen"):
            scen_file_path = os.path.join(scen_folder_path, scen_filename)
            
            # Extract agent start and goal data from the scen file in increments
            all_agent_data = extract_scen_data(scen_file_path, max_agents, increment)
            
             # Create a separate folder for this .scen file
            scen_folder_name = os.path.splitext(scen_filename)[0]  # Remove .scen extension
            scen_output_folder = os.path.join(output_folder_path, scen_folder_name)
            
            # Create the folder if it doesn't exist
            os.makedirs(scen_output_folder, exist_ok=True)

            # Create output .lp files for each increment
            for i, agent_data in enumerate(all_agent_data, start=1):
                # Calculate the actual number of agents in this file
                actual_agents = len(agent_data) // 3  # Each agent has 3 lines: agent, start, goal
                
                 # Determine the file name
                if i * increment <= max_agents:
                    output_lp_path = os.path.join(scen_output_folder, f"{scen_folder_name}_{i * increment}.lp")
                else:
                    output_lp_path = os.path.join(scen_output_folder, f"{scen_folder_name}_{actual_agents}.lp")
                
                # Write the file
                write_lp_file(output_lp_path, vertices, agent_data)

if __name__ == "__main__":
    # Command-line arguments
    map_file = sys.argv[1]  # Path to the .map file
    scen_folder = sys.argv[2]  # Path to the folder containing .scen files
    output_folder = sys.argv[3]  # Path to the folder where .lp files will be saved
    increment = int(sys.argv[4])  # Increment step for the number of agents (e.g., 5, 10, etc.)
    max_agents = int(sys.argv[5])  # Maximum number of agents to extract

    # Call the main function
    combine_map_and_scen(map_file, scen_folder, output_folder, increment, max_agents)


    #python extract_map.py '\instances\Empty\empty-8-8\empty-8-8.map' '\instances\Empty\empty-8-8\scen-random' '\instances\Processed\empty-8-8-random-1' 5 32
    #python extract_map.py 'Instances\maps\empty-32-32.map' 'Instances\scenarios\empty-32-32' 'Instances\Processed\empty-32-32' 5 100