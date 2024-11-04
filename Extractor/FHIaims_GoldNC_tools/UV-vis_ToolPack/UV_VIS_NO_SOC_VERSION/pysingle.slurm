#!/bin/bash

# Slurm job options (job-name, compute nodes, job time)
#SBATCH --job-name=pbefup
#SBATCH --time=24:00:00
#SBATCH --ntasks=1

# Replace [budget code] below with your budget code (e.g. t01)
#SBATCH --account=e05-power-smw
#SBATCH --partition=serial
#SBATCH --qos=serial
#SBATCH --mem=8G

# Set the number of threads to 1
#   This prevents any threaded system libraries from automatically 
#   using threading.
export OMP_NUM_THREADS=1

echo ' * shell loading py env'
source /work/e05/e05/wkjee/miniconda3/bin/activate
echo ' | shell loading py env - done'
# Launch the parallel job
#   Using 512 MPI processes and 128 MPI processes per node
#   srun picks up the distribution from the sbatch options

#
# preparation
#
#python mos_analyser_2.py -spin 1> mos_analyser_2.out 2> mos_analyser_2.err

#echo ' | start up channel'
#python get_transitions_data_up.py   1> simpleUV.up.out 2> simpleUV.up.err
#echo ' | up channel processing done'

echo ' | start dn channel'
python get_transitions_data_down.py 1> simpleUV.dn.out 2> simpleUV.dn.err
echo ' | dn channel processing done'

#get_transitions_data_up.py
#get_transitions_data_down.py
