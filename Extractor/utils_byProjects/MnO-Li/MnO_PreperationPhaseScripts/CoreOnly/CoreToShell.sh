#!/bin/bash

sta=0
max=9424
size=24

header_lim=10	# header + cell info
root="${PWD}"
headerFile="/work/e05/e05/wkjee/Masters/Zirui2023/MnO/coreOnly/new_header"
footerFile="/work/e05/e05/wkjee/Masters/Zirui2023/MnO/coreOnly/new_footer"

# n = 1		| 73
# n = 2		| 74
# ..
# n = 7		| 79
# ..
# n = 12	| 84

Natoms=$(echo "${size} + 72" | bc)
headN=$(echo "${Natoms} + ${header_lim}" | bc)

rm -rf newrun
mkdir  newrun

for(( i=${sta}; i<=${max}; i++ )); do

	rm -f geometry
	target_input="${root}/summary_li${size}/A${i}.gin"
	head -"${headN}" ${target_input} | tail -"${Natoms}" > geometry

	#sed -i "s|O     core|O     shel|" geometry
	#sed -i "s|Tc    core|Tc    shel|" geometry

	cat ${headerFile} >> ${root}/newrun/A${i}.gin
	cat geometry      >> ${root}/newrun/A${i}.gin
	cat ${footerFile} >> ${root}/newrun/A${i}.gin

	echo "progressing ... ${i}" >> newrun.log

done

mv newrun.log ${root}/newrun

# cleaning ...
rm -f geometry
