"""
CPU Scheduling Algorithm: SRTF (Shortest Remaining Time First) - Preemptive SJF
-------------------------------------------------------------------------------
Description:
Preemptive version of SJF. The process with the smallest amount of time remaining until completion is selected to execute.
If a new process arrives with a shorter burst time than the remaining time of the current process, the current process is preempted.

Logic:
1. At each time unit, check for arriving processes.
2. Select process with minimum remaining time among all available processes.
3. If current process is different from previous, a context switch occurred.
4. Decrement remaining time of selected process.
5. If remaining time is 0, process is completed.
"""

def calculate_srtf(processes):
    n = len(processes)
    current_time = 0
    completed = 0
    total_tat = 0
    total_wt = 0
    
    # Initialize remaining time
    for p in processes:
        p['remaining'] = p['burst']
        p['start_times'] = [] # To track when it runs for Gantt chart
    
    print(f"\n{'PID':<5}{'Arrival':<10}{'Burst':<10}{'CT':<10}{'TAT':<10}{'WT':<10}")
    print("-" * 55)

    while completed < n:
        # Find process with min remaining time among arrived and not completed
        idx = -1
        min_remaining = float('inf')
        
        for i in range(n):
            if processes[i]['arrival'] <= current_time and processes[i]['remaining'] > 0:
                if processes[i]['remaining'] < min_remaining:
                    min_remaining = processes[i]['remaining']
                    idx = i
                # Tie breaker: Arrival time
                if processes[i]['remaining'] == min_remaining:
                    if processes[i]['arrival'] < processes[idx]['arrival']:
                        idx = i

        if idx != -1:
            # Execute for 1 unit
            processes[idx]['remaining'] -= 1
            current_time += 1
            
            # Check for completion
            if processes[idx]['remaining'] == 0:
                completed += 1
                completion_time = current_time
                turnaround_time = completion_time - processes[idx]['arrival']
                waiting_time = turnaround_time - processes[idx]['burst']
                
                total_tat += turnaround_time
                total_wt += waiting_time
                
                p = processes[idx]
                print(f"{p['id']:<5}{p['arrival']:<10}{p['burst']:<10}{completion_time:<10}{turnaround_time:<10}{waiting_time:<10}")
        else:
            current_time += 1

    print("-" * 55)
    print(f"Average TAT: {total_tat / n:.2f}")
    print(f"Average WT:  {total_wt / n:.2f}")

if __name__ == "__main__":
    print("--- SRTF (Preemptive SJF) CPU Scheduling ---")
    
    data = [
        {'id': 'P1', 'arrival': 0, 'burst': 8},
        {'id': 'P2', 'arrival': 1, 'burst': 4},
        {'id': 'P3', 'arrival': 2, 'burst': 9},
        {'id': 'P4', 'arrival': 3, 'burst': 5},
    ]
    
    calculate_srtf(data)
