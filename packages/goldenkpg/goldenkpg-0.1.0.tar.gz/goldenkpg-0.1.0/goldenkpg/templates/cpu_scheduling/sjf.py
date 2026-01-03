"""
CPU Scheduling Algorithm: SJF (Shortest Job First) - Non-Preemptive
-------------------------------------------------------------------
Description:
Selects the waiting process with the smallest execution time (burst time) to execute next.
This approach minimizes the average waiting time.

Logic:
1. Maintain a list of available processes.
2. At any point, select the process with min burst time from those that have arrived.
3. If no process has arrived, advance time.
"""

def calculate_sjf(processes):
    n = len(processes)
    completed = 0
    current_time = 0
    visited = [False] * n
    
    # Sort by arrival first to handle tie-breaking or initial check easily
    # Note: Logic below finds min burst among arrived, so initial sort helps mainly visualization
    # We will work on a copy to not mutate original if needed, but here we just flag 'visited'
    
    total_tat = 0
    total_wt = 0
    
    print(f"\n{'PID':<5}{'Arrival':<10}{'Burst':<10}{'CT':<10}{'TAT':<10}{'WT':<10}")
    print("-" * 55)

    while completed < n:
        # Find process with min burst among those arrived and not visited
        idx = -1
        min_burst = float('inf')
        
        for i in range(n):
            if not visited[i] and processes[i]['arrival'] <= current_time:
                if processes[i]['burst'] < min_burst:
                    min_burst = processes[i]['burst']
                    idx = i
                # Optional: Tie-breaker on arrival time if bursts are equal?
                # Usually FCFS for ties, which loop order might handle if sorted by arrival initially

        if idx != -1:
            # Execute process
            p = processes[idx]
            completion_time = current_time + p['burst']
            turnaround_time = completion_time - p['arrival']
            waiting_time = turnaround_time - p['burst']
            
            total_tat += turnaround_time
            total_wt += waiting_time
            
            print(f"{p['id']:<5}{p['arrival']:<10}{p['burst']:<10}{completion_time:<10}{turnaround_time:<10}{waiting_time:<10}")
            
            visited[idx] = True
            current_time = completion_time
            completed += 1
        else:
            # No process arrived yet using current logic, jump to next arrival
            # Optimization: Find the nearest arrival time > current_time
            # Alternatively just increment time (simpler but slower for large gaps)
            current_time += 1

    print("-" * 55)
    print(f"Average TAT: {total_tat / n:.2f}")
    print(f"Average WT:  {total_wt / n:.2f}")

if __name__ == "__main__":
    print("--- SJF (Non-Preemptive) CPU Scheduling ---")
    
    data = [
        {'id': 'P1', 'arrival': 1, 'burst': 7},
        {'id': 'P2', 'arrival': 2, 'burst': 5},
        {'id': 'P3', 'arrival': 3, 'burst': 1},
        {'id': 'P4', 'arrival': 4, 'burst': 2},
        {'id': 'P5', 'arrival': 0, 'burst': 8},
    ]

    calculate_sjf(data)
