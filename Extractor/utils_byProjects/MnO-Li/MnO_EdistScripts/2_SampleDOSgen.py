#!/bin/python

import sys
import numpy as np
import pandas as pd

import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator

import seaborn as sns



if __name__=='__main__':

	# sampling 3,6,9,12,15,18,21,24
	csvlist = [ f'nconp{(i+1)*3}.csv' for i in range(8) ]
	size    = [ (i+1)*3 for i in range(8) ]
	xlist   = [ float((i+1)*3)/24. for i in range(8) ]

	# some model parameters
	_e_gulp_mn2O4 = -534.25669638*6.                                        # R - Mn24O48 energy
	_LiOx         = +5.39171                                                # Li(g) -> Li(+)(g) + e-
	_MnRe         = -51.2                                                   # Mn(4+)(g) + e- -> Mn(3+)(g)

	#
	# this may change
	# _corr         = +1.6510 + 5.7400                                        # 1.6510(eV): formation energy Li CRC : +159.3kJ/mol Li(g), + residual energy 5.740 (eV); or the chemical potential (u)
	# _corr = 7.391
	# change me - chemical potential 
	_corr = 7.391


	# testing some values near 5.74 eV
	# Read CSV files
	dflist = []
	gmelist = []
	for csvfile,s in zip(csvlist,size):
		try:
			df = pd.read_csv(csvfile)
			if len(df) > 10000:
				df = df.sample(n=10000, random_state=42)  # Use a fixed random state for reproducibility
			# Lithiation energy converting
			df['energy'] = (df['energy'] - _e_gulp_mn2O4 + (_LiOx + _MnRe + _corr) * s )/24.		# yes chemical potential
			#df['energy'] = (df['energy'] - _e_gulp_mn2O4 + (_LiOx + _MnRe + 0. ) * s )/24.			# no  chemical potential

			# sorting ... 'energy'
			df = df.sort_values(by='energy',ascending=True)

			# df['energy'] = df['energy'] - 0.25
			# Subtract 0.25 only from rows where another column 'condition_column' has a certain value
			# df.loc[df['condition_column'] == 'specific_value', 'energy'] = df.loc[df['condition_column'] == 'specific_value', 'energy'] - 0.25
			_global_min = df['energy'].iloc[0]
			gmelist.append(_global_min)

			# calibration
			#df['energy'] = df['energy'] - _global_min# calibration

			# save into 'dflist' using later
			dflist.append(df)

		except IndexError as e:
			print(e)
	'''
	# Energy resetting (lithiation energy)
	#
	#   dH = E[Li(1+)x Mn(3+)x Mn(4+)(2-x) O4] - E[Mn(4+)2 O4] - xE[Li(0)] + xE[Mn(3+)] - nE[Mn(4+)] + nE[Li(1+)]
	            = E[Li(1+)x Mn(3+)x Mn(4+)(2-x) O4] - E[Mn(4+)2 O4] + n{E[Li(1+)] - E[Li(0)]} + n{E[Mn(3+)]-E[Mn(4+)]}
	              VVVVVVVV                            VVVVVVV         VVVVVVV                   VVVVVVV
	              GULP calculated sample energy       GULP Mn2O4      Oxidation E of Li         Reduction energy of Mn3+
	                                                                  VVVVVVV                   VVVVVVV
	                                                                  Ionisation E of Li        - 4th Ionisation E of Mn
	     (E-E0+ErM+EoLi)/24 -> to MnO2 unit
	'''
_r = 2
_c = 4

cm = 1/2.54
fig, axes = plt.subplots(_r,_c)   # 2 (rows) x 4 (cols)
#fig.set_size_inches((36*cm,16*cm))
fig.set_size_inches((40*cm,20*cm))

plt.subplots_adjust(
    left = 0.03,
    bottom = 0.1,
    right = 0.97,
    top = 0.96,
    wspace = 0.080,
    hspace = 0.200,
)
_fs = 12    # font size - ticks / text (+2)
_lfs = 14   # font size - labels

