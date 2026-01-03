"""
Disk Scheduling Algorithm: SCAN (Elevator Algorithm)
----------------------------------------------------
Description:
The disk arm starts at one end of the disk and moves toward the other end, 
servicing requests as it reaches each cylindrical position, until it gets 
to the other end of the disk, where the head movement is reversed.

Logic:
1. Sort requests.
2. Filter requests into "left of head" and "right of head".
3. If direction is right (high values):
   - Visit all 'right' requests sorted ascending.
   - Go to disk end (MAX_TRACK) if needed (usually YES).
   - Reverse and visit 'left' requests sorted descending.
"""

def calculate_disk_scan(requests, head, direction='right', disk_size=200):
    seek_count = 0
    current_pos = head
    
    # Include bounds if necessary, or just track seek
    left = [r for r in requests if r < head]
    right = [r for r in requests if r > head]
    
    # Sort
    left.sort()
    right.sort()
    
    sequence = [head]
    
    # Run scan
    if direction == 'right':
        # Move right
        for r in right:
            seek_count += abs(current_pos - r)
            current_pos = r
            sequence.append(r)
        
        # Go to end (disk_size - 1)
        # Note: SCAN usually goes to the specific end
        seek_count += abs(current_pos - (disk_size - 1))
        current_pos = disk_size - 1
        sequence.append(current_pos)
        
        # Reverse to left
        for r in reversed(left):
            seek_count += abs(current_pos - r)
            current_pos = r
            sequence.append(r)
            
    elif direction == 'left':
        # Move left
        for r in reversed(left):
            seek_count += abs(current_pos - r)
            current_pos = r
            sequence.append(r)
            
        # Go to 0
        seek_count += abs(current_pos - 0)
        current_pos = 0
        sequence.append(current_pos)
        
        # Reverse to right
        for r in right:
            seek_count += abs(current_pos - r)
            current_pos = r
            sequence.append(r)

    print("Seek Sequence: ", " -> ".join(map(str, sequence)))
    print(f"Total Seek Operations: {seek_count}")

if __name__ == "__main__":
    print("--- SCAN Disk Scheduling ---")
    
    reqs = [82, 170, 43, 140, 24, 16, 190]
    initial_head = 50
    disk_size = 200
    direction = 'right' # or 'left'

    calculate_disk_scan(reqs, initial_head, direction, disk_size)
