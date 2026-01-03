"""
Page Replacement Algorithm: Clock (Second Chance)
-------------------------------------------------
Description:
Approximation of LRU. Uses a circular buffer and a 'use bit' (reference bit).
If 'use bit' is 0, replace. If 1, set to 0 and move hand to next.

Logic:
1. Pointer 'hand' iterates memory.
2. If page match: Hit, set use_bit = 1.
3. If miss:
   - While use_bit[hand] == 1:
       use_bit[hand] = 0
       hand = (hand + 1) % capacity
   - Replace page at 'hand'.
   - use_bit[hand] = 1 (new page gets second chance initially? Usually yes, or 0? 1 implies recently used).
   - hand = (hand + 1) % capacity
"""

def calculate_clock_paging(pages, capacity):
    memory = [None] * capacity
    use_bit = [0] * capacity
    hand = 0
    
    page_faults = 0
    hits = 0
    
    # We maintain memory as fixed size array to simulate frames properly with indices
    
    print(f"Frame Capacity: {capacity}")
    print(f"{'Page':<5}{'Action':<10}{'Memory':<20}{'Bits'}")
    print("-" * 50)
    
    for page in pages:
        # Check if in memory
        found = False
        for i in range(capacity):
            if memory[i] == page:
                found = True
                use_bit[i] = 1 # Set reference bit
                action = "Hit"
                hits += 1
                break
        
        if not found:
            action = "Fault"
            page_faults += 1
            
            # Find victim
            while True:
                if memory[hand] is None:
                    # Empty slot
                    memory[hand] = page
                    use_bit[hand] = 1
                    hand = (hand + 1) % capacity
                    break
                
                if use_bit[hand] == 1:
                    use_bit[hand] = 0
                    hand = (hand + 1) % capacity
                else:
                    # Found victim (bit 0)
                    memory[hand] = page
                    use_bit[hand] = 1
                    hand = (hand + 1) % capacity
                    break
                    
        print(f"{page:<5}{action:<10}{str(memory):<20}{use_bit}")

    print("-" * 50)
    print(f"Total Page Faults: {page_faults}")
    print(f"Total Hits: {hits}")

if __name__ == "__main__":
    print("--- Clock (Second Chance) Page Replacement ---")
    
    pages = [0, 4, 1, 4, 2, 4, 3, 4, 2, 4, 0, 4, 1, 4, 2, 4, 3, 4]
    capacity = 3
    
    calculate_clock_paging(pages, capacity)
