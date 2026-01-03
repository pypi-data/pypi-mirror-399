"""
Page Replacement Algorithm: Optimal
-----------------------------------
Description:
Replaces the page that will not be used for the longest period of time in the future.
Impossible to implement in real-time (requires future knowledge), but used as benchmark.

Logic:
1. If page in memory: Hit.
2. If page not in memory: Miss.
   - If full: Look ahead in 'pages' to find which page in memory appears furthest in future (or never).
   - Replace that page.
"""

def calculate_optimal_paging(pages, capacity):
    memory = []
    page_faults = 0
    hits = 0
    
    print(f"Frame Capacity: {capacity}")
    print(f"{'Page':<5}{'Action':<10}{'Memory State'}")
    print("-" * 40)
    
    for i, page in enumerate(pages):
        if page in memory:
            action = "Hit"
            hits += 1
        else:
            action = "Fault"
            page_faults += 1
            if len(memory) < capacity:
                memory.append(page)
            else:
                # Find victim
                furthest_idx = -1
                victim_idx = -1
                
                for idx, mem_page in enumerate(memory):
                    # Check next occurrence
                    try:
                        # Slice from i+1 to end
                        next_use = pages[i+1:].index(mem_page)
                    except ValueError:
                        # Page never used again - best victim
                        next_use = float('inf')
                    
                    if next_use > furthest_idx:
                        furthest_idx = next_use
                        victim_idx = idx
                
                memory[victim_idx] = page
                
        print(f"{page:<5}{action:<10}{memory}")

    print("-" * 40)
    print(f"Total Page Faults: {page_faults}")
    print(f"Total Hits: {hits}")

if __name__ == "__main__":
    print("--- Optimal Page Replacement ---")
    
    pages = [7, 0, 1, 2, 0, 3, 0, 4, 2, 3, 0, 3, 2]
    capacity = 3
    
    calculate_optimal_paging(pages, capacity)
