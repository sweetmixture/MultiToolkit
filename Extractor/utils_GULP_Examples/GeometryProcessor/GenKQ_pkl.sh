#!/bin/bash

for ((i = 1; i< 25; i++)); do
	
	cd "li${i}"
	echo $PWD

	python KQ_RIMconv_DBgen.py ${i}
	mv "config_size_${i}.pkl" ./../config_RIM_conv
	cd ..

done
