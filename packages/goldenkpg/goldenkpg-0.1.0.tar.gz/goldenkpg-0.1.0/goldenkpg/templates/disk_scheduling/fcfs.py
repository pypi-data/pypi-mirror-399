"""
Disk Scheduling Algorithm: FCFS (First-Come, First-Served)
----------------------------------------------------------
Description:
The disk arm services requests in the order they arrive.
No optimization for seek time.

Logic:
1. Start from 'Head' position.
2. Visit requests sequentially.
3. Calculate seek distance = abs(current_track - pending_track).
"""

def calculate_disk_fcfs(requests, head):
    seek_count = 0
    distance = 0
    current_pos = head

    print(f"Seek Sequence: {head}", end='')

    for req in requests:
        current_distance = abs(req - current_pos)
        seek_count += current_distance
        current_pos = req
        print(f" -> {current_pos}", end='')

    print("\n")
    print(f"Total Seek Operations: {seek_count}")
    print(f"Average Seek Length: {seek_count / len(requests):.2f}")

if __name__ == "__main__":
    print("--- FCFS Disk Scheduling ---")
    
    # Example Requests sequence
    reqs = [82, 170, 43, 140, 24, 16, 190]
    initial_head = 50

    calculate_disk_fcfs(reqs, initial_head)
