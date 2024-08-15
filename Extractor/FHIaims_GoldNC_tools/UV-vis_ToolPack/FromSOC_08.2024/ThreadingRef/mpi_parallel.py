from mpi4py import MPI
import numpy as np

def compute_result(i, j):
    # Example computation, replace with your actual logic
    return i + j

def main():
    comm = MPI.COMM_WORLD
    rank = comm.Get_rank()
    size = comm.Get_size()

    # Example dimensions
    outer_dim = 10
    inner_dim = 20

    # Compute the number of iterations each process will handle
    outer_indices = np.arange(outer_dim)
    
    # Distribute outer indices to processes in a round-robin fashion
    outer_indices_split = np.array_split(outer_indices, size)
    
    # Get the portion of indices for this process
    local_indices = outer_indices_split[rank]
    
    # Initialize a local accumulator for results
    local_accumulator = np.zeros(inner_dim, dtype=np.float64)

    # Compute the local part of the result and accumulate
    for i in local_indices:
        for j in range(inner_dim):
            local_accumulator[j] += compute_result(i, j)

    # Gather accumulated results from all processes
    global_accumulator = np.zeros(inner_dim, dtype=np.float64)

    comm.Reduce(local_accumulator, global_accumulator, op=MPI.SUM, root=0)

    if rank == 0:
        print("Accumulated Results:")
        print(global_accumulator)

if __name__ == "__main__":
    main()

