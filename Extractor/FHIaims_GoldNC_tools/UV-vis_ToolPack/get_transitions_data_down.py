import pandas as pd 
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.ticker import MultipleLocator
import seaborn as sns
import json,sys

from Transition import get_trans_int
# def get_trans_int(icube,fcube,verbose=False):

#
# Order: Au[6sp],Au[5d],S[3p],Others
# 

# USER CONTROL
_upspin_homo = 1555
_downspin_homo = 1554
#
# load json
#
_upjson_file = 'selected_up.json'
_downjson_file = 'selected_down.json'
upjson = None
downjson = None
with open(_upjson_file,'r') as log_file:
    print(f' loading ... {_upjson_file}')
    upjson = json.load(log_file)
with open(_downjson_file,'r') as log_file:
    print(f' loading ... {_downjson_file}')
    downjson = json.load(log_file)
#
# setting cube files
#
upfile_list   = 'up_cubelist.dat'
downfile_list = 'down_cubelist.dat'

# linking 'cube' file to upjson
with open(upfile_list,'r') as f:
	next(f) # skip fisrt line
	for line in f:
		ls = line.split()
		state = ls[0]
		filepath = ls[1]
		for key in upjson.keys():
			if key == state:
				upjson[key]['cube'] = filepath
				print(state,upjson[key])
print('')
# linking 'cube' file to downjson
with open(downfile_list,'r') as f:
	next(f) # skip fisrt line
	for line in f:
		ls = line.split()
		state = ls[0]
		filepath = ls[1]
		for key in downjson.keys():
			if key == state:
				downjson[key]['cube'] = filepath
				print(state,downjson[key])
print('')
#
# parsing json : LUMOs / HOMOs
#
up_homo = {}
up_lumo = {}

down_homo = {}
down_lumo = {}

# set upspin homo/lumo
for key in upjson.keys():
	if int(key) <= _upspin_homo:	# if 'key' is same or less than homo_state_number 
		#up_homo[int(key)-_upspin_homo] = upjson[key]
		up_homo[key] = upjson[key]
	else:
		#up_lumo[int(key)-_upspin_homo] = upjson[key]
		up_lumo[key] = upjson[key]
# set downspin homo/lumo
for key in downjson.keys():
	if int(key) <= _downspin_homo:
		#down_homo[int(key)-_downspin_homo] = downjson[key]
		down_homo[key] = downjson[key]
	else:
		#down_lumo[int(key)-_downspin_homo] = downjson[key]
		down_lumo[key] = downjson[key]

# Get HOMO(-X) -----> LUMO(+X) transition spectrum
print(f' * up-spin homo state reference: {_upspin_homo}')
print(f' ! HOMO keys')
print(up_homo.keys()) # listing HOMO states: [ HOMO-0, HOMO-1, HOMO-2 ... HOMO-min ]
print(f' ! LUMO keys')
print(up_lumo.keys()) # listing LUMO states: [ LUMO+max ... LUMO+2, LUMO+1, LUMO+0 ]
print(f' * down-spin homo state reference: {_downspin_homo}')
print(f' ! HOMO keys')
print(down_homo.keys())
print(f' ! LUMO keys')
print(down_lumo.keys())

#print(f' * ----------------------------------------')
#print(f' ! start up-spin transitions')	
#print(f' ! homo_state_i  lumo_state_f  deltaE  transI')
#print(f' * ----------------------------------------')
##
## up-spin
#uptranslist = []
#uptransI = []
##
## printing items: istate fstate exciteE transI
##
## transI : transition dipole (NOT 'oscillator strength')
##
#for istate in up_homo.keys():
#	istate_eval = up_homo[istate]['eval']
#
#	for fstate in up_lumo.keys():
#		fstate_eval = up_lumo[fstate]['eval']
#		transE = fstate_eval - istate_eval
#		uptranslist.append(transE)
#
#		il = int(istate)
#		fl = int(fstate)
#		# print(f'{il:6d}{fl:6d}',end='')
#		#
#		# get transition intensity
#		#
#		
#		# get cube files
#		try:
#			icube_file = up_homo[istate]['cube']
#			fcube_file = up_lumo[fstate]['cube']
#		
#			# get_trans_int(icube,fcube,verbose=False):
#			transI = get_trans_int(icube_file,fcube_file,verbose=False)
#			print(f'{il:6d}{fl:6d}',end='')
#			uptransI.append(transI)
#			#print(f'{il:6d}{fl:6d}{transE:16.8f}{transI:16.8f}')			
#			#print(f'{transE:16.8f}{transI:16.8f}')			
#			print(f'{transE:16.8f}{transI:40.12e}')
#
#		except:
#			print(' Error, json does not have key : cube')
#			sys.exit()

print(f' * ----------------------------------------')
print(f' ! start down-spin transitions')	
print(f' ! homo_state_i  lumo_state_f  deltaE  transI')
print(f' * ----------------------------------------')
#
# down-spin
downtranslist = []
downtransI = []
for istate in down_homo.keys():
	istate_eval = down_homo[istate]['eval']

	for fstate in down_lumo.keys():
		fstate_eval = down_lumo[fstate]['eval']
		transE = fstate_eval - istate_eval
		downtranslist.append(transE)

		il = int(istate)
		fl = int(fstate)
		# print(f'{il:6d}{fl:6d}',end='')
		#
		# get transition intensity
		#

		# get cube files
		try:
			icube_file = down_homo[istate]['cube']
			fcube_file = down_lumo[fstate]['cube']
		
			# get_trans_int(icube,fcube,verbose=False):
			transI = get_trans_int(icube_file,fcube_file,verbose=False)
			print(f'{il:6d}{fl:6d}',end='')
			downtransI.append(transI)
			#print(f'{il:6d}{fl:6d}{transE:16.8f}{transI:16.8f}')			
			#print(f'{transE:16.8f}{transI:16.8f}')			
			print(f'{transE:16.8f}{transI:40.12e}')

		except:
			print(f'{il:6d}{fl:6d} : ',end='')
			print(' Error, json does not have key : cube')
			pass

sys.exit()
