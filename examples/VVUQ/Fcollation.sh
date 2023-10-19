#!/bin/bash

# USER ========
max=2
# USER ========


analysis_x="/work/e05/e05/wkjee/Software/MultiToolkit/examples/Fcollation_VVUQ_FHIaims_Perovskite.py"

echo -n "energy,homo,lumo,homolumo," >> result.txt
echo -n "a,b,c,al,be,ga,v,"	>> result.txt
echo -n "ba1,ba2,ba3,ba4,bb1,bb2,bb3,bb4,bc1,bc2,bc3,bc4," >> result.txt
echo -n "dd1,dd2,dd3,dd4,dd5,dd6,dd7,dd8,"	>> result.txt
echo -n "ss1,ss2,ss3,ss4,ss5,ss6,ss7,ss8,"	>> result.txt
echo -n "rmsd,"	>> result.txt
echo -n "Ax1,Ay1,Az1,Ax2,Ay2,Az2,Ax3,Ay3,Az3,Ax4,Ay4,Az4,Ax5,Ay5,Az5,Ax6,Ay6,Az6,Ax7,Ay7,Az7,Ax8,Ay8,Az8," >> result.txt
echo -n "Bx1,By1,Bz1,Bx2,By2,Bz2,Bx3,By3,Bz3,Bx4,By4,Bz4,Bx5,By5,Bz5,Bx6,By6,Bz6,Bx7,By7,Bz7,Bx8,By8,Bz8," >> result.txt
echo "Xx1,Xy1,Xz1,Xx2,Xy2,Xz2,Xx3,Xy3,Xz3,Xx4,Xy4,Xz4,Xx5,Xy5,Xz5,Xx6,Xy6,Xz6,Xx7,Xy7,Xz7,Xx8,Xy8,Xz8,Xx9,Xy9,Xz9,Xx10,Xy10,Xz10,Xx11,Xy11,Xz11,Xx12,Xy12,Xz12,Xx13,Xy13,Xz13,Xx14,Xy14,Xz14,Xx15,Xy15,Xz15,Xx16,Xy16,Xz16,Xx17,Xy17,Xz17,Xx18,Xy18,Xz18,Xx19,Xy19,Xz19,Xx20,Xy20,Xz20,Xx21,Xy21,Xz21,Xx22,Xy22,Xz22,Xx23,Xy23,Xz23,Xx24,Xy24,Xz24,sAx1,sAy1,sAz1,sAx2,sAy2,sAz2,sAx3,sAy3,sAz3,sAx4,sAy4,sAz4,sAx5,sAy5,sAz5,sAx6,sAy6,sAz6,sAx7,sAy7,sAz7,sAx8,sAy8,sAz8,sBx1,sBy1,sBz1,sBx2,sBy2,sBz2,sBx3,sBy3,sBz3,sBx4,sBy4,sBz4,sBx5,sBy5,sBz5,sBx6,sBy6,sBz6,sBx7,sBy7,sBz7,sBx8,sBy8,sBz8,sXx1,sXy1,sXz1,sXx2,sXy2,sXz2,sXx3,sXy3,sXz3,sXx4,sXy4,sXz4,sXx5,sXy5,sXz5,sXx6,sXy6,sXz6,sXx7,sXy7,sXz7,sXx8,sXy8,sXz8,sXx9,sXy9,sXz9,sXx10,sXy10,sXz10,sXx11,sXy11,sXz11,sXx12,sXy12,sXz12,sXx13,sXy13,sXz13,sXx14,sXy14,sXz14,sXx15,sXy15,sXz15,sXx16,sXy16,sXz16,sXx17,sXy17,sXz17,sXx18,sXy18,sXz18,sXx19,sXy19,sXz19,sXx20,sXy20,sXz20,sXx21,sXy21,sXz21,sXx22,sXy22,sXz22,sXx23,sXy23,sXz23,sXx24,sXy24,sXz24," >> result.txt

for (( i=1; i<=${max}; i++ )); do

	argv1="${i}_aims_init.in"
	argv2="${i}_aims_final.in"
	argv3="${i}_aims.out"

	python3 ${analysis_x} ${argv1} ${argv2} ${argv3} >> result.txt

	# silent
	#echo -ne "Progressing... ${i}/${max} \r"

	echo "progressing ... ${i}"
done


# Ax1,Ay1,Az1,Ax2,Ay2,Az2,Ax3,Ay3,Az3,Ax4,Ay4,Az4,Ax5,Ay5,Az5,Ax6,Ay6,Az6,Ax7,Ay7,Az7,Ax8,Ay8,Az8,
# Bx1,By1,Bz1,Bx2,By2,Bz2,Bx3,By3,Bz3,Bx4,By4,Bz4,Bx5,By5,Bz5,Bx6,By6,Bz6,Bx7,By7,Bz7,Bx8,By8,Bz8,
# Xx1,Xy1,Xz1,Xx2,Xy2,Xz2,Xx3,Xy3,Xz3,Xx4,Xy4,Xz4,Xx5,Xy5,Xz5,Xx6,Xy6,Xz6,Xx7,Xy7,Xz7,Xx8,Xy8,Xz8,Xx9,Xy9,Xz9,Xx10,Xy10,Xz10,Xx11,Xy11,Xz11,Xx12,Xy12,Xz12,Xx13,Xy13,Xz13,Xx14,Xy14,Xz14,Xx15,Xy15,Xz15,Xx16,Xy16,Xz16,Xx17,Xy17,Xz17,Xx18,Xy18,Xz18,Xx19,Xy19,Xz19,Xx20,Xy20,Xz20,Xx21,Xy21,Xz21,Xx22,Xy22,Xz22,Xx23,Xy23,Xz23,Xx24,Xy24,Xz24, 

# sAx1,sAy1,sAz1,sAx2,sAy2,sAz2,sAx3,sAy3,sAz3,sAx4,sAy4,sAz4,sAx5,sAy5,sAz5,sAx6,sAy6,sAz6,sAx7,sAy7,sAz7,sAx8,sAy8,sAz8,
# sBx1,sBy1,sBz1,sBx2,sBy2,sBz2,sBx3,sBy3,sBz3,sBx4,sBy4,sBz4,sBx5,sBy5,sBz5,sBx6,sBy6,sBz6,sBx7,sBy7,sBz7,sBx8,sBy8,sBz8,
# sXx1,sXy1,sXz1,sXx2,sXy2,sXz2,sXx3,sXy3,sXz3,sXx4,sXy4,sXz4,sXx5,sXy5,sXz5,sXx6,sXy6,sXz6,sXx7,sXy7,sXz7,sXx8,sXy8,sXz8,sXx9,sXy9,sXz9,sXx10,sXy10,sXz10,sXx11,sXy11,sXz11,sXx12,sXy12,sXz12,sXx13,sXy13,sXz13,sXx14,sXy14,sXz14,sXx15,sXy15,sXz15,sXx16,sXy16,sXz16,sXx17,sXy17,sXz17,sXx18,sXy18,sXz18,sXx19,sXy19,sXz19,sXx20,sXy20,sXz20,sXx21,sXy21,sXz21,sXx22,sXy22,sXz22,sXx23,sXy23,sXz23,sXx24,sXy24,sXz24,
