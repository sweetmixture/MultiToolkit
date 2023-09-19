#!/bin/bash
#SBATCH --job-name "gulp"
#SBATCH --output "gulp.o"
#SBATCH --nodes 1
#SBATCH --ntasks-per-node 1
#SBATCH --cpus-per-task 1
#SBATCH --hint nomultithread
#SBATCH --export NONE

set -e

module load gulp/gcc8/5.2
ulimit -c 0 # disable core files

gulp-serial < "$1" > "$1".got
