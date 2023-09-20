#!/bin/bash
#SBATCH --job-name "3.config.gulp"
#SBATCH --output "3.config.gulp.o"
#SBATCH --nodes 1
#SBATCH --ntasks-per-node 1
#SBATCH --cpus-per-task 1
#SBATCH --hint nomultithread
#SBATCH --export NONE

set -e

module load gulp/gcc8/5.2
ulimit -c 0 # disable core files

gulp-serial < "3.config.gulp" > "3.config.gulp.got"

