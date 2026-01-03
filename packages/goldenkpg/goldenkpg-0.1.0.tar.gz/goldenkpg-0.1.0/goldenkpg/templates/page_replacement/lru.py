"""
Page Replacement Algorithm: LRU (Least Recently Used)
-----------------------------------------------------
Description:
Replaces the page that has not been used for the longest period of time.
Good approximation of optimal algorithm.

Logic:
1. If page in memory: Hit. Move page to 'most recent' position (end of list).
2. If page not in memory: Miss.
   - If full: Remove 'least recent' (first element).
   - Add new page to 'most recent' (end).
"""

def calculate_lru_paging(pages, capacity):
    memory = [] # Using list as ordered structure: [Least Recent ... Most Recent]
    page_faults = 0
    hits = 0
    
    print(f"Frame Capacity: {capacity}")
    print(f"{'Page':<5}{'Action':<10}{'Memory State'}")
    print("-" * 40)
    
    for page in pages:
        if page in memory:
            action = "Hit"
            hits += 1
            # Update usage: remove and re-add to end
            memory.remove(page)
            memory.append(page)
        else:
            action = "Fault"
            page_faults += 1
            if len(memory) >= capacity:
                memory.pop(0) # Remove lru (first)
            memory.append(page)
            
        print(f"{page:<5}{action:<10}{memory}")

    print("-" * 40)
    print(f"Total Page Faults: {page_faults}")
    print(f"Total Hits: {hits}")

if __name__ == "__main__":
    print("--- LRU Page Replacement ---")
    
    pages = [7, 0, 1, 2, 0, 3, 0, 4, 2, 3, 0, 3, 2]
    capacity = 3
    
    calculate_lru_paging(pages, capacity)
