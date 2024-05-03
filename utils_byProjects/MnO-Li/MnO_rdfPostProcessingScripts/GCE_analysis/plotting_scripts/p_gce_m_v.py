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


#path1 = f'/Users/woongkyujee/Desktop/2023SolidSolution/PaperWriting/RDF_Analysis/GCEnsemble/RDF_GCE_T{_T1}'
#path2 = f'/Users/woongkyujee/Desktop/2023SolidSolution/PaperWriting/RDF_Analysis/GCEnsemble/RDF_GCE_T{_T2}'

path1 = f'/Users/woongkyujee/Desktop/2023SolidSolution/PaperWriting/RDF_Analysis/GCEnsemble/vRDF_GCE_T{_T1}'
path2 = f'/Users/woongkyujee/Desktop/2023SolidSolution/PaperWriting/RDF_Analysis/GCEnsemble/vRDF_GCE_T{_T2}'

_max = 24

#offset = 6
offset = 12
sigma = 3
#sigma = 0.00001

'''
	color scheme
'''
c_1 = 'lime'		# LiLi	(3)
#c_2 = 'darkorchid'	# TcTc	(4)
c_2 = 'violet'	# TcTc	(4)
#c_3 = 'slategrey'	# LiTc	(7)
c_3 = 'aqua'	# LiTc	(7)

c_11 = 'forestgreen'
c_22 = 'blueviolet'
c_33 = 'steelblue'

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
	fig, axes = plt.subplots(1,3)
	fig.set_size_inches((32*cm,16*cm))

	plt.subplots_adjust(
		left = 0.04,
		bottom = 0.1,
		right = 0.96,
		top = 0.96,
		wspace = 0.200,
		hspace = 0.0
	)
	
	# font size
	_fs = 12
	_lfs = 14

	#axes[0].set_xlabel('$\it{r}$(Li$^{+}$-Li$^{+}$), Å', fontsize=_lfs)
	#axes[1].set_xlabel('$\it{r}$(Mn$^{3+}$-Mn$^{3+}$), Å', fontsize=_lfs)
	#axes[2].set_xlabel('$\it{r}$(Mn$^{3+}$-Li$^{+}$), Å', fontsize=_lfs)

	#axes[0].set_xlabel('$\it{r}_\mathrm{Li^{+}Li^{+}}$, ${\AA}$', fontsize=_lfs)
	axes[0].set_xlabel('$\it{r}_\mathrm{Li^{+}Li^{+}}$, Å', fontsize=_lfs)
	axes[1].set_xlabel('$\it{r}_\mathrm{Mn^{3+}Mn^{3+}}$, Å', fontsize=_lfs)
	axes[2].set_xlabel('$\it{r}_\mathrm{Mn^{3+}Li^{+}}$, Å', fontsize=_lfs)

	for i,ax in enumerate(axes):
		ax.tick_params(axis='x', labelsize=_fs)  # Corrected line
		#ax.tick_params(axis='y', labelsize=_fs)  # Corrected line
		ax.set_xlim(1.5, 8.0)
		ax.set_ylim(-20, 110)

		ax.xaxis.set_major_locator(MultipleLocator(1))
		ax.xaxis.set_minor_locator(MultipleLocator(0.5))

		# set no yticks - for the rests
		ax.set_yticks([])
		if i == 0:
			ax.set_ylabel('$\it{g}$($\it{r}$), a.u.', fontsize=_lfs+4)

	axes[0].legend([f'{_T2} K'],fontsize=_fs)
	axes[1].legend([f'{_T2} K'],fontsize=_fs)
	axes[2].legend([f'{_T2} K'],fontsize=_fs)
	
	# ----------------------------------------------------------
	# plotting - 1
	for i, file_path in enumerate(file_paths1):
		# Read data from file
		with open(file_path, 'r') as file:
			data = np.loadtxt(file, skiprows=1)
			#data = np.loadtxt(file)
			x = data[:, 0]

			y1 = data[:, 2]
			y2 = data[:, 3]
			y3 = data[:, 6]
 
		# Normalise
		#max_y1 = max(y1)
		#max_y2 = max(y2)
		#max_y3 = max(y3)
		max_y1 = 1
		max_y2 = 1
		max_y3 = 1
		#print(max_y1,max_y2,max_y3)
		y_normalised1 = y1 / max_y1
		y_normalised2 = y2 / max_y2
		y_normalised3 = y3 / max_y3
	   
		# Apply offset to y values
		y_offset = i * offset
		print(i,offset,y_offset)
		
		# Apply Gaussian broadening to y values
		#y_broadened = gaussian_filter1d(y, sigma=broadening_sigma)
		y_broadened1 = gaussian_filter1d(y_normalised1, sigma=broadening_sigma)
		y_broadened2 = gaussian_filter1d(y_normalised2, sigma=broadening_sigma)
		y_broadened3 = gaussian_filter1d(y_normalised3, sigma=broadening_sigma)
		
		# Plot data
		if i == 0:
			axes[0].plot(x, y_broadened1 + y_offset - 15, color=c_1, label=f'{_T1} K')
			axes[1].plot(x, y_broadened2 + y_offset - 15, color=c_2, label=f'{_T1} K')
			axes[2].plot(x, y_broadened3 + y_offset - 15, color=c_3, label=f'{_T1} K')
		else:
			axes[0].plot(x, y_broadened1 + y_offset, color=c_1)
			axes[1].plot(x, y_broadened2 + y_offset, color=c_2)
			axes[2].plot(x, y_broadened3 + y_offset, color=c_3)
	
		#if i == 0:
		#	axes[0].legend([f'{_T1} K'])
		#	axes[1].legend([f'{_T1} K'])
		#	axes[2].legend([f'{_T1} K'])

	# ----------------------------------------------------------
	# plotting - 2
	for i, file_path in enumerate(file_paths2):
		# Read data from file
		with open(file_path, 'r') as file:
			data = np.loadtxt(file, skiprows=1)
			#data = np.loadtxt(file)
			x = data[:, 0]

			y1 = data[:, 2]
			y2 = data[:, 3]
			y3 = data[:, 6]
 
		# Normalise
		#max_y1 = max(y1)
		#max_y2 = max(y2)
		#max_y3 = max(y3)
		max_y1 = 1
		max_y2 = 1
		max_y3 = 1
		#print(max_y1,max_y2,max_y3)
		y_normalised1 = y1 / max_y1
		y_normalised2 = y2 / max_y2
		y_normalised3 = y3 / max_y3
	   
		# Apply offset to y values
		y_offset = i * offset
		
		# Apply Gaussian broadening to y values
		#y_broadened = gaussian_filter1d(y, sigma=broadening_sigma)
		y_broadened1 = gaussian_filter1d(y_normalised1, sigma=broadening_sigma)
		y_broadened2 = gaussian_filter1d(y_normalised2, sigma=broadening_sigma)
		y_broadened3 = gaussian_filter1d(y_normalised3, sigma=broadening_sigma)
		

		# Plot data
		if i == 0:
			axes[0].plot(x, y_broadened1 + y_offset - 15, color=c_11, linestyle='--', label=f'{_T2} K')
			axes[1].plot(x, y_broadened2 + y_offset - 15, color=c_22, linestyle='--', label=f'{_T2} K')
			axes[2].plot(x, y_broadened3 + y_offset - 15, color=c_33, linestyle='--', label=f'{_T2} K')
		else:
			axes[0].plot(x, y_broadened1 + y_offset, color=c_11, linestyle='--')
			axes[1].plot(x, y_broadened2 + y_offset, color=c_22, linestyle='--')
			axes[2].plot(x, y_broadened3 + y_offset, color=c_33, linestyle='--')

		#if i == 0:
		#	axes[0].legend([f'{_T2} K'])
		#	axes[1].legend([f'{_T2} K'])
		#	axes[2].legend([f'{_T2} K'])

	#plt.legend()	# as done as 'label' in plot()
	axes[0].legend(fontsize=_fs)
	axes[1].legend(fontsize=_fs)
	axes[2].legend(fontsize=_fs)

	fig.show()

	plt.show()

	fig.savefig(f'v_rdf_ce_mul_{_T1}_{_T2}.png', dpi=1200, bbox_inches='tight')
	fig.savefig(f'v_rdf_ce_mul_{_T1}_{_T2}.pdf', format='pdf', dpi=1200, bbox_inches='tight')

