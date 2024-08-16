#!/bin/bash

# Slurm job options (job-name, compute nodes, job time)
#SBATCH --job-name=mpipy-t
#SBATCH --time=00:20:00
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=128
#SBATCH --cpus-per-task=1

# Replace [budget code] below with your budget code (e.g. t01)
#SBATCH --account=e05-react-smw
#SBATCH --partition=standard
#SBATCH --qos=short

# Set the number of threads to 1
#   This prevents any threaded system libraries from automatically 
#   using threading.
export OMP_NUM_THREADS=1

# USE PYTHON
echo ' * shell loading py env'
source /work/e05/e05/wkjee/miniconda3/bin/activate
ldd /work/e05/e05/wkjee/miniconda3/bin/mpirun
echo ' | shell loading py env - done'
# USE PYTHON
# e.g.,
# source /work/e05/e05/wkjee/miniconda3/bin/activate
# export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/work/e05/e05/wkjee/miniconda3/lib/
# USE PYTHON

# Launch the parallel job
#   Using 512 MPI processes and 128 MPI processes per node
#   srun picks up the distribution from the sbatch options

EXE="/work/e05/e05/wkjee/Software/MultiToolkit/Extractor/FHIaims_GoldNC_tools/UV-vis_ToolPack/FromSOC_08.2024/ThreadingRef/mpi4py"
MPIRUN="/work/e05/e05/wkjee/miniconda3/bin/mpirun"
#    /work/e05/e05/wkjee/Gold/soc_cube_estate/soc_evec/b3lyp_ex_states
echo ' | start dn channel'

#srun python ${EXE}/triple_mpi.py 1> mpi_triple.out 2> mpi_triple.err
#srun --ntasks-per-node=128 --cpus-per-task=1 --distribution=block:block --hint=nomultithread \
#		python ${EXE}/triple_mpi.py 1> mpi_triple.out 2> mpi_triple.err

${MPIRUN} -np 128 ${EXE}/triple_mpi.py 1> mpi_triple.out 2> mpi_triple.err
#            /uv-vis_soc_analysis_p.py
echo ' | dn channel processing done'


# WKJEE 08.2024
#
# using 'mpirun -np xxx python xxx.py --> permission denied on ARCHER2 compute node
# 											only available on the head nodes
