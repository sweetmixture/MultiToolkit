import pandas as pd 
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.ticker import MultipleLocator
import json,sys,copy

#
# Order: Au[6sp],Au[5d],S[3p],Others : HOMO State - 3109
# 
_HOMO_STATE = 3109
#
# load json
#
_homojson_file = 'homo_occ.json'
_lumojson_file = 'lumo_occ.json'

print(f'---------------------------------------')
with open(_homojson_file,'r') as log_file:
    print(f' loading ... {_homojson_file}')
    homojson = json.load(log_file)
with open(_lumojson_file,'r') as log_file:
    print(f' loading ... {_lumojson_file}')
    lumojson = json.load(log_file)
print(f'---------------------------------------')
# merge: homojson + lumojson
homojson.update(lumojson)
alljson = homojson

print(f'state     eval      soc_eval')
print(f'---------------------------------------')
for key in alljson.keys():
	ev = alljson[key]['eval']
	sev= alljson[key]['soc_eval']
	if _HOMO_STATE == int(key):
		print(f' * {key:6s}{ev:12.6f}{sev:12.6f}{
	else:
		print(f'   {key:6s}{ev:12.6f}{sev:12.6f}')

print(f'---------------------------------------')

#
# alljson<dict>
#"state": 3101,
#"eval": -6.819686,
#"soc_eval": -6.744122,
#"Au_d": 0.3340681572601996,
#"Au_sp": 0.10499049652114065,
#"S_p": 0.4308686922093148,
#"O": 0.1300726540093463,
#"occ_sum": 1.0000000000000013,
#"up_frac": 0.8253866306940105,
#"dn_frac": 0.17461336930598895
#

# overall LUMO -5.577844371450539
# overall HOMO -6.592289964648314
# order: Au_sp,Au_d,S_p,O

# COLOR BANK
#colors_up = ['red','blue','green','gray','black','orange']
colors_up= ['red','blue','green','black','black','orange']
colors_down= ['red','blue','green','black','black','orange']

_height = 0.015
_height = 0.005
_height = 0.010
clist = ['red','blue','green','black','black','orange']


# ========================================
# PLOTTING
# ========================================
cm = 1/2.54
#fig, ax = plt.subplots(figsize=(10,12))
#fig, ax = plt.subplots(1,2)
fig, ax = plt.subplots()
#fig.set_size_inches((44*cm,30*cm))
fig.set_size_inches((16*cm,24*cm))
# Fig 1
ax.set_xlim(0,1)
ax.set_xlabel('Occupancy',fontsize=16)
ax.set_ylabel('Energy (eV)',fontsize=16)
ax.tick_params(axis='both', labelsize=16)

for state in alljson.keys():

	soc_ev = alljson[state]['soc_eval']
	occ_list = [ alljson[state]['Au_sp'], alljson[state]['Au_d'], alljson[state]['S_p'], alljson[state]['O'] ]
	values_cum = np.array(occ_list).cumsum().tolist()
	starts = values_cum - np.array(occ_list)
	ax.barh(y=soc_ev,width=occ_list,left=starts,color=clist,height=_height)

#ymin = -7.2
#ymax = -2.7
#ax.set_ylim(ymin,ymax)
ax.set_ylim(-7.0,-3.5)
ax.yaxis.set_major_locator(MultipleLocator(0.5))
ax.yaxis.set_minor_locator(MultipleLocator(0.1))
#ax.set_yticks([])

_fs = 14
ax.plot(0,0, color='red', label='Au$_\mathrm{sp}$')
ax.plot(0,0, color='blue', label='Au$_\mathrm{d}$')
ax.plot(0,0, color='green', label='S$_\mathrm{p}$')
ax.plot(0,0, color='black', label='Others')
#ax.legend(fontsize=_fs,bbox_to_anchor=(1.01, 1),loc='upper left')
#ax.legend(fontsize=_fs,bbox_to_anchor=(0.5, -0.0),loc='upper left')
'''     
    plot config
'''     
plt.subplots_adjust(
    left = 0.19,
    bottom = 0.074,
    right = 0.94,
    top = 0.95,
    wspace = 0.200,
    hspace = 0.0
)   


plt.show()
fig.savefig(f'sample_orbitals.png')
sys.exit()

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
    left = 0.19,
    bottom = 0.074,
    right = 0.94,
    top = 0.95,
    wspace = 0.200,
    hspace = 0.0
)   

#ax[0].set_ylim(top=-2.5)
ax[0].set_ylim(-7.5,-2.5)
ax[0].set_ylim(-6.8,-3.6)
ax[0].yaxis.set_major_locator(MultipleLocator(0.25))
ax[0].yaxis.set_minor_locator(MultipleLocator(0.125))
#ax[1].set_ylim(-7.5,-2.5)
#ax[1].yaxis.set_major_locator(MultipleLocator(0.5))
#ax[1].yaxis.set_minor_locator(MultipleLocator(0.25))
#ax[1].set_yticks([])
_fs = 14
#axes[0].set_xlabel('$\it{r}_\mathrm{Li^{+}Li^{+}}$, Å', fontsize=_lfs)
#ax[1].plot(0,0, color='red', label='Au$_\mathrm{sp}$')
#ax[1].plot(0,0, color='blue', label='Au$_\mathrm{d}$')
#ax[1].plot(0,0, color='green', label='S$_\mathrm{p}$')
#ax[1].plot(0,0, color='gray', label='Others spin↑')
#ax[1].plot(0,0, color='black', label='Others spin↓')
#ax[1].plot(0,0, color='black', label='Others')

#ax[1].legend(fontsize=_fs,bbox_to_anchor=(1.01, 1),loc='upper left')
#ax.legend(fontsize=_fs-2)
plt.show()
fig.set_size_inches((10,12))
fig.savefig(f'sample_orbitals.png')
