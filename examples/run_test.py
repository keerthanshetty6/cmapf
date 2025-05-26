import subprocess
import sys
import timeit 

upper_bound :int  = 25  # horizon
python_executable = sys.executable  # Automatically detects the current Python executable

# Run clingo with the pathfinding model
for i in range(0, upper_bound):
    command = [python_executable, "MAPF_with_priority.py", f'--delta={i}', "priority.lp", "instances_old\\toy1.lp","--stats"]#,"--heuristic=domain"]
    start = timeit.default_timer()
    result = subprocess.run(command, capture_output=True, text=True)
    end = timeit.default_timer()
    # Get the clingo output (stdout)
    output = result.stdout
    print(f"for iteration {i} time taken :{end - start}")
    if "The problem is satisfiable!" in output:
        print(output)
        break