# ------------------------------------------------------------------------------

#file_paths = [ f'RDF_{_T}.0_{i}.rdf' for i in range(_max) ]

# setting path 1
#file_paths1 = [ f'{path1}/RDF_{_T1}.0_{(i+1)*3}.rdf' for i in range(8) ]
#file_paths2 = [ f'{path2}/RDF_{_T2}.0_{(i+1)*3}.rdf' for i in range(8) ]

#for i,path in enumerate(file_paths1):
#	file_paths1[i] = os.path.join(os.getcwd(),path)
#for i,path in enumerate(file_paths2):
#	file_paths2[i] = os.path.join(os.getcwd(),path)
#file_paths = (file_paths1, file_paths2)

file_paths1 = [f'RDF_GCE_{_T1}.0_0.125.rdf', f'RDF_GCE_{_T1}.0_0.25.rdf', f'RDF_GCE_{_T1}.0_0.375.rdf', f'RDF_GCE_{_T1}.0_0.5.rdf', f'RDF_GCE_{_T1}.0_0.625.rdf',
            f'RDF_GCE_{_T1}.0_0.75.rdf', f'RDF_GCE_{_T1}.0_0.875.rdf',  f'RDF_GCE_{_T1}.0_1.0.rdf' ]
file_paths2 = [f'RDF_GCE_{_T2}.0_0.125.rdf', f'RDF_GCE_{_T2}.0_0.25.rdf', f'RDF_GCE_{_T2}.0_0.375.rdf', f'RDF_GCE_{_T2}.0_0.5.rdf', f'RDF_GCE_{_T2}.0_0.625.rdf',
            f'RDF_GCE_{_T2}.0_0.75.rdf', f'RDF_GCE_{_T2}.0_0.875.rdf',  f'RDF_GCE_{_T2}.0_1.0.rdf' ]

for i in range(len(file_paths1)):

	file_paths1[i] = os.path.join(path1,file_paths1[i])
	file_paths2[i] = os.path.join(path2,file_paths2[i])

	print(file_paths1[i],file_paths2[i])
file_paths = (file_paths1, file_paths2)

plot_data(file_paths, offset=offset, broadening_sigma=sigma)

