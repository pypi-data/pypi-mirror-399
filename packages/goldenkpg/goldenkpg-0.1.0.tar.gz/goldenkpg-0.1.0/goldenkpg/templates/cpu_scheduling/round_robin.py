"""
CPU Scheduling Algorithm: Round Robin (RR)
------------------------------------------
Description:
Preemptive algorithm where each process is assigned a fixed time quantum.
Designed for time-sharing systems.

Logic:
1. Maintain a FIFO Ready Queue.
2. Run process for 'Time Quantum' or 'Rem Burst' (whichever is smaller).
3. If process unfinished, add back to end of queue.
"""

def calculate_round_robin(processes, time_quantum):
    n = len(processes)
    # Store remaining burst time
    remaining_burst = [p['burst'] for p in processes]
    # To track if process is in queue, etc. simpler to simulate queue
    
    # We'll use a manual simulation with a time variable
    current_time = 0
    completed = 0
    
    # Ready queue will store INDICES of processes
    queue = []
    
    # Sort by arrival initially to push first processes
    # But we need to keep original indices for remaining_burst access
    # So let's create a list of (arrival, index)
    arrivals = [(processes[i]['arrival'], i) for i in range(n)]
    arrivals.sort()
    
    # Pointers
    arrival_ptr = 0
    
    # Push initial process(es)
    if arrivals[0][0] > 0:
        current_time = arrivals[0][0]
    
    # Add all processes that arrive at current_time (or start)
    while arrival_ptr < n and arrivals[arrival_ptr][0] <= current_time:
        queue.append(arrivals[arrival_ptr][1])
        arrival_ptr += 1
        
    tat = [0] * n
    wt = [0] * n
    ct = [0] * n
    
    print(f"\nTime Quantum: {time_quantum}")
    print(f"Processing Order (Log): ")

    while completed < n:
        if not queue:
            # If queue empty but processes left, jump time
            if arrival_ptr < n:
                current_time = arrivals[arrival_ptr][0]
                while arrival_ptr < n and arrivals[arrival_ptr][0] <= current_time:
                    queue.append(arrivals[arrival_ptr][1])
                    arrival_ptr += 1
            else:
                break # Should not happen if completed < n
        
        idx = queue.pop(0)
        
        # Execute
        exec_time = min(time_quantum, remaining_burst[idx])
        remaining_burst[idx] -= exec_time
        current_time += exec_time
        
        print(f"  -> P{processes[idx]['id']} (runs {exec_time}s, left {remaining_burst[idx]}s) at T={current_time}")
        
        # Check for new arrivals during this execution
        while arrival_ptr < n and arrivals[arrival_ptr][0] <= current_time:
            queue.append(arrivals[arrival_ptr][1])
            arrival_ptr += 1
            
        # If not finished, re-queue
        if remaining_burst[idx] > 0:
            queue.append(idx)
        else:
            # Completed
            completed += 1
            ct[idx] = current_time
            tat[idx] = ct[idx] - processes[idx]['arrival']
            wt[idx] = tat[idx] - processes[idx]['burst']

    # Print Summary
    print("\nFinal Metrics:")
    print(f"{'PID':<5}{'Arrival':<10}{'Burst':<10}{'CT':<10}{'TAT':<10}{'WT':<10}")
    print("-" * 55)
    
    total_tat = sum(tat)
    total_wt = sum(wt)
    
    for i in range(n):
        p = processes[i]
        print(f"{p['id']:<5}{p['arrival']:<10}{p['burst']:<10}{ct[i]:<10}{tat[i]:<10}{wt[i]:<10}")
        
    print("-" * 55)
    print(f"Average TAT: {total_tat / n:.2f}")
    print(f"Average WT:  {total_wt / n:.2f}")

if __name__ == "__main__":
    print("--- Round Robin Scheduling ---")
    
    data = [
        {'id': 1, 'arrival': 0, 'burst': 5},
        {'id': 2, 'arrival': 1, 'burst': 4},
        {'id': 3, 'arrival': 2, 'burst': 2},
        {'id': 4, 'arrival': 3, 'burst': 1},
    ]
    
    tq = 2
    calculate_round_robin(data, tq)
