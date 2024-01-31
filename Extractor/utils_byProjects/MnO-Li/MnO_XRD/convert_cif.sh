#!/bin/bash

for ((i=1; i<23; i++)); do

	cd 'li'${i}
		
		echo " ------ on shell executing rdf summariser"
		echo " working dir: " $PWD
		python /work/e05/e05/wkjee/Masters/Zirui2023/MnO/conpshell/parallel_gulp_cif_convert.py
	cd ..
done
