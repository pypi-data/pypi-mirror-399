"""
Disk Scheduling Algorithm: C-SCAN (Circular SCAN)
-------------------------------------------------
Description:
Similar to SCAN, but only provides service in one direction.
When it reaches the end, it immediately returns to the beginning of the disk 
without servicing any requests on the return trip.

Logic:
1. Sort requests.
2. If direction is right:
   - Visit 'right' requests.
   - Go to End.
   - Jump to Start (0). (This jump distance is arguably not counted in Seek Time by some definitions, but usually is tracks traversed).
   - Visit 'left' requests.
"""

def calculate_disk_cscan(requests, head, disk_size=200):
    seek_count = 0
    current_pos = head
    
    left = [r for r in requests if r < head]
    right = [r for r in requests if r > head]
    
    left.sort()
    right.sort()
    
    sequence = [head]
    
    # Assume moving Right by default for C-SCAN usually
    # 1. service right
    for r in right:
        seek_count += abs(current_pos - r)
        current_pos = r
        sequence.append(r)
        
    # 2. move to max track
    seek_count += abs(current_pos - (disk_size - 1))
    current_pos = disk_size - 1
    sequence.append(current_pos)
    
    # 3. jump to 0 (circular)
    seek_count += abs(current_pos - 0)
    current_pos = 0
    sequence.append(current_pos)
    
    # 4. service left (which are now 'ahead' in the circle)
    for r in left:
        seek_count += abs(current_pos - r)
        current_pos = r
        sequence.append(r)
        
    print("Seek Sequence: ", " -> ".join(map(str, sequence)))
    print(f"Total Seek Operations: {seek_count}")

if __name__ == "__main__":
    print("--- C-SCAN Disk Scheduling ---")
    
    reqs = [82, 170, 43, 140, 24, 16, 190]
    initial_head = 50
    disk_size = 200

    calculate_disk_cscan(reqs, initial_head, disk_size)
