#
#   03.2024 W.Jee 
#
#   KLMC Solid Solution: scripts for production phase
#
'''
    Xingfan Zhang, 12/2023
    Woongkyu Jee, 12/203

    * note that this code running must be followed after converting all gulp generated cif to standardised 'cif': see 'KLMC_convert_gulp_cif_to_standard.py'

    * note that to execute this script, you must prepare summary csv file for a taskfarming run: see /MnO-Li/MnO_ProductionPhase_PostScripting/ShellConp/KLMC_PoolGulpEx.py
      -> xrd simulation performed based on 'taskid' given in the csv file
'''
# USER DEFINE ----
_target_cif_file = 'std.cif' # standard 'cif' file !!!!! NOT GULP generated 'cif' file (for its conversion see KLMC_convert_gulp_cif_to_standard.py)
_xrd_wavelength = 1.54059 # in Angstrom for Cu Ka generator
_two_theta_min_input = 10 # ttheta start
_two_theta_max_input = 90 # ttheta end
_output_xrd_filename = 'powderXRD.txt'
# USER DEFINE ----


# -----------------------------------------------------------------------------
import os,sys
import numpy as np
import pandas as pd

import Dans_Diffraction as dif

#from concurrent.futures import ProcessPoolExecutor

_wavelength = _xrd_wavelength
#_energy_kev = 8.0478	# --> _wavelength
#              8.047853674810085

def get_xrd(file):

	global _wavelength
	global _two_theta_min_input, _two_theta_max_input
	global _output_xrd_filename
	#global _energy_kev 

	cif_file = file

	xtl = dif.Crystal(cif_file)

	energy_kev = dif.fc.wave2energy(_wavelength)
	print(energy_kev)

	#
	# 1st arg : 'neutron', 'x-ray'
	# deprecates
	# xtl.Scatter.setup_scatter(type='x-ray',energy_keV=_energy_kev)
	# xtl.Scatter.print_all_refelctions()

	#
	# setting min/max 2theta value
	# suppressing priting output -> false
	# 
	xtl.Scatter.setup_scatter(min_twotheta=_two_theta_min_input, max_twotheta=_two_theta_max_input,output=False)
	
	# run XRD
	twotheta, intensity, reflections = xtl.Scatter.powder('x-ray', units='twotheta', energy_kev=energy_kev, peak_width=0.01, background=0)
	
	# normalise 'intensity'
	nfactor = np.linalg.norm(intensity)
	intensity = intensity / nfactor

	# extrating all elements in the first dimension
	twotheta = twotheta[:].tolist()
	intensity= intensity[:].tolist()

	#print('shape intensity : ',intensity.shape) # (length,)
	#print('shape twotheta  : ',twotheta.shape)	# (length,)

	# ! return type 'numpy.ndarray' 
	# ! print(reflections,type(reflections))

	with open(f'{_output_xrd_filename}','w') as f:
		for tt,signal in zip(twotheta,intensity):
			contents = f'{tt} , {signal}\n'
			f.write(contents)

if __name__ == '__main__':

	file = _target_cif_file
	get_xrd(file)
