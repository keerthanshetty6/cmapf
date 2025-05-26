import re

# Assuming output contains the full output of your program
output = """clingo version 5.7.1
Reading from priority.lp ...
Solving...
Answer: 1
penalty_summary(1,shortest_path(6),Path_taken(6)) penalty_summary(2,shortest_path(4),Path_taken(4)) penalty_summary(3,shortest_path(6),Path_taken(6)) penalty_summary(4,shortest_path(6),Path_taken(6)) penalty_summary(5,shortest_path(5),Path_taken(5))
The problem is satisfiable!
SATISFIABLE

Models       : 1+
Calls        : 1
Time         : 0.024s (Solving: 0.01s 1st Model: 0.00s Unsat: 0.00s)
CPU Time     : 0.000s

Choices      : 10
Conflicts    : 0        (Analyzed: 0)
Restarts     : 0
Model-Level  : 11.0
Problems     : 1        (Average Length: 1.00 Splits: 0)
Lemmas       : 0        (Deleted: 0)
  Binary     : 0        (Ratio:   0.00%)
  Ternary    : 0        (Ratio:   0.00%)
  Conflict   : 0        (Average Length:    0.0 Ratio:   0.00%)
  Loop       : 0        (Average Length:    0.0 Ratio:   0.00%)
  Other      : 0        (Average Length:    0.0 Ratio:   0.00%)
Backjumps    : 0        (Average:  0.00 Max:   0 Sum:      0)
  Executed   : 0        (Average:  0.00 Max:   0 Sum:      0 Ratio:   0.00%)
  Bounded    : 0        (Average:  0.00 Max:   0 Sum:      0 Ratio: 100.00%)

Rules        : 1133     (Original: 1118)
  Choice     : 56
Atoms        : 953
Bodies       : 232      (Original: 217)
  Count      : 0        (Original: 6)
Equivalences : 508      (Atom=Atom: 194 Body=Body: 34 Other: 280)
Tight        : Yes
Variables    : 172      (Eliminated:    0 Frozen:  172)
Constraints  : 363      (Binary:  77.4% Ternary:  22.6% Other:   0.0%)

PriorityMAPF
  Time
    Load     : 0.0028565
    Ground Instance: 0.0032117
    Extract Problem: 0.0001653
    Reachable: 0.0006804
    Ground Encoding: 0.0065477
  Delta      : 0
  Reachable  : 61
  Min Cost   : 27
  Min Horizon: 6
  Total Cost : 27
  Max Horizon: 6"""

# Try a simple pattern to match the "PriorityMAPF Time" block and test
pattern = re.compile(r"PriorityMAPF\s+Time([\s\S]+?)\s+Delta", re.DOTALL)  # match everything from "PriorityMAPF Time" to "Delta"

# Check if pattern is capturing anything
priority_time_match = re.search(r"PriorityMAPF\s+Time([\s\S]+?)\s+Delta", output)

if priority_time_match:
    print("Pattern found!")
    # Extract times if available
    time_values = re.findall(r"([A-Za-z\s]+):\s*([\d.]+)", priority_time_match.group(1))

    for key, value in time_values:
        print(f"{key.strip()} : {value.strip()}s")
else:
    print("Pattern not matched!")
