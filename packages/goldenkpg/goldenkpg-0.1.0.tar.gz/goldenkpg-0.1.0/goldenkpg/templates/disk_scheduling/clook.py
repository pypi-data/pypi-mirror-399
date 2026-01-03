"""
Disk Scheduling Algorithm: C-LOOK (Circular LOOK)
-------------------------------------------------
Description:
Enhanced version of LOOK. The arm only goes as far as the last request in each direction.
However, when reversing, it jumps immediately to the other end's furthest request without serving any requests in between,
creating a "circular" list effect. It basically treats the cylinder as a circular list.

Logic:
1. Sort requests.
2. Filter requests into "left" and "right".
3. If direction is "right" (up):
    - Serve all "right" requests in ascending order.
    - Jump to the lowest "left" request (start of the list).
    - Serve "left" requests in ascending order.
"""

def calculate_clook(request_queue, head, direction="right"):
    seek_count = 0
    distance = 0
    cur_track = head
    
    left = []
    right = []
    
    for track in request_queue:
        if track < head:
            left.append(track)
        if track > head:
            right.append(track)
            
    left.sort()
    right.sort()
    
    seek_sequence = []
    
    # Implementation for Right/Up direction
    if direction == "right":
        # Process all to the right
        for track in right:
            seek_sequence.append(track)
            distance = abs(track - cur_track)
            seek_count += distance
            cur_track = track
            
        # Jump to lowest track in left (First request of list)
        if left:
            seek_sequence.append(left[0])
            distance = abs(left[0] - cur_track)
            seek_count += distance
            cur_track = left[0]
            
            # Continue processing left list from there
            for i in range(1, len(left)):
                track = left[i]
                seek_sequence.append(track)
                distance = abs(track - cur_track)
                seek_count += distance
                cur_track = track
                
    elif direction == "left":
        # Process all to the left (descending)
        left.reverse()
        for track in left:
            seek_sequence.append(track)
            distance = abs(track - cur_track)
            seek_count += distance
            cur_track = track
            
        # Jump to highest track in right (Last request of list)
        if right:
            # right is sorted ascending, so last element is max
            highest_right = right[-1]
            seek_sequence.append(highest_right)
            distance = abs(highest_right - cur_track)
            seek_count += distance
            cur_track = highest_right

            # Continue descending processing of right list
            # We want to go from highest to lowest in right list now
            right.reverse()
            # Start from 2nd index (since we are already at right[0] which was old right[-1])
            for i in range(1, len(right)):
                track = right[i]
                seek_sequence.append(track)
                distance = abs(track - cur_track)
                seek_count += distance
                cur_track = track

    print(f"Seek Sequence: {seek_sequence}")
    print(f"Total Seek Operations: {seek_count}")

if __name__ == "__main__":
    print("--- C-LOOK Disk Scheduling ---")
    
    request_queue = [176, 79, 34, 60, 92, 11, 41, 114]
    head = 50
    direction = "right"
    
    print(f"Requests: {request_queue}")
    print(f"Head: {head}, Direction: {direction}")
    
    calculate_clook(request_queue, head, direction)
