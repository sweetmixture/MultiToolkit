#!/bin/bash

for ((i=0; i<25; i++)); do

	cd 'li'${i}
		
		echo " ------ on shell executing rdf summariser"
		echo " working dir: " $PWD
		python /work/e05/e05/wkjee/Masters/Zirui2023/MnO/conpshell/get_rdf_batch.py ${i} -parallel
	cd ..
done
