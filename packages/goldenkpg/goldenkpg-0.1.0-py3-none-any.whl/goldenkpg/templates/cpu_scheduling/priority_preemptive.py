"""
CPU Scheduling Algorithm: Priority Scheduling (Preemptive)
----------------------------------------------------------
Description:
The CPU is allocated to the process with the highest priority (number). 
If a new process arrives with a higher priority than the currently running process, the current process is preempted.
HERE: LOWER number = HIGHER priority (e.g., 1 is top priority).

Logic:
1. At each time unit, check all available processes.
2. Select process with highest priority (lowest number in this implementation).
3. If multiple have same priority, FCFS is used (arrival time).
"""

def calculate_priority_preemptive(processes):
    n = len(processes)
    current_time = 0
    completed = 0
    total_tat = 0
    total_wt = 0
    
    for p in processes:
        p['remaining'] = p['burst']
    
    print(f"\n{'PID':<5}{'Arrival':<10}{'Burst':<10}{'Priority':<10}{'CT':<10}{'TAT':<10}{'WT':<10}")
    print("-" * 65)

    while completed < n:
        idx = -1
        # Find highest priority (lowest value) among arrived and incomplete
        best_priority = float('inf')
        
        for i in range(n):
            if processes[i]['arrival'] <= current_time and processes[i]['remaining'] > 0:
                if processes[i]['priority'] < best_priority:
                    best_priority = processes[i]['priority']
                    idx = i
                elif processes[i]['priority'] == best_priority:
                    # Tie-breaker: Arrival time
                    if processes[i]['arrival'] < processes[idx]['arrival']:
                        idx = i
        
        if idx != -1:
            processes[idx]['remaining'] -= 1
            current_time += 1
            
            if processes[idx]['remaining'] == 0:
                completed += 1
                completion_time = current_time
                turnaround_time = completion_time - processes[idx]['arrival']
                waiting_time = turnaround_time - processes[idx]['burst']
                
                total_tat += turnaround_time
                total_wt += waiting_time
                
                p = processes[idx]
                print(f"{p['id']:<5}{p['arrival']:<10}{p['burst']:<10}{p['priority']:<10}{completion_time:<10}{turnaround_time:<10}{waiting_time:<10}")
        else:
            current_time += 1

    print("-" * 65)
    print(f"Average TAT: {total_tat / n:.2f}")
    print(f"Average WT:  {total_wt / n:.2f}")

if __name__ == "__main__":
    print("--- Priority Scheduling (Preemptive) ---")
    print("Note: Lower value = Higher Priority")
    
    data = [
        {'id': 'P1', 'arrival': 0, 'burst': 10, 'priority': 3},
        {'id': 'P2', 'arrival': 1, 'burst': 1, 'priority': 1},
        {'id': 'P3', 'arrival': 2, 'burst': 2, 'priority': 4},
        {'id': 'P4', 'arrival': 3, 'burst': 1, 'priority': 5},
        {'id': 'P5', 'arrival': 4, 'burst': 5, 'priority': 2},
    ]
    
    calculate_priority_preemptive(data)
