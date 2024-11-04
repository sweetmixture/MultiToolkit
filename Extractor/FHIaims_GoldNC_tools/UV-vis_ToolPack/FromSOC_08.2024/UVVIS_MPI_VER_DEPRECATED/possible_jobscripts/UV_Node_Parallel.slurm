#!/bin/bash

# Slurm job options (job-name, compute nodes, job time)
#SBATCH --job-name=uv_b3lyp
#SBATCH --time=48:00:00
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=128

# Replace [budget code] below with your budget code (e.g. t01)
#SBATCH --account=e05-react-smw
#SBATCH --partition=standard
#SBATCH --qos=long

# Set the number of threads to 1
#   This prevents any threaded system libraries from automatically 
#   using threading.
export OMP_NUM_THREADS=128

# USE PYTHON
echo ' * shell loading py env'
source /work/e05/e05/wkjee/miniconda3/bin/activate
echo ' | shell loading py env - done'
# USE PYTHON
# e.g.,
# source /work/e05/e05/wkjee/miniconda3/bin/activate
# export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/work/e05/e05/wkjee/miniconda3/lib/
# USE PYTHON

# Launch the parallel job
#   Using 512 MPI processes and 128 MPI processes per node
#   srun picks up the distribution from the sbatch options

EXE="/work/e05/e05/wkjee/Gold/soc_cube_estate/soc_evec/b3lyp_ex_states"
#    /work/e05/e05/wkjee/Gold/soc_cube_estate/soc_evec/b3lyp_ex_states
echo ' | start dn channel'
python ${EXE}/uv-vis_soc_analysis_p.py 1> simpleUV.p.out 2> simpleUV.p.err
#            /uv-vis_soc_analysis_p.py
echo ' | dn channel processing done'
