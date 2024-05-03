#!/bin/python

import sys
import numpy as np
import pandas as pd
from math import factorial as fact

import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator

import seaborn as sns

# execution
# $python this_script.py nconp${N}.csv N

if __name__=='__main__':

	csvlist = [sys.argv[1]]
	size    = [int(sys.argv[2])]

	xlist   = []    # save fraction 'x'
	for s in size:
	    x = float(s)/24.
	    xlist.append(x)
	# some model parameters
	_e_gulp_mn2O4 = -534.25669638*6.                                        # R - Mn24O48 energy
	_LiOx         = +5.39171                                                # Li(g) -> Li(+)(g) + e-
	_MnRe         = -51.2                                                   # Mn(4+)(g) + e- -> Mn(3+)(g)

	#
	# this may change
	# _corr         = +1.6510 + 5.7400	# 1.6510(eV): formation energy Li CRC : +159.3kJ/mol Li(g), + residual energy 5.740 (eV); or the chemical potential (u)
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
			if len(df) > 15000:
				df = df.sample(n=15000, random_state=42)  # Use a fixed random state for reproducibility

				df1= df.sample(n=10000, random_state=42)
				df2= df.sample(n=5000, random_state=42)
				df3= df.sample(n=2000, random_state=42)
				df4= df.sample(n=1000, random_state=42)
				df5= df.sample(n=100, random_state=42)

			# Lithiation energy converting
			#df['energy'] = (df['energy'] - _e_gulp_mn2O4 + (_LiOx + _MnRe + 0. ) * s )/24.			# no  chemical potential
			#df['energy'] = (df['energy'] - _e_gulp_mn2O4 + (_LiOx + _MnRe + _corr) * s )/24.		# yes chemical potential
			#df1['energy'] = (df1['energy'] - _e_gulp_mn2O4 + (_LiOx + _MnRe + _corr) * s )/24.		# yes chemical potential
			#df2['energy'] = (df2['energy'] - _e_gulp_mn2O4 + (_LiOx + _MnRe + _corr) * s )/24.		# yes chemical potential
			#df3['energy'] = (df3['energy'] - _e_gulp_mn2O4 + (_LiOx + _MnRe + _corr) * s )/24.		# yes chemical potential
			#df4['energy'] = (df4['energy'] - _e_gulp_mn2O4 + (_LiOx + _MnRe + _corr) * s )/24.		# yes chemical potential
			#df5['energy'] = (df5['energy'] - _e_gulp_mn2O4 + (_LiOx + _MnRe + _corr) * s )/24.		# yes chemical potential

			df['energy'] = (df['energy'] - _e_gulp_mn2O4)/24.

			df1['energy'] = (df1['energy'] - _e_gulp_mn2O4)/24. 
			df2['energy'] = (df2['energy'] - _e_gulp_mn2O4)/24.
			df3['energy'] = (df3['energy'] - _e_gulp_mn2O4)/24.
			df4['energy'] = (df4['energy'] - _e_gulp_mn2O4)/24.
			df5['energy'] = (df5['energy'] - _e_gulp_mn2O4)/24.


			# sorting ... 'energy'
			df = df.sort_values(by='energy',ascending=True)

			df1 = df1.sort_values(by='energy',ascending=True)
			df2 = df2.sort_values(by='energy',ascending=True)
			df3 = df3.sort_values(by='energy',ascending=True)
			df4 = df4.sort_values(by='energy',ascending=True)
			df5 = df5.sort_values(by='energy',ascending=True)

			# df['energy'] = df['energy'] - 0.25
			# Subtract 0.25 only from rows where another column 'condition_column' has a certain value
			# df.loc[df['condition_column'] == 'specific_value', 'energy'] = df.loc[df['condition_column'] == 'specific_value', 'energy'] - 0.25
			_global_min = df['energy'].iloc[0]
			gmelist.append(_global_min)

			# calibration
			#df['energy'] = df['energy'] - _global_min# calibration
			#df1['energy'] = df1['energy'] - _global_min# calibration
			#df2['energy'] = df2['energy'] - _global_min# calibration
			#df3['energy'] = df3['energy'] - _global_min# calibration
			#df4['energy'] = df4['energy'] - _global_min# calibration
			#df5['energy'] = df5['energy'] - _global_min# calibration

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

'''
	plot settings
'''
cm = 1/2.54
fig, axes = plt.subplots(5,1)   # 5 (rows) x 1 (cols)
fig.set_size_inches((16*cm,16*cm))

plt.subplots_adjust(
    left = 0.1,
    bottom = 0.1,
    right = 0.96,
    top = 0.96,
    wspace = 0.200,
    hspace = 0.0
)
_fs = 12	# font size - ticks / text (+2)
_lfs = 14	# font size - labels

