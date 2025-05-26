import subprocess
import sys
import timeit
import logging
from functools import wraps
import os
import re
import pandas as pd
import openpyxl 
import locale
import numpy as np

# Set locale to use comma as a decimal separator
locale.setlocale(locale.LC_NUMERIC, "de_DE")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
    handlers=[
        logging.FileHandler("MAPF_solver.log"),  # Log to a file
        logging.StreamHandler()  # Log to console
    ]
)
   
# Initialize a DataFrame to hold the results (this will be saved to Excel later)
columns = ['Processing File', 'Heuristics', 'Load Time', 'Ground Instance Time', 'Extract Problem Time',
           'Reachable Time', 'Ground Encoding Time', 'Solve Encoding Time', 'Delta', 'Total Time']

# Load existing results from Excel file (if it exists)
EXCEL_FILE = "solver_results.xlsx"
if os.path.exists(EXCEL_FILE):
    results_df = pd.read_excel(EXCEL_FILE, engine='openpyxl')
else:
    results_df = pd.DataFrame(columns=columns)

TIMEOUT = 300  # Timeout for a single iteration in seconds

# Decorator to log cumulative time and other details
def log_cumulative_time(func):
    @wraps(func)
    def wrapper(file_path, *args, **kwargs):
        cumulative_time = 0  # Initialize cumulative time
        delta = 0  # Start with delta = 0    
        logging.info(f"file : {os.path.basename(file_path)},Heuristic : {Heuristics}")
        while True:
            #start = timeit.default_timer()
            result, time_spent,stats  = func(file_path,delta, *args, **kwargs)  # Call the decorated function
            #end = timeit.default_timer()
            #iteration_time = end - start
            cumulative_time += time_spent
            
            
            # Append the results for this delta iteration to the DataFrame
            results_df.loc[len(results_df)] = [
                os.path.basename(file_path), Heuristics,
                float(stats.get('Load', 0)) if stats.get('Load') else np.nan,
                float(stats.get('Ground Instance', 0)) if stats.get('Ground Instance') else np.nan,
                float(stats.get('Extract Problem', 0)) if stats.get('Extract Problem') else np.nan,
                float(stats.get('Reachable', 0)) if stats.get('Reachable') else np.nan,
                float(stats.get('Ground Encoding', 0)) if stats.get('Ground Encoding') else np.nan,
                float(stats.get('Solve Encoding', 0)) if stats.get('Solve Encoding') else np.nan,
                delta, float(cumulative_time)  # Ensure numeric values
                ] 

            if result == "timeout":
                logging.info(f"file : {os.path.basename(file_path)},Heuristic : {Heuristics}, delta : {delta}, time : {cumulative_time:.2f} (timeout)")
                return True    # Stop processing further files
            elif result == "solution_found":
                logging.info(f"file : {os.path.basename(file_path)},Heuristic : {Heuristics}, delta : {delta}, time : {cumulative_time:.2f} (solution found)")
                return False    # Continue processing next file

            delta += 1  # Increment delta for the next iteration
            logging.info(f" delta : {delta}, time_spent : {time_spent:.2f}")
    return wrapper

# Main function to run the solver
@log_cumulative_time
def run_solver(file_path,delta, *args, **kwargs):
    python_executable = sys.executable  # Detect current Python executable
    command = [
        python_executable, "MAPF_with_priority.py", f'--delta={delta}', "priority.lp",
        file_path#, "--heuristic=domain"#,"--stats"
    ]

    start_time = timeit.default_timer()
    try:
        result = subprocess.run(command, capture_output=True, text=True, timeout=TIMEOUT)
    except subprocess.TimeoutExpired:
        elapsed_time = timeit.default_timer() - start_time  # Time spent before timeout
        logging.info(f"Timeout occurred after {elapsed_time:.2f} seconds")
        return "timeout", elapsed_time,{}  # Return timeout and time spent so far
       


    iteration_time = timeit.default_timer() - start_time  # Time taken for this iteration
    # Capture the clingo statistics
    stdout = result.stdout

    stats = {}
    # Extract and log time statistics if available
    stats_section = re.search(r"Statistics:(.*?)SATISFIABLE", stdout, re.DOTALL) or re.search(r"Statistics:(.*?)UNSATISFIABLE", stdout, re.DOTALL)
    
    if stats_section:
        # Extract and log the time stats directly
        for line in stats_section.group(1).splitlines():
            if any(line.startswith(prefix) for prefix in ["Load", "Ground Instance", "Extract Problem", "Reachable", "Ground Encoding", "Solve Encoding"]):
                category, time_value = line.split(":")
                stats[category] = time_value.strip()
                #logging.info(f"{category} Time: {time_value} seconds")

    if "The problem is satisfiable!" in stdout:
        return "solution_found", iteration_time, stats

    return "continue", iteration_time, stats



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

    results_df.to_excel("solver_results.xlsx", index=False)

FOLDER_PATH = "Instances\Processed\empty-32-32\empty-32-32-condensed-0"
Heuristics = 'No'


# Start processing all files
process_all_files()