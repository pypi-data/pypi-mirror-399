"""
Disk Scheduling Algorithm: SSTF (Shortest Seek Time First)
----------------------------------------------------------
Description:
Selects the request with the minimum seek time from the current head position.
Greedy algorithm. May cause starvation.

Logic:
1. From current head, find the request with min distance in the list of unserviced requests.
2. Move head to that request.
3. Repeat.
"""

def calculate_disk_sstf(requests, head):
    # Work on a copy
    pending = requests.copy()
    seek_count = 0
    current_pos = head
    
    print(f"Seek Sequence: {head}", end='')
    
    while pending:
        # Find nearest
        nearest_idx = -1
        min_dist = float('inf')
        
        for i, req in enumerate(pending):
            dist = abs(req - current_pos)
            if dist < min_dist:
                min_dist = dist
                nearest_idx = i
        
        # Service request
        target = pending.pop(nearest_idx)
        seek_count += min_dist
        current_pos = target
        
        print(f" -> {current_pos}", end='')

    print("\n")
    print(f"Total Seek Operations: {seek_count}")

if __name__ == "__main__":
    print("--- SSTF Disk Scheduling ---")
    
    reqs = [82, 170, 43, 140, 24, 16, 190]
    initial_head = 50

    calculate_disk_sstf(reqs, initial_head)
