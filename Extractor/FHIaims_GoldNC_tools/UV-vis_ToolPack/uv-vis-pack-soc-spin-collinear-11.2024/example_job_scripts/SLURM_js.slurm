#!/bin/bash

# Slurm job options (job-name, compute nodes, job time)
#SBATCH --job-name=soc_b3lyp
#SBATCH --time=06:00:00
#SBATCH --nodes=4

# Replace [budget code] below with your budget code (e.g. t01)
#SBATCH --account=e05-react-smw
#SBATCH --partition=standard
#SBATCH --qos=standard

# Set the number of threads to 1
#   This prevents any threaded system libraries from automatically 
#   using threading.
export OMP_NUM_THREADS=1

# USE PYTHON
# source /work/e05/e05/wkjee/miniconda3/bin/activate
# export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/work/e05/e05/wkjee/miniconda3/lib/
# USE PYTHON

# Launch the parallel job
#   Using 512 MPI processes and 128 MPI processes per node
#   srun picks up the distribution from the sbatch options

EXE="/work/e05/e05/wkjee/Software/fhi-aims.240507.socfix/_build-gnu-exe/aims.240627.scalapack.mpi.x"
srun --ntasks-per-node=128 --cpus-per-task=1 --distribution=block:block --hint=nomultithread --exact ${EXE} 1> FHIaims.out 2> FHIaims.err

#mkdir result
#mv A* ./result

#mkdir log
#mv master.log ./log
#mv workgroup*.log ./log
