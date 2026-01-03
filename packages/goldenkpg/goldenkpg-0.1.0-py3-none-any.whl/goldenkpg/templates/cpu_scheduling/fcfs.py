"""
CPU Scheduling Algorithm: FCFS (First-Come, First-Served)
---------------------------------------------------------
Description:
The simplest CPU scheduling algorithm. Processes are executed in the order 
they arrive in the ready queue. Implementation uses a simple FIFO queue logic.

Metrics calculated:
- Completion Time (CT)
- Turnaround Time (TAT) = CT - Arrival Time
- Waiting Time (WT) = TAT - Burst Time
"""

def calculate_fcfs(processes):
    """
    Calculates FCFS scheduling metrics.
    
    Args:
        processes: List of dicts, where each dict has 'id', 'arrival', 'burst'.
                   Assumes the list is SORTED by arrival time.
    """
    current_time = 0
    results = []
    
    print(f"\n{'PID':<5}{'Arrival':<10}{'Burst':<10}{'CT':<10}{'TAT':<10}{'WT':<10}")
    print("-" * 55)

    total_tat = 0
    total_wt = 0

    for p in processes:
        arrival = p['arrival']
        burst = p['burst']
        pid = p['id']

        # If CPU is idle before process arrives
        if current_time < arrival:
            current_time = arrival
        
        # Process runs
        completion_time = current_time + burst
        turnaround_time = completion_time - arrival
        waiting_time = turnaround_time - burst
        
        # Update system time
        current_time = completion_time

        # Store calculation
        results.append({
            'id': pid,
            'ct': completion_time,
            'tat': turnaround_time,
            'wt': waiting_time
        })
        
        total_tat += turnaround_time
        total_wt += waiting_time

        print(f"{pid:<5}{arrival:<10}{burst:<10}{completion_time:<10}{turnaround_time:<10}{waiting_time:<10}")

    n = len(processes)
    print("-" * 55)
    print(f"Average TAT: {total_tat / n:.2f}")
    print(f"Average WT:  {total_wt / n:.2f}")
    
    return results

if __name__ == "__main__":
    print("--- FCFS CPU Scheduling ---")
    
    # Example Input: List of processes [ID, Arrival Time, Burst Time]
    # You can modify this or take user input
    data = [
        {'id': 'P1', 'arrival': 0, 'burst': 4},
        {'id': 'P2', 'arrival': 1, 'burst': 3},
        {'id': 'P3', 'arrival': 2, 'burst': 1},
        {'id': 'P4', 'arrival': 5, 'burst': 2},
    ]

    # FCFS requires sorting by arrival time primarily
    data.sort(key=lambda x: x['arrival'])
    
    calculate_fcfs(data)