#
_div = 60
stat = 'density' # 'probability'
bwa=0.38
#sns.kdeplot(data=df5,x='energy',ax=axes[0],fill=True,bw_adjust=bwa)
#sns.kdeplot(data=df4,x='energy',ax=axes[1],fill=True,bw_adjust=bwa)
#sns.kdeplot(data=df3,x='energy',ax=axes[2],fill=True,bw_adjust=bwa)
#sns.kdeplot(data=df2,x='energy',ax=axes[3],fill=True,bw_adjust=bwa)
#sns.kdeplot(data=df1,x='energy',ax=axes[4],fill=True,bw_adjust=bwa)

#bins = np.histogram_bin_edges(df['energy'],bins='auto')

bins = np.histogram_bin_edges(df['energy'],bins='fd')		# for using same bins ... function itself for getting optimal number of bins
ble = bins[0]
bre = bins[-1]
bin_count = 120

dbin = (bre - ble)/bin_count

bins = []
for i in range(bin_count):
	bins.append(ble + float(i)*dbin)
bins = np.array(bins)


#sns.histplot(df1['energy'].tolist(),bins=(len(df1['energy'].tolist()))//_div,kde=True,stat=stat,color='blue',ax=axes[4],element='step')
sns.histplot(df5['energy'].tolist(),kde=True,kde_kws={'bw_adjust': bwa},stat=stat,color='blue',ax=axes[0],element='step',bins=bins)
sns.histplot(df4['energy'].tolist(),kde=True,kde_kws={'bw_adjust': bwa},stat=stat,color='blue',ax=axes[1],element='step',bins=bins)
sns.histplot(df3['energy'].tolist(),kde=True,kde_kws={'bw_adjust': bwa},stat=stat,color='blue',ax=axes[2],element='step',bins=bins)
sns.histplot(df2['energy'].tolist(),kde=True,kde_kws={'bw_adjust': bwa},stat=stat,color='blue',ax=axes[3],element='step',bins=bins)
sns.histplot(df1['energy'].tolist(),kde=True,kde_kws={'bw_adjust': bwa},stat=stat,color='blue',ax=axes[4],element='step',bins=bins)

nsamples = [len(df5),len(df4),len(df3),len(df2),len(df1)]


# fraction x
frac_x = float(sys.argv[2])/24.
frac_x = str(round(frac_x,2))

for i,axis in enumerate(axes):
	print(i)

	if i == 4:	
		#axis.set_xlabel(f'$\Delta \it E_\mathrm{{f}}$, (eV / Li$_{{{frac_x}}}$MnO$_{{2}}$ unit)', fontsize=_lfs)
		axis.set_xlabel(f'$\Delta \it E_\mathrm{{f}}$, (eV/f.u.)',fontsize=_lfs)
		axis.tick_params(axis='x', labelsize=_fs)

		axis.xaxis.set_major_locator(MultipleLocator(0.1))
		axis.xaxis.set_minor_locator(MultipleLocator(0.05))

	axis.set_xlim(ble,bre)

	axis.set_ylabel('')
	#axis.set_ylim(0,8)
	axis.set_yticks([])
	if i != 4:
		axis.set_xticks([])

	#axis.tick_params(axis='both',which='both',labelsize=14)

	text = f'{nsamples[i]} samples'	
	axis.text(0.85,0.8,text,transform=axis.transAxes,fontsize=_fs+2,ha='center',va='center')		# transform=axis.transAxes ensures that the coordinates are relative to the axes.

#if j == 0:
#    axes[i,j].set_ylabel('DOS')
#else:
#    axes[i,j].set_ylabel('')
#axes[i,j].set_xlabel('Energy (eV) x=%.3f' % (xlist[dl]))
#axes[i,j].set_xlim(0,0.5)
##axes[i,j].set_xlim(gmelist[dl]+0.,gmelist[dl]+0.5)
#if i > 0:
#    axes[i,j].set_ylim(0,0.06)


#sns.histplot(df['energy'].tolist(),bins=(len(df['energy'].tolist()))//_div,kde=True,stat=stat,color='blue',ax=axes,element='step')
#sns.histplot(df5['energy'].tolist(),bins=(len(df5['energy'].tolist()))//_div,kde=True,stat=stat,color='green',ax=axes,element='step'
#sns.histplot(dflist[dl]['energy'].tolist(),bins=(len(dflist[dl]['energy'].tolist()))//_div,kde=True,stat='probability',ax=axes[i,j],color='blue',element="step")

fig.text(0.04, 0.5, 'DOS, (a.u.)', va='center', rotation='vertical', fontsize=_lfs)
'''
	0.04, 0.5 : fractional x y in the figure
	va - cetnre vertically
	rotation rotate
	fontsize - fontsize
'''

fig.savefig(f'convergence_check_size{sys.argv[2]}.png', dpi=1200, bbox_inches='tight')
fig.savefig(f'convergence_check_size{sys.argv[2]}.pdf', format='pdf', dpi=1200, bbox_inches='tight')

plt.show()

sys.exit(1)
