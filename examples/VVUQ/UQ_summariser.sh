#!/bin/bash

#
#  wkjee 07/23
#
#  looping vvuq fhiaims calculations - retreiving 
#    1. standard output
#    2. initial and final geometry
#    * only case if aims calculation finished successfully
#
#  MUST !
#  each VVUQ calculation must be stored in 'local_XX' directories
#  

root=$PWD
prefix_1="local_"

# some pre-settings
if [ -d "summary" ]; then
    :
else
    mkdir summary
fi
summary_path="${root}/summary"

# this could be modified for rerun
count=1

if [ -f "summary.log" ]; then
	:
else
	touch summary.log
fi

# this could be modified for rerun
# batch 2 : 238 - 301
# batch 3 : 302 - 364 : 12.09.2023
for ((i=1; i<=306; i++)); do

    # get inside the dir

    dir="local_"$i"/run__*"
	echo "* * * processing directory: local_$i" >> "${root}/summary.log"
    cd $dir"/runs"
    	# run_x
		for subdir in */; do
			if [ -d "$subdir" ]; then
				# echo "Processing directory: $subdir of local $i ------------------" >> "${root}/summary.log"
				# Add your desired actions for each directory here

				cd $subdir
						rm -rf core
						ifsuccess=$(python /work/e05/e05/wkjee/Software/Scripts/Python/Perovskite/utils/aims_ifsuccess.py > checker && tail -1 checker)
				
						if [ "$ifsuccess" = "True" ]; then

								wd=$PWD

								# rotate to standard format
								python /work/e05/e05/wkjee/Software/fhi-aims.221103/utilities/rotate_to_standard_orientation_ase.py geometry.in.next_step

								# collect / stdout / geo.in / geo.out
								aims_output="${count}_aims.out"
								aims_geoin="${count}_aims_init.in"
								aims_geoout="${count}_aims_final.in"
								aims_geoout_rotate="${count}_aims_final.in.rotate"

								ln -s "$PWD"/FHIaims.out "${summary_path}/${aims_output}"
								ln -s "$PWD"/geometry.in "${summary_path}/${aims_geoin}"
								ln -s "$PWD"/geometry.in.next_step "${summary_path}/${aims_geoout}"
								ln -s "$PWD"/geometry.in.rotate "${summary_path}/${aims_geoout_rotate}"

								echo $PWD "   count: " $count >> "${root}/summary.log"
								(( count++ ))
						fi	
				cd ..
			fi
		done
	cd $root
done
