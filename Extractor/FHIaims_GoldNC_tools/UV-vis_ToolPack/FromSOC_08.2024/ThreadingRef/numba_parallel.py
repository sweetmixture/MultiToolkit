from numba import njit, prange
import numpy as np
import time

@njit(parallel=True)
def triple_nested_loop(n, m, p):
	result = np.zeros((n, m, p))
	
	for i in prange(n):
		for j in range(m):
			for k in range(p):
				result[i, j, k] = i + j + k
	
	return result

# Define dimensions
n, m, p = 100, 100, 100

# Measure start time
start_time = time.time()

# Call the function
output = triple_nested_loop(n, m, p)
# Measure end time
end_time = time.time()
# Calculate elapsed time
elapsed_time = end_time - start_time

# Print elapsed time
print(f"Computation completed in {elapsed_time:.4f} seconds.")

