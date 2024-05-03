import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator
import numpy as np
from scipy.ndimage import gaussian_filter1d

# Function to plot data with offset and Gaussian broadening

# Example usage
_T   = 10
_max = 24

offset = 12
sigma = 3

'''
	color scheme
'''
c_1 = 'lime'    # LiLi	(3)
c_2 = 'violet'  # TcTc	(4)
c_3 = 'aqua'    # LiTc	(7)

def plot_data(file_paths, offset=offset, broadening_sigma=sigma):

	global _T

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

	axes[0].set_xlabel('Li$^{+}$-Li$^{+}$ (Å)', fontsize=_fs)
	axes[1].set_xlabel('Mn$^{3+}$-Mn$^{3+}$ (Å)', fontsize=_fs)
	axes[2].set_xlabel('Mn$^{3+}$-Li$^{+}$ (Å)', fontsize=_fs)

	for i,ax in enumerate(axes):
		ax.tick_params(axis='x', labelsize=_fs)  # Corrected line
		#ax.tick_params(axis='y', labelsize=_fs)  # Corrected line
		ax.set_xlim(1.5, 8.0)

		ax.xaxis.set_major_locator(MultipleLocator(1))
		ax.xaxis.set_minor_locator(MultipleLocator(0.5))

		ax.set_yticks([])
		if i == 0:
			ax.set_ylabel('RDF (a.u.)', fontsize=_fs)
	
	axes[0].legend([f'{_T} K'])
	axes[1].legend([f'{_T} K'])
	axes[2].legend([f'{_T} K'])

	# ----------------------------------------------------------

	for i, file_path in enumerate(file_paths):
		# Read data from file
		with open(file_path, 'r') as file:
			#data = np.loadtxt(file, skiprows=2)
			data = np.loadtxt(file)
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
			axes[0].plot(x, y_broadened1 + y_offset, color=c_1, label=f'{_T} K')
			axes[1].plot(x, y_broadened2 + y_offset, color=c_2, label=f'{_T} K')
			axes[2].plot(x, y_broadened3 + y_offset, color=c_3, label=f'{_T} K')
		else:
			axes[0].plot(x, y_broadened1 + y_offset, color=c_1)
			axes[1].plot(x, y_broadened2 + y_offset, color=c_2)
			axes[2].plot(x, y_broadened3 + y_offset, color=c_3)

	axes[0].legend()
	axes[1].legend()
	axes[2].legend()

	plt.show()

	fig.savefig(f'rdf_ce_{_T}.png', dpi=1200, bbox_inches='tight')
	fig.savefig(f'rdf_ce_{_T}.pdf', format='pdf', dpi=1200, bbox_inches='tight')


#file_paths = [ f'RDF_{_T}.0_{i}.rdf' for i in range(_max) ]
file_paths = [ f'RDF_{_T}.0_{(i+1)*3}.rdf' for i in range(8) ]



plot_data(file_paths)
