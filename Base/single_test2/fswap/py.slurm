#!/bin/bash --login

#SBATCH --job-name=sgf
#SBATCH --nodes=4
#SBATCH --ntasks-per-node=128
#SBATCH --distribution=block:block
#SBATCH --hint=nomultithread
#SBATCH --time=00:20:00
#SBATCH --account=e05-gc-smw
#SBATCH --partition=standard
#SBATCH --qos=short

# Load the Python module
# module load cray-python

# If using a virtual environment
# module load fhiaims
export OMP_NUM_THREADS=1

#source /work/e05/e05/wkjee/miniconda3/bin/activate /work/e05/e05/wkjee/miniconda3/envs/pax/
# Run your Python progamme
# time python vvuq_run.py $SLURM_ARRAY_TASK_ID

srun --ntasks-per-node=128 --cpus-per-task=1 /work/y07/shared/apps/core/fhiaims/210716.3/bin/aims.mpi.x 1> FHIaims.out 2> FHIaims.err
