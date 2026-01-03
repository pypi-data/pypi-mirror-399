"""
Page Replacement Algorithm: FIFO (First-In, First-Out)
------------------------------------------------------
Description:
The simplest page replacement algorithm. The operating system keeps track 
of all pages in memory in a queue, with the oldest page at the front. 
When a page needs to be replaced, the page at the front of the queue is removed.

Logic:
1. Maintain a queue/list of size 'capacity'.
2. If page in memory: Hit.
3. If page not in memory:
   - If memory full: Remove first element (oldest).
   - Add new page to end.
   - Fault (Miss).
"""

def calculate_fifo_paging(pages, capacity):
    memory = []
    page_faults = 0
    hits = 0
    
    print(f"Frame Capacity: {capacity}")
    print(f"{'Page':<5}{'Action':<10}{'Memory State'}")
    print("-" * 40)
    
    for page in pages:
        if page in memory:
            action = "Hit"
            hits += 1
        else:
            action = "Fault"
            page_faults += 1
            if len(memory) >= capacity:
                memory.pop(0) # Remove first (oldest)
            memory.append(page)
            
        print(f"{page:<5}{action:<10}{memory}")

    print("-" * 40)
    print(f"Total Page Faults: {page_faults}")
    print(f"Total Hits: {hits}")
    print(f"Hit Ratio: {hits / len(pages):.2f}")

if __name__ == "__main__":
    print("--- FIFO Page Replacement ---")
    
    # Reference String
    pages = [7, 0, 1, 2, 0, 3, 0, 4, 2, 3, 0, 3, 2]
    capacity = 3
    
    calculate_fifo_paging(pages, capacity)
