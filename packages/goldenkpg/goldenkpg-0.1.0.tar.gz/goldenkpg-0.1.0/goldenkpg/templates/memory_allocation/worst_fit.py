"""
Memory Allocation Algorithm: Worst Fit
--------------------------------------
Description:
Allocates the largest available block. 
The idea is that the remaining hole will be large enough to be useful for another process.

Logic:
1. Iterate through memory blocks.
2. Find the "worst" block: largest block where block_size >= process_size.
3. Assign process to that block.
"""

def calculate_worst_fit(blocks, processes):
    allocation = [-1] * len(processes)
    available_blocks = list(blocks)
    
    print(f"Initial Blocks: {available_blocks}")
    print(f"Process Requests: {processes}")
    print("-" * 40)
    print(f"{'Process No.':<15}{'Process Size':<15}{'Block No.':<15}")
    
    for i in range(len(processes)):
        worst_idx = -1
        
        for j in range(len(available_blocks)):
            if available_blocks[j] >= processes[i]:
                if worst_idx == -1:
                    worst_idx = j
                elif available_blocks[j] > available_blocks[worst_idx]:
                    worst_idx = j
        
        if worst_idx != -1:
            allocation[i] = worst_idx
            available_blocks[worst_idx] -= processes[i]
            
        block_str = str(allocation[i] + 1) if allocation[i] != -1 else "Not Allocated"
        print(f"{i+1:<15}{processes[i]:<15}{block_str:<15}")
        
    print("-" * 40)
    print(f"Remaining Blocks: {available_blocks}")

if __name__ == "__main__":
    print("--- Worst Fit Memory Allocation ---")
    
    blocks = [100, 500, 200, 300, 600]
    processes = [212, 417, 112, 426]
    
    calculate_worst_fit(blocks, processes)
