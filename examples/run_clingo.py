import subprocess
import sys
import timeit
import logging
from functools import wraps
import os
import re

# Configure logging
logging.basicConfig(
    level=logging.INFO, #General information about the program's execution.
    format="%(asctime)s: %(message)s",
    handlers=[
        logging.FileHandler("MAPF_solver.log"),  # Log to a file
        logging.StreamHandler()  # Log to console
    ]
)



# Decorator to log cumulative time and other details
def log_cumulative_time(func):
    @wraps(func)
    def wrapper(file_path,*args, **kwargs):
        cumulative_time = 0  # Initialize cumulative time
        delta = 0  # Start with delta = 0
        timeout = 1000  # Timeout for a single iteration in seconds
        
        
        while True:
            start = timeit.default_timer()
            result = func(file_path, delta, timeout, *args, **kwargs)  # Call the decorated function
            end = timeit.default_timer()
            iteration_time = end - start
            cumulative_time += iteration_time

            if result == "timeout":
                logging.info(f"delta : {delta}, time : {cumulative_time:.2f} (timeout)")
                return True  # Stop processing further files
            elif result == "solution_found":
                logging.info(f"delta : {delta}, time : {cumulative_time:.2f} (solution found)")
                return False  # Continue processing next file

            delta += 1  # Increment delta for the next iteration

    return wrapper

# Main function to run the solver
@log_cumulative_time
def run_solver(file_path, delta, timeout):
    python_executable = sys.executable  # Detect current Python executable
    command = [
        python_executable, "MAPF_with_priority.py", f'--delta={delta}', "priority.lp",
        file_path#, "--heuristic=domain"#,"--stats"
    ]

    try:
        result = subprocess.run(command, capture_output=True, text=True, timeout=timeout)
    except subprocess.TimeoutExpired:
        return "timeout"  # Timeout occurred

    # Capture the clingo statistics
    stdout = result.stdout

    if "The problem is satisfiable!" in stdout:
        # Use regex to extract the time stats section between the markers
        stats_section = re.search(r"Statistics:(.*?)SATISFIABLE", stdout, re.DOTALL)

        if stats_section:
            # Extract and log the time stats directly
            for line in stats_section.group(1).splitlines():
                if any(line.startswith(prefix) for prefix in ["Load", "Ground Instance", "Extract Problem", "Reachable", "Ground Encoding", "Solve Encoding"]):
                    category, time_value = line.split(":")
                    logging.info(f"{category} Time: {time_value} seconds")

        return "solution_found"

    return "continue"  # Continue to the next delta iteration

# Get all .lp files in the folder and process them
def process_all_files():
    lp_files = sorted(
    [os.path.join(FOLDER_PATH, f) for f in os.listdir(FOLDER_PATH) if f.endswith(".lp")],
    key=os.path.getctime)  # Sort by creation time
    
    logging.info(f"Processing file: {lp_files[0].split('\\')[3]} with {Heuristics} Heuristics")  # Log the file being processed

    for file_path in lp_files:
        timeout_occurred = run_solver(file_path)  # Process each file
        if timeout_occurred:  # Stop further processing if timeout occurred
            break

FOLDER_PATH = "instances_old"
Heuristics = 'No'
# Start processing all files
process_all_files()