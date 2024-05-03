#!/bin/python3

import sys
import numpy as np
import pandas as pd
from math import factorial as fact

import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator

#filelist = [ 'HST10.0_d0.5.out', 'HST100.0_d0.5.out', 'HST1000.0_d0.5.out', 'HST200.0_d0.5.out', 'HST300.0_d0.5.out', 'HST500.0_d0.5.out' ]
#filelist = [ 'HST100.0_d0.5.out', 'HST200.0_d0.5.out', 'HST300.0_d0.5.out', 'HST500.0_d0.5.out' ]
filelist = [ 'HST100.0_d0.5.out', 'HST200.0_d0.5.out', 'HST300.0_d0.5.out' ]
#filelist = [ 'HST100.0_d0.5.out', 'HST200.0_d0.5.out', 'HST300.0_d0.5.out', 'HST500.0_d0.5.out', 'HST1000.0_d0.5.out' ]
#filelist = [ 'HST10.0_d0.5.out', 'HST100.0_d0.5.out', 'HST200.0_d0.5.out', 'HST300.0_d0.5.out', 'HST500.0_d0.5.out' ]
#filelist = [ 'HST100.0_d0.5.out', 'HST200.0_d0.5.out', 'HST300.0_d0.5.out', 'HST1000.0_d0.5.out' ]
# orange green red blue 

'''
	plot config
'''
cm = 1/2.54
fig, ax = plt.subplots()
fig.set_size_inches((16*cm,12*cm))

plt.subplots_adjust(
left = 0.125,
bottom = 0.125,
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
ax.set_ylim(-42,17)
ax.xaxis.set_major_locator(MultipleLocator(0.1))
ax.xaxis.set_minor_locator(MultipleLocator(0.05))
ax.yaxis.set_major_locator(MultipleLocator(10.))
ax.yaxis.set_minor_locator(MultipleLocator(5.))

# set no yticks - for the rests
#ax.set_yticks([])
#ax.set_ylabel('$\it V$ (vs. Li/Li$^+$)', fontsize=_lfs)
#ax.set_ylabel('V (vs. Li/Li^+)', fontsize=_lfs+4)
ax.set_ylabel('$\it S$$_\mathrm{mix}$ (J mol$^{-1}$ K$^{-1}$)', fontsize=_lfs)


#clist = ['silver','lightcoral','black','bisque','lime','khaki','peachpuff','aqua','plum']
#clist = ['gray','indianred','orange','forestgreen','gold','chocolate','steelblue','mediumpurple']
#clist = ['gray','indianred','orange','black','gold','chocolate','steelblue','mediumpurple']
#clist = ['steelblue','lightcoral','black','lime','khaki','peachpuff','aqua','plum']
#clist = ['indianred','orange','mediumpurple','lime','black','forestgreen','chocolate','steelblue','mediumpurple']

#clist = ['steelblue','orange','red','black','gray']
clist = ['orange','green','red','blue']
clist = ['orange','coral','red','rosybrown','black']
clist = ['orange','blue','red','rosybrown','black']

sizelist = ['1 samples','1000 samples','5000 samples','10000 samples','100000 samples']
# plot
for i,file_path in enumerate(filelist):

	with open(file_path,'r') as file:

		data = np.loadtxt(file,skiprows=1)

		#if i < 3:
		#	x = data[:,0]
		#	y = data[:,2]
		#else:
		#	x = data[:,0]
		#	y = data[:,1]
		x = data[:,0]
		y = data[:,3] # col3 -> 'S' entropy 

		#if i == 4:
		#	ax.plot(x,y, color=clist[i], linestyle='--', label=f'{sizelist[i]}')
		#else:
		#	ax.plot(x,y, color=clist[i], label=f'{sizelist[i]}')
		# Reference


		#if i == 0:
		#	#ax.plot(x,y, color=clist[i], label=f'10K$^a$')
		#	ax.plot(x,y, color=clist[i], label=f'10K')
		#if i == 1:
		#	#ax.plot(x,y, color=clist[i], label=f'100K$^a$')
		#	ax.plot(x,y, color=clist[i], label=f'100K')
		#if i == 2:
		#	#ax.plot(x,y, color=clist[i], label=f'300K$^a$')
		#	ax.plot(x,y, color=clist[i], label=f'300K')
		#if i == 3:
		#	ax.plot(x,y, color=clist[i], label=f'Exp.$^a$')
		#if i == 4:
		#	ax.plot(x,y, color=clist[i], label=f'DFT$^a$')


		#ax.plot(x,y, color=clist[i])
		if i == 0:
			ax.plot(x,y, color=clist[i], label=f'100K')
			# ax.plot(x,y, color=clist[i], label=f'100K',marker='o',markevery=10)
		if i == 1:
			ax.plot(x,y, color=clist[i], label=f'200K')
		if i == 2:
			ax.plot(x,y, color=clist[i], label=f'300K')

	ax.legend(fontsize=_fs-2)
	# Add legend outside the graph
	#ax.legend(fontsize=_fs-3.5, bbox_to_anchor=(1.05, 1), loc='upper left')


# add reference line
#ax.axvline(x=9./24., color='black', linestyle='--') # label='Reference line')
#ax.axvline(x=15./24., color='black', linestyle='--') #label='Reference line')
ax.axvline(x=12./24., color='black', linestyle='--') #label='Reference line')
ax.axhline(y=0, color='black', linestyle='--') #label='Reference line')

fig.savefig(f'EntropyProfile.png', dpi=1200, bbox_inches='tight')
fig.savefig(f'EntropyProfile.pdf', format='pdf', dpi=1200, bbox_inches='tight')

plt.show()
