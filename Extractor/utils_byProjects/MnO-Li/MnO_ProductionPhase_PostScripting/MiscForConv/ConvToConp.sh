#!/bin/bash

sta=0
size=$1			# taking input - size
max=$2			# max configuration

root="${PWD}"
footerFile="/work/e05/e05/wkjee/Masters/Zirui2023/MnO/shelOnly/new_footer"

# line limit for keywords and geometries
# kg=$(grep -n "total" A1234.gin | cut -c1-3)

rm -rf newrun geometry
mkdir  newrun

for(( i=${sta}; i<=${max}; i++ )); do

	target_input="${root}/summary_li${size}/A${i}.gin"

	kg=$(grep -n "total" ${target_input} | cut -c1-3)			# 'kg' line limit for keywords and geometries
	if [ -z "$kg" ]; then
		kg=$(grep -n "species" ${target_input} | cut -c1-3)           # 'kg' line limit for keywords and geometries
		kg=$( echo "${kg} - 1" | bc )
	fi

	head -n"${kg}" ${target_input} > geometry

	sed -i "s|conv|conp|" geometry

	cat geometry      >> ${root}/newrun/A${i}.gin
	cat ${footerFile} >> ${root}/newrun/A${i}.gin

	echo "progressing ... ${i}" >> newrun.log

done

mv newrun.log ${root}/newrun

# cleaning ...
rm -f geometry
