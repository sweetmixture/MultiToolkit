#!/bin/python
import os,sys
import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator
import numpy as np
from scipy.ndimage import gaussian_filter1d

# Function to plot data with offset and Gaussian broadening

# Example usage
_T1 = 10
_T2 = 300

path1 = f'/Users/woongkyujee/Desktop/2023SolidSolution/PaperWriting/XRD_Analysis/GCEnsemble/vXRD_T{_T1}'
path2 = f'/Users/woongkyujee/Desktop/2023SolidSolution/PaperWriting/XRD_Analysis/GCEnsemble/vXRD_T{_T2}'

ref_path = '/Users/woongkyujee/Desktop/2023SolidSolution/PaperWriting/XRD_Analysis/GCEnsemble/GULP_MnO2_0Li.int'

_max = 24

#offset = 6
offset = 0.4
sigma = 0.001
#sigma = 0.00001

'''
	color scheme
'''
clist1 = ['silver','lightcoral','bisque','lime','khaki','peachpuff','aqua','plum']
clist2 = ['gray','indianred','orange','forestgreen','gold','chocolate','steelblue','mediumpurple']

def plot_data(file_paths, offset=offset, broadening_sigma=sigma):

	file_paths1, file_paths2 = file_paths

	fcheck1 = [ os.path.exists(path) for path in file_paths1 ]
	fcheck2 = [ os.path.exists(path) for path in file_paths2 ]

	print(fcheck1,fcheck2)

	global _T1, _T2

	'''
		plot config
	'''
	cm = 1/2.54
	fig, ax = plt.subplots()
	fig.set_size_inches((16*cm,18*cm))

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

	ax.set_xlabel('2$\it θ$ (°)', fontsize=_lfs)


	ax.tick_params(axis='x', labelsize=_fs)  # Corrected line
	#ax.tick_params(axis='y', labelsize=_fs)  # Corrected line
	ax.set_xlim(15, 60)
	#ax.set_ylim(-20, 110)
	ax.xaxis.set_major_locator(MultipleLocator(5))
	ax.xaxis.set_minor_locator(MultipleLocator(2.5))

	# set no yticks - for the rests
	ax.set_yticks([])

	ax.set_ylabel('$\it I$ (a.u.)', fontsize=_lfs+4)

	# ----------------------------------------------------------
	# plotting - 1
	for i, file_path in enumerate(file_paths1):
		# Read data from file
		with open(file_path, 'r') as file:
			data = np.loadtxt(file, skiprows=1)
			#data = np.loadtxt(file)
			x = data[:, 0]
			y = data[:, 1]
 
		# Normalise
		max_y = max(y)
		#max_y = 1
		y_normalised = y / max_y
	   
		# Apply offset to y values
		y_offset = i * offset
		#print(i,offset,y_offset)
		
		# Apply Gaussian broadening to y values
		y_broadened = gaussian_filter1d(y_normalised, sigma=broadening_sigma)
		
		# Plot data
		if i == 0:
			ax.plot(x, y_broadened + y_offset, color=clist1[i], label=f'{_T1} K')
		else:
			ax.plot(x, y_broadened + y_offset, color=clist1[i])
	
	# ----------------------------------------------------------
	# plotting - 2
	for i, file_path in enumerate(file_paths2):
		# Read data from file
		with open(file_path, 'r') as file:
			data = np.loadtxt(file, skiprows=1)
			#data = np.loadtxt(file)
			x = data[:, 0]
			y = data[:, 1]
 
		# Normalise
		max_y = max(y)
		#max_y = 1
		y_normalised = y / max_y
	   
		# Apply offset to y values
		y_offset = i * offset
		#print(i,offset,y_offset)
		
		# Apply Gaussian broadening to y values
		y_broadened = gaussian_filter1d(y_normalised, sigma=broadening_sigma)

		# Plot data
		if i == 0:
			ax.plot(x, y_broadened + y_offset, color=clist2[i], linestyle='--', label=f'{_T2} K')
		else:
			ax.plot(x, y_broadened + y_offset, color=clist2[i], linestyle='--')

	# plot reference R-MnO2 
	global ref_path
	with open(ref_path,'r') as file:
		data = np.loadtxt(file,skiprows=2)
		x = data[:,0]
		y = data[:,1]

		# Normalise
		max_y = max(y)
		#max_y = 1
		y_normalised = y / max_y
	   
		# Apply offset to y values
		y_offset = 1 * offset
		#print(i,offset,y_offset)
		
		# Apply Gaussian broadening to y values
		y_broadened = gaussian_filter1d(y_normalised, sigma=broadening_sigma)

		ax.plot(x, y_broadened - y_offset, color='black', label=f'R-MnO$_2$')

	#plt.legend()	# as done as 'label' in plot()
	ax.legend(fontsize=_fs)

	plt.show()

	fig.savefig(f'v_xrd_ce_mul_{_T1}_{_T2}.png', dpi=1200, bbox_inches='tight')
	fig.savefig(f'v_xrd_ce_mul_{_T1}_{_T2}.pdf', format='pdf', dpi=1200, bbox_inches='tight')

# ------------------------------------------------------------------------------

file_paths1 = [f'XRD_GCE_{_T1}.0_0.125.xrd', f'XRD_GCE_{_T1}.0_0.25.xrd', f'XRD_GCE_{_T1}.0_0.375.xrd', f'XRD_GCE_{_T1}.0_0.5.xrd', f'XRD_GCE_{_T1}.0_0.625.xrd',
            f'XRD_GCE_{_T1}.0_0.75.xrd', f'XRD_GCE_{_T1}.0_0.875.xrd',  f'XRD_GCE_{_T1}.0_1.0.xrd' ]

file_paths2 = [f'XRD_GCE_{_T2}.0_0.125.xrd', f'XRD_GCE_{_T2}.0_0.25.xrd', f'XRD_GCE_{_T2}.0_0.375.xrd', f'XRD_GCE_{_T2}.0_0.5.xrd', f'XRD_GCE_{_T2}.0_0.625.xrd',
            f'XRD_GCE_{_T2}.0_0.75.xrd', f'XRD_GCE_{_T2}.0_0.875.xrd',  f'XRD_GCE_{_T2}.0_1.0.xrd' ]


for i in range(len(file_paths1)):

	file_paths1[i] = os.path.join(path1,file_paths1[i])
	file_paths2[i] = os.path.join(path2,file_paths2[i])

	print(file_paths1[i],file_paths2[i])
file_paths = (file_paths1, file_paths2)

plot_data(file_paths, offset=offset, broadening_sigma=sigma)

