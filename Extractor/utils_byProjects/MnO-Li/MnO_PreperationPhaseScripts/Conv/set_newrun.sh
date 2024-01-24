#!/bin/bash

rm -rf newrun
mkdir newrun
tardir=$(echo "summary_*")

cp ${tardir}/*gin ./newrun
cd newrun

	sed -i "s|conv|conp|" *.gin
	sed -i "s|maxcyc opt  1000000|maxcyc opt 500|" *.gin

cd ..
