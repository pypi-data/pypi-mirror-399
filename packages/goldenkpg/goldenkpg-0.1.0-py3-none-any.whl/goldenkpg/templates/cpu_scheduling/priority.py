"""
CPU Scheduling Algorithm: Priority Scheduling (Non-Preemptive)
--------------------------------------------------------------
Description:
Processes are executed based on priority. 
Higher priority number could mean higher or lower priority depending on convention.
HERE: LOWER number = HIGHER priority (e.g., 1 is top priority).

Logic similar to SJF, but selects based on Priority instead of Burst Time.
"""

def calculate_priority(processes):
    n = len(processes)
    completed = 0
    current_time = 0
    visited = [False] * n
    
    total_tat = 0
    total_wt = 0
    
    print(f"\n{'PID':<5}{'Arrival':<10}{'Burst':<10}{'Priority':<10}{'CT':<10}{'TAT':<10}{'WT':<10}")
    print("-" * 65)

    while completed < n:
        idx = -1
        # Find highest priority (lowest number) among arrived processes
        best_priority = float('inf')
        
        for i in range(n):
            if not visited[i] and processes[i]['arrival'] <= current_time:
                if processes[i]['priority'] < best_priority:
                    best_priority = processes[i]['priority']
                    idx = i
                elif processes[i]['priority'] == best_priority:
                    # FCFS Tie-breaking if priorities are equal
                    if processes[i]['arrival'] < processes[idx]['arrival']:
                        idx = i
        
        if idx != -1:
            p = processes[idx]
            completion_time = current_time + p['burst']
            turnaround_time = completion_time - p['arrival']
            waiting_time = turnaround_time - p['burst']
            
            total_tat += turnaround_time
            total_wt += waiting_time
            
            print(f"{p['id']:<5}{p['arrival']:<10}{p['burst']:<10}{p['priority']:<10}{completion_time:<10}{turnaround_time:<10}{waiting_time:<10}")
            
            visited[idx] = True
            current_time = completion_time
            completed += 1
        else:
            current_time += 1

    print("-" * 65)
    print(f"Average TAT: {total_tat / n:.2f}")
    print(f"Average WT:  {total_wt / n:.2f}")

if __name__ == "__main__":
    print("--- Priority Scheduling (Non-Preemptive) ---")
    print("Note: Lower value = Higher Priority")
    
    data = [
        {'id': 'P1', 'arrival': 0, 'burst': 4, 'priority': 2},
        {'id': 'P2', 'arrival': 1, 'burst': 3, 'priority': 3},
        {'id': 'P3', 'arrival': 2, 'burst': 1, 'priority': 4},
        {'id': 'P4', 'arrival': 3, 'burst': 5, 'priority': 5},
        {'id': 'P5', 'arrival': 4, 'burst': 2, 'priority': 5},
    ]
    
    calculate_priority(data)
