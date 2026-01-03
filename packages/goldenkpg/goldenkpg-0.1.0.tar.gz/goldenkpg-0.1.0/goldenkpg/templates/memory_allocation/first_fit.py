"""
Memory Allocation Algorithm: First Fit
--------------------------------------
Description:
Allocates the first block (hole) that is large enough to satisfy the request. 
Search starts from the beginning of the free block list.

Logic:
1. Iterate through memory blocks for each process.
2. Assign the process to the first block where block_size >= process_size.
3. Reduce block size by process size (internal fragmentation model for simplicity, or mark 'block' as used).
"""

def calculate_first_fit(blocks, processes):
    # blocks: list of available memory block sizes
    # processes: list of required memory for each process
    
    allocation = [-1] * len(processes)
    # Work on a copy of blocks to persist changes
    available_blocks = list(blocks)
    
    print(f"Initial Blocks: {available_blocks}")
    print(f"Process Requests: {processes}")
    print("-" * 40)
    print(f"{'Process No.':<15}{'Process Size':<15}{'Block No.':<15}")
    
    for i in range(len(processes)):
        allocated = False
        for j in range(len(available_blocks)):
            if available_blocks[j] >= processes[i]:
                allocation[i] = j
                available_blocks[j] -= processes[i]
                allocated = True
                break
        
        block_str = str(allocation[i] + 1) if allocation[i] != -1 else "Not Allocated"
        print(f"{i+1:<15}{processes[i]:<15}{block_str:<15}")
        
    print("-" * 40)
    print(f"Remaining Blocks: {available_blocks}")

if __name__ == "__main__":
    print("--- First Fit Memory Allocation ---")
    
    # Block sizes in generic units
    blocks = [100, 500, 200, 300, 600]
    # Process memory requirements
    processes = [212, 417, 112, 426]
    
    calculate_first_fit(blocks, processes)
