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

def extract_scen_data(scen_file_path: str) -> list[str]:
    """
    Extract start and goal positions for agents from the .scen file.
    
    Args:
        scen_file_path (str): Path to the .scen file.
        
    Returns:
        list[str]: A list of agent start and goal positions in the format:
                   agent(1). start(1, (row, col)). goal(1, (row, col)).
    """
    scen_data = read_file(scen_file_path,1)
    agent_data = []
    
    for i, line in enumerate(scen_data, start=1):
        parts = line.split()
        agent_id = i
        start_row, start_col = int(parts[4]), int(parts[5])
        goal_row, goal_col = int(parts[6]), int(parts[7])
        
        agent_data.append(f"agent({agent_id}).")
        agent_data.append(f"start({agent_id},({start_row},{start_col})).")
        agent_data.append(f"goal({agent_id},({goal_row},{goal_col})).")
    return agent_data

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
def combine_map_and_scen(map_file_path: str, scen_folder_path: str, output_folder_path: str):
    # Read the map data and convert to vertices
    grid = read_file(map_file_path, num=4)  # Adjust starting line for the map
    vertices = grid_to_vertices(grid)
    
    # Process each .scen file in the scen_folder_path
    for scen_filename in os.listdir(scen_folder_path):
        if scen_filename.endswith(".scen"):
            scen_file_path = os.path.join(scen_folder_path, scen_filename)
            
            # Extract agent start and goal data from the scen file
            agent_data = extract_scen_data(scen_file_path)
            
            # Create output .lp file path
            output_lp_path = os.path.join(output_folder_path, scen_filename.replace(".scen", ".lp"))
            # Write the combined data into the output .lp file
            write_lp_file(output_lp_path, vertices, agent_data)



if __name__ == "__main__":
    map_file = sys.argv[1]
    scen_folder = sys.argv[2]
    output_folder = sys.argv[3]
    increment = 5
    max_agents = 100
    combine_map_and_scen(map_file, scen_folder, output_folder)
