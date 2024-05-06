import pandas as pd 
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.ticker import MultipleLocator
import json,sys

#
# Order: Au[6sp],Au[5d],S[3p],Others
# 

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
# parsing json
#
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
