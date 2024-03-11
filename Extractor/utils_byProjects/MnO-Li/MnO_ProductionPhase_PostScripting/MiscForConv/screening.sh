#!/bin/bash

count=0

sta=0
end=18954
tol=0.00005


rm -rf summary
mkdir summary

for(( i=${sta}; i<=${end}; i++ )); do

	gulp_output="A${i}"/gulp_klmc.gout
	gulp_dump="A${i}"/gulp.res
	#gulp_cif="A${i}"/cryst.cif

	gnorm=$(grep "Final Gnorm  =       " ${gulp_output} | awk '{print $4}')

	echo $i $count $gnorm 

	compare_results=$(echo "${gnorm} < ${tol}" | bc )
	if [ ${compare_results} -eq 1 ]; then
		#cp "${gulp_output}" summary/"A${count}.gout"
    	cp "${gulp_dump}" summary/"A${count}.gin"
		#cp "${gulp_cif}" summary/"crystA${count}.cif"
		(( count++ ))
	fi


done
