import pandas as pd 
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.ticker import MultipleLocator
import seaborn as sns
import json,sys

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
		up_homo[int(key)-_upspin_homo] = upjson[key]
	else:
		up_lumo[int(key)-_upspin_homo] = upjson[key]
# set downspin homo/lumo
for key in downjson.keys():
	if int(key) <= _downspin_homo:
		down_homo[int(key)-_downspin_homo] = downjson[key]
	else:
		down_lumo[int(key)-_downspin_homo] = downjson[key]

print(f' UP   HOMO/LUMO CNT: {len(up_homo)} / {len(up_lumo)}')
print(f' DOWN HOMO/LUMO CNT: {len(down_homo)} / {len(down_lumo)}')
# Get HOMO(-X) -----> LUMO(+X) transition spectrum

#
# up-spin
uptranslist = []
for istate in up_homo.keys():
	istate_eval = up_homo[istate]['eval']

	for fstate in up_lumo.keys():
		fstate_eval = up_lumo[fstate]['eval']
		transE = fstate_eval - istate_eval
		uptranslist.append(transE)
#
# down-spin
downtranslist = []
for istate in down_homo.keys():
	istate_eval = down_homo[istate]['eval']

	for fstate in down_lumo.keys():
		fstate_eval = down_lumo[fstate]['eval']
		transE = fstate_eval - istate_eval
		downtranslist.append(transE)


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









up_evals = []
down_evals = []
up = {}
down = {}
for key in upjson.keys():
	up_evals.append(upjson[key]['eval'])
	up[key] = upjson[key]['occ']

for key in downjson.keys():
	down_evals.append(downjson[key]['eval'])
	down[key] = downjson[key]['occ']

# overall LUMO -5.577844371450539
# overall HOMO -6.592289964648314
# order: Au_sp,Au_d,S_p,O

# COLOR BANK
#colors_up = ['red','blue','green','gray','black','orange']
colors_up= ['red','blue','green','black','black','orange']
colors_down= ['red','blue','green','black','black','orange']


# ========================================
# PLOTTING
# ========================================
cm = 1/2.54
#fig, ax = plt.subplots(figsize=(10,12))
fig, ax = plt.subplots(1,2)
#fig.set_size_inches((24*cm,30*cm))
fig.set_size_inches((44*cm,30*cm))
# Fig 1 upspin
ax[0].set_xlim(0,1)
ax[0].set_xlabel('Occupancy',fontsize=16)
ax[0].set_ylabel('Energy (eV)',fontsize=16)
ax[0].tick_params(axis='both', labelsize=16)
# Fig 2 downspin
ax[1].set_xlim(0,1)
ax[1].set_xlabel('Occupancy',fontsize=16)
ax[1].set_ylabel('',fontsize=16)
ax[1].tick_params(axis='both', labelsize=16)

for yval,values in zip(up_evals,up.values()):
	values_cum =  np.array(values).cumsum().tolist()
	starts = values_cum - np.array(values)
	ax[0].barh(y=yval,width=values,left=starts,color=colors_up,height=0.015)
	#print(yval,values,values_cum,starts)

for yval,values in zip(down_evals,down.values()):
	values_cum =  np.array(values).cumsum().tolist()
	starts = values_cum - np.array(values)
	ax[1].barh(y=yval,width=values,left=starts,color=colors_down,height=0.015)
	#print(yval,values,values_cum,starts)
##
## simply annotations
##
#
##for p in ax.patches:
##    ax.annotate(str(p.get_x()), xy=(p.get_x(), p.get_y()+0.2))
##plt.legend(bbox_to_anchor=(0, -0.15), loc=3, prop={'size': 14}, frameon=False)
#
# overall LUMO -5.577844371450539
# overall HOMO -6.592289964648314
# order: Au_sp,Au_d,S_p,O
'''     
    plot config
'''     
plt.subplots_adjust(
    left = 0.11,
    bottom = 0.08,
    right = 0.82,
    top = 0.96,
    wspace = 0.200,
    hspace = 0.0
)   

#ax[0].set_ylim(top=-2.5)
ax[0].set_ylim(-7.5,-2.5)
ax[0].yaxis.set_major_locator(MultipleLocator(0.5))
ax[0].yaxis.set_minor_locator(MultipleLocator(0.25))
ax[1].set_ylim(-7.5,-2.5)
ax[1].yaxis.set_major_locator(MultipleLocator(0.5))
ax[1].yaxis.set_minor_locator(MultipleLocator(0.25))
ax[1].set_yticks([])
_fs = 14
#xes[0].set_xlabel('$\it{r}_\mathrm{Li^{+}Li^{+}}$, Å', fontsize=_lfs)
ax[1].plot(0,0, color='red', label='Au$_\mathrm{sp}$')
ax[1].plot(0,0, color='blue', label='Au$_\mathrm{d}$')
ax[1].plot(0,0, color='green', label='S$_\mathrm{p}$')
#ax[1].plot(0,0, color='gray', label='Others spin↑')
#ax[1].plot(0,0, color='black', label='Others spin↓')
ax[1].plot(0,0, color='black', label='Others')

ax[1].legend(fontsize=_fs,bbox_to_anchor=(1.01, 1),loc='upper left')
#ax.legend(fontsize=_fs-2)
plt.show()
fig.set_size_inches((10,12))
fig.savefig(f'sample_orbitals.png')
