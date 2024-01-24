#!/bin/bash

# print(' * Err ... one of following inputs missed')
# print(' (1) pklfile\n
#         (2) csvfile\n
#         (3) target_pair : LiLi, LiTc, TcTc\n
#         (4) size')
#

pexe='/work/e05/e05/wkjee/Masters/Zirui2023/MnO/conpshell/rdf_pkl/averaging_pkl.py'

for((i=1;i<25;i++)); do

	echo "size ${i} LiLi ..."
	python ${pexe} rdf${i}.pkl nconp${i}.csv LiLi ${i}
	echo "size ${i} LiTc ..."
	python ${pexe} rdf${i}.pkl nconp${i}.csv LiTc ${i}
	echo "size ${i} TcTc ..."
	python ${pexe} rdf${i}.pkl nconp${i}.csv TcTc ${i}

done
