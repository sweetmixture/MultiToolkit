#!/bin/python

'''
    Xingfan Zhang, 12/2023
    Woongkyu Jee, 12/203
'''

import os,sys
import numpy as np
import pandas as pd

import Dans_Diffraction as dif

#from concurrent.futures import ProcessPoolExecutor

_wavelength = 1.54059
#_energy_kev = 8.0478	# --> _wavelength
#              8.047853674810085

def get_xrd(file):

	global _wavelength
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
	xtl.Scatter.setup_scatter(min_twotheta=10, max_twotheta=90,output=False)
	
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

	with open('powder.txt','w') as f:
		for tt,signal in zip(twotheta,intensity):
			contents = f'{tt} , {signal}\n'
			f.write(contents)

if __name__ == '__main__':

	file = sys.argv[1]
	get_xrd(file)