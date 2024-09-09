#!/bin/bash

# Slurm job options (job-name, compute nodes, job time)
#SBATCH --job-name=uv_b3mpi
#SBATCH --time=24:00:00
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=32
#SBATCH --cpus-per-task=1

# 1 node 128 - OOM (OUT OF MEMORY)
# 1 node 64  - OK * best performance
# 1 node 32  - OK
# 4 node 32  - ?

# Replace [budget code] below with your budget code (e.g. t01)
#SBATCH --account=e05-react-smw
#SBATCH --partition=standard
#SBATCH --qos=standard

# Set the number of threads to 1
#   This prevents any threaded system libraries from automatically 
#   using threading.
export OMP_NUM_THREADS=1

# USE PYTHON
echo ' * shell loading py env'
#module load cray-python
#module load cray-mpich/8.1.23
#srun --mpi=list
source /work/e05/e05/wkjee/miniconda3/bin/activate
echo ' | shell loading py env - done'
# USE PYTHON
# e.g.,
# source /work/e05/e05/wkjee/miniconda3/bin/activate
# export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/work/e05/e05/wkjee/miniconda3/lib/
# USE PYTHON

# Pass cpus-per-task setting to srun
export SRUN_CPUS_PER_TASK=${SLURM_CPUS_PER_TASK}

# Launch the parallel job
#   Using 512 MPI processes and 128 MPI processes per node
#   srun picks up the distribution from the sbatch options

EXE=$PWD
#    /work/e05/e05/wkjee/Gold/soc_cube_estate/soc_evec/b3lyp_ex_states
echo ' | start dn channel'

#srun python ${EXE}/triple_mpi.py 1> mpi_triple.out 2> mpi_triple.err
#srun --ntasks-per-node=128 --cpus-per-task=1 --distribution=block:block --hint=nomultithread \
#		python ${EXE}/triple_mpi.py 1> mpi_triple.out 2> mpi_triple.err

#srun python ${EXE}/triple_mpi.py 1> mpi_triple.out 2> mpi_triple.err
#srun --mpi=pmix 

srun --mpi=pmi2 python ${EXE}/uv-vis_soc_analysis_mpi.py 1> uv_mpipy.out 2> uv_mpipy.err

echo ' | dn channel processing done'


# WKJEE 08.2024
#
# only successful case : 'srun --mpi=pmi2 python'