# histogram parameters
_div = 60

for i in range(_r):
	for j in range(_c):

		dl = i*4 + j # index access dflist

		sns.histplot(dflist[dl]['energy'].tolist(),bins=(len(dflist[dl]['energy'].tolist()))//_div,kde=True,stat='probability',ax=axes[i,j],color='blue',element="step")
		#axes[i,j].axvspan(0, (3.+xlist[dl])*0.0259, alpha=0.3, color='red')

		#axes[i,j].set_yticks([])

		# set all ylim same
		axes[i,j].set_ylim(0,0.08)
		# remove yticks
		axes[i,j].set_yticks([])

		# set xtick size
		axes[i,j].tick_params(axis='x', labelsize=_fs)
		# set xticks
		axes[i,j].xaxis.set_major_locator(MultipleLocator(0.2))
		axes[i,j].xaxis.set_minor_locator(MultipleLocator(0.05))

		if j == 0:
			axes[i,j].set_ylabel('DOS, (a.u.)',fontsize=_lfs)
		else:
			axes[i,j].set_ylabel('')
		#axes[i,j].set_xlabel('Energy (eV) x=%.3f' % (xlist[dl]))
		axes[i,j].set_xlabel(f'$\it E_\mathrm{{r}}$($\it x$={xlist[dl]:.3f}), (eV/f.u.)',fontsize=_lfs)

		#axes[i,j].set_xlim(0,0.5)
		#axes[i,j].set_xlim(gmelist[dl]+0.,gmelist[dl]+0.5)
		if i > 0:
			axes[i,j].set_ylim(0,0.06)

fig.savefig(f'dos_all.png', dpi=1200, bbox_inches='tight')
fig.savefig(f'dos_all.pdf', format='pdf', dpi=1200, bbox_inches='tight')

plt.show()


sys.exit()	# ------------------------------------------------------------------------------------------------------------------

# plot

fig, axes = plt.subplots(6,4)   # 6 x 4 -> 24 figs together

plt.subplots_adjust(
wspace = 0.225,
hspace = 0.33,
left = 0.05,
right = 0.95,
bottom = 0.05,
top = 0.95)

# parameter 
_div = 60
fs = 16


for i in range(6):
	for j in range(4):
		dl = i*4 + j

		sns.histplot(dflist[dl]['energy'].tolist(),bins=(len(dflist[dl]['energy'].tolist()))//_div,kde=True,stat='probability',ax=axes[i,j],color='blue',element="step")
		#sns.histplot(dflist[dl]['energy'].tolist(),bins=(len(dflist[dl]['energy'].tolist()))//_div,kde=True,stat='density',ax=axes[i,j],color='blue')
		#sns.histplot(dflist[dl]['energy'].tolist(),bins=30,kde=True,stat='density',ax=axes[i,j],color='blue')

		#axes[i,j].fill_between(np.arange(0.0,(3.+xlist[dl])*0.0259,0.01),facecolor='gray',alpha=0.5)
		axes[i,j].axvspan(0, (3.+xlist[dl])*0.0259, alpha=0.3, color='red')
		#axes[i,j].axvspan(gmelist[dl] + 0.,gmelist[dl] + (3.+xlist[dl])*0.0259, alpha=0.3, color='red')

		if j == 0:
			axes[i,j].set_ylabel('DOS')
		else:
			axes[i,j].set_ylabel('')
		axes[i,j].set_xlabel('Energy (eV) x=%.3f' % (xlist[dl]))

		axes[i,j].set_xlim(0,0.5)
		#axes[i,j].set_xlim(gmelist[dl]+0.,gmelist[dl]+0.5)
		if i > 0:
			axes[i,j].set_ylim(0,0.06)

fig.set_size_inches((14,14))
fig.savefig(f'delocal_all.png')
plt.show()
