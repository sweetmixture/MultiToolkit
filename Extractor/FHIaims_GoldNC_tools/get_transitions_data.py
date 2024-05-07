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
# parsing json : LUMOs / HOMOs
#
up_homo = {}
up_lumo = {}

down_homo = {}
down_lumo = {}

# set upspin homo/lumo
for key in upjson.keys():
	if int(key) <= _upspin_homo:
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
print(up_homo.keys())
print(f' ! LUMO keys')
print(up_lumo.keys())
print(f' * down-spin homo state reference: {_downspin_homo}')
print(f' ! HOMO keys')
print(down_homo.keys())
print(f' ! LUMO keys')
print(down_lumo.keys())

print(f' * ----------------------------------------')
print(f' ! start up-spin transitions')	
print(f' ! homo_state_i  lumo_state_f  deltaE  transI')
print(f' * ----------------------------------------')
#
# up-spin
uptranslist = []
uptransI = []
for istate in up_homo.keys():
	istate_eval = up_homo[istate]['eval']

	for fstate in up_lumo.keys():
		fstate_eval = up_lumo[fstate]['eval']
		transE = fstate_eval - istate_eval
		uptranslist.append(transE)

		il = int(istate)
		fl = int(fstate)
		print(f'{il:6d}{fl:6d}',end='')
		#
		# get transition intensity
		#
		
		# get cube files
		try:
			icube_file = up_homo[istate]['cube']
			fcube_file = up_lumo[fstate]['cube']
		
			# get_trans_int(icube,fcube,verbose=False):
			transI = get_trans_int(icube_file,fcube_file,verbose=False)
			uptransI.append(transI)
			#print(f'{il:6d}{fl:6d}{transE:16.8f}{transI:16.8f}')			
			print(f'{transE:16.8f}{transI:16.8f}')			

		except:
			print(' Error, json does not have key : cube')
			sys.exit()

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
		print(f'{il:6d}{fl:6d}',end='')
		#
		# get transition intensity
		#

		# get cube files
		try:
			icube_file = down_homo[istate]['cube']
			fcube_file = down_lumo[fstate]['cube']
		
			# get_trans_int(icube,fcube,verbose=False):
			transI = get_trans_int(icube_file,fcube_file,verbose=False)
			downtransI.append(transI)
			#print(f'{il:6d}{fl:6d}{transE:16.8f}{transI:16.8f}')			
			print(f'{transE:16.8f}{transI:16.8f}')			

		except:
			print(' Error, json does not have key : cube')
			sys.exit()
sys.exit()








#
# use uptranslist / downtranslist : histogram plot
#

# ========================================
# PLOTTING
# ========================================
cm = 1/2.54
fig, ax = plt.subplots()   # 5 (rows) x 1 (cols)
fig.set_size_inches((24*cm,30*cm))
plt.subplots_adjust(
    left = 0.11,
    bottom = 0.08,
    right = 0.82,
    top = 0.96,
    wspace = 0.200,
    hspace = 0.0
)   


upbins = np.histogram_bin_edges(uptranslist,bins='fd')
#ble = upbins[0]
#bre = upbins[-1]
#bin_count = 120
#dbin = (bre - ble)/bin_count
#bins = []
#for i in range(bin_count):
#    bins.append(ble + float(i)*dbin)
#upbins = np.array(bins)

downbins = np.histogram_bin_edges(downtranslist,bins='fd')
#ble = downbins[0]
#bre = downbins[-1]
#bin_count = 120
#dbin = (bre - ble)/bin_count
#bins = []
#for i in range(bin_count):
#    bins.append(ble + float(i)*dbin)
#downbins = np.array(bins)

bwa = 0.38
stat = 'density' # 'probability'
sns.histplot(uptranslist,  kde=True,kde_kws={'bw_adjust': bwa},stat=stat,color='black',element='step',bins=upbins)
sns.histplot(downtranslist,kde=True,kde_kws={'bw_adjust': bwa},stat=stat,color='gray',element='step',bins=downbins)

_imagefile = 'NoSelectionRule'
fig.savefig(f'{_imagefile}.png', dpi=1200, bbox_inches='tight')
fig.savefig(f'{_imagefile}.pdf', format='pdf', dpi=1200, bbox_inches='tight')
plt.show()

sys.exit()
