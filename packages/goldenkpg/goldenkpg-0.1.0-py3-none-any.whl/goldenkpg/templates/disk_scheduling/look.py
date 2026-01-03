"""
Disk Scheduling Algorithm: LOOK
-------------------------------
Description:
Similar to SCAN (Elevator), but the arm only goes as far as the last request in each direction, 
then reverses direction immediately without going all the way to the end of the disk.

Logic:
1. Sort requests.
2. Filter requests into "left" (smaller than head) and "right" (larger than head).
3. If direction is "right" (up):
    - Serve all "right" requests in ascending order.
    - Reverse direction.
    - Serve all "left" requests in descending order.
4. Calculate total seek distance.
"""

def calculate_look(request_queue, head, direction="right"):
    seek_count = 0
    distance = 0
    cur_track = head
    
    left = []
    right = []
    
    # Separate tracks
    for track in request_queue:
        if track < head:
            left.append(track)
        if track > head:
            right.append(track)
            
    left.sort()
    right.sort()
    
    seek_sequence = []
    
    # Run the loop two times (one for right, one for left or vice versa)
    run_order = [right, left] if direction == "right" else [left, right]
    
    # For LOOK, we process the first batch, then reverse for the second batch
    
    # First Pass
    batch1 = run_order[0]
    if direction == "left":
        batch1.reverse() # Process left/downwards in descending order (e.g., 90 -> 80)
    
    for track in batch1:
        seek_sequence.append(track)
        distance = abs(track - cur_track)
        seek_count += distance
        cur_track = track
        
    # Second Pass (Reverse Direction)
    batch2 = run_order[1]
    if direction == "right": # Initially right, now going left (descending)
        batch2.reverse()
    # if initially left, second pass is right (ascending), which is default sort
        
    for track in batch2:
        seek_sequence.append(track)
        distance = abs(track - cur_track)
        seek_count += distance
        cur_track = track

    print(f"Seek Sequence: {seek_sequence}")
    print(f"Total Seek Operations: {seek_count}")

if __name__ == "__main__":
    print("--- LOOK Disk Scheduling ---")
    
    request_queue = [176, 79, 34, 60, 92, 11, 41, 114]
    head = 50
    direction = "right" 
    
    print(f"Requests: {request_queue}")
    print(f"Head: {head}, Direction: {direction}")
    
    calculate_look(request_queue, head, direction)
