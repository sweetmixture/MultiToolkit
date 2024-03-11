#!/bin/bash
#
# 03.2024 W.JEE
# KLMC Solid Soultion
# filter to collect low gnorm structures
#
#   file names used below may change depending on user's choice
#
#   variables    | file_name    | description
#   $gulp_output : gulp_klmc.out  (standard gulp output)
#   $gulp_dump   : gulp.res       (standard gulp dump) 
#   $gulp_cif    : cryst.cif      (standard gulp cif)
#
#   # save $gulp_dump as $A{tag}.gin
#
count=0

# USER DEFINE ----
sta=0					# STARTING STRUCTURE NO.
end=19999				# ENDING   STRUCTURE NO.
tol=0.00005				# GNORM    TOLERANCE (eV/Angs)
# USEF DEFINE ----

rm -rf summary
mkdir summary			# SAVE RESULT TO 'summary' directory

for(( i=${sta}; i<=${end}; i++ )); do

	# USER DEFINE ----
	gulp_output="A${i}"/gulp_klmc.gout
	gulp_dump="A${i}"/gulp.res
	gulp_cif="A${i}"/cryst.cif
	# USER DEFINE ----

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
