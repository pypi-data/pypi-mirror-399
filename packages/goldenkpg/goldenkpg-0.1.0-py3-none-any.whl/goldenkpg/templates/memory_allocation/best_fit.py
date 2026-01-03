"""
Memory Allocation Algorithm: Best Fit
-------------------------------------
Description:
Allocates the smallest block that is large enough to satisfy the request. 
The idea is to leave the smallest left-over hole (minimize fragmentation).
Requires searching the entire list or a sorted list.

Logic:
1. Iterate through memory blocks.
2. Find the "best" block: smallest block where block_size >= process_size.
3. Assign process to that block.
"""

def calculate_best_fit(blocks, processes):
    allocation = [-1] * len(processes)
    available_blocks = list(blocks)
    
    print(f"Initial Blocks: {available_blocks}")
    print(f"Process Requests: {processes}")
    print("-" * 40)
    print(f"{'Process No.':<15}{'Process Size':<15}{'Block No.':<15}")
    
    for i in range(len(processes)):
        best_idx = -1
        
        for j in range(len(available_blocks)):
            if available_blocks[j] >= processes[i]:
                if best_idx == -1:
                    best_idx = j
                elif available_blocks[j] < available_blocks[best_idx]:
                    best_idx = j
        
        if best_idx != -1:
            allocation[i] = best_idx
            available_blocks[best_idx] -= processes[i]
            
        block_str = str(allocation[i] + 1) if allocation[i] != -1 else "Not Allocated"
        print(f"{i+1:<15}{processes[i]:<15}{block_str:<15}")
        
    print("-" * 40)
    print(f"Remaining Blocks: {available_blocks}")

if __name__ == "__main__":
    print("--- Best Fit Memory Allocation ---")
    
    blocks = [100, 500, 200, 300, 600]
    processes = [212, 417, 112, 426]
    
    calculate_best_fit(blocks, processes)
