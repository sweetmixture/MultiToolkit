#!/bin/python3

import sys
import numpy as np
import pandas as pd
from math import factorial as fact

import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator

_mode = 'v'
# mode : v , p
filelist = [ f'{_mode}{i}.out' for i in range(5) ]


'''
	plot config
'''
cm = 1/2.54
fig, ax = plt.subplots()
fig.set_size_inches((16*cm,12*cm))

plt.subplots_adjust(
left = 0.10,
bottom = 0.1,
right = 0.96,
top = 0.96,
wspace = 0.200,
hspace = 0.0
)

# font size
_fs = 12
_lfs = 14

#
ax.set_xlabel('$\it x$', fontsize=_lfs)

ax.tick_params(axis='x', labelsize=_fs)  # Corrected line
ax.tick_params(axis='y', labelsize=_fs)  # Corrected line
ax.set_xlim(0., 1.)
ax.set_ylim(0.0,5.4)
ax.xaxis.set_major_locator(MultipleLocator(0.1))
ax.xaxis.set_minor_locator(MultipleLocator(0.05))
ax.yaxis.set_major_locator(MultipleLocator(0.5))
ax.yaxis.set_minor_locator(MultipleLocator(0.25))

# set no yticks - for the rests
#ax.set_yticks([])
ax.set_ylabel('V (vs. Li/Li$^+$)', fontsize=_lfs)
#ax.set_ylabel('V (vs. Li/Li^+)', fontsize=_lfs+4)


clist = ['silver','lightcoral','black','bisque','lime','khaki','peachpuff','aqua','plum']
#clist = ['gray','indianred','orange','forestgreen','gold','chocolate','steelblue','mediumpurple']
clist = ['gray','indianred','orange','black','gold','chocolate','steelblue','mediumpurple']
#clist = ['steelblue','lightcoral','black','lime','khaki','peachpuff','aqua','plum']
clist = ['indianred','orange','mediumpurple','lime','black','forestgreen','chocolate','steelblue','mediumpurple']

sizelist = ['1 samples','1000 samples','5000 samples','10000 samples','100000 samples']
# plot
for i,file_path in enumerate(filelist):

	with open(file_path,'r') as file:

		data = np.loadtxt(file,skiprows=1)

		x = data[:,0]
		y = data[:,2]

		if i == 4:
			ax.plot(x,y, color=clist[i], linestyle='--', label=f'{sizelist[i]}')
		else:
			ax.plot(x,y, color=clist[i], label=f'{sizelist[i]}')

	#ax.legend(fontsize=_fs-2)
	# Add legend outside the graph
	ax.legend(fontsize=_fs-3.5, bbox_to_anchor=(1.05, 1), loc='upper left')


# add reference line
ax.axvline(x=1./24., color='red', linestyle=':', label='Reference line')
#ax.axvline(x=23./24., color='blue', linestyle='--', label='Reference line')

fig.savefig(f'{_mode}_allrange.png', dpi=1200, bbox_inches='tight')
fig.savefig(f'{_mode}_allrange.pdf', format='pdf', dpi=1200, bbox_inches='tight')

plt.show()
