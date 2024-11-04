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

#print(f'state     eval      soc_eval')
print(f'   state         eval    soc_eval         Aud        Ausp          Sp           O')
for key in alljson.keys():
	ev = alljson[key]['eval']
	sev= alljson[key]['soc_eval']
	
	Au_d = alljson[key]['Au_d']
	Au_sp= alljson[key]['Au_sp']
	S_p  = alljson[key]['S_p']
	O    = alljson[key]['O']

	if _HOMO_STATE == int(key):
		#print(f' * {key:6s}{ev:12.6f}{sev:12.6f}')
		print(f' * {key:6s}{ev:12.6f}{sev:12.6f}{Au_d:12.6f}{Au_sp:12.6f}{S_p:12.6f}{O:12.6f}')
	else:
		#print(f'   {key:6s}{ev:12.6f}{sev:12.6f}')
		print(f'   {key:6s}{ev:12.6f}{sev:12.6f}{Au_d:12.6f}{Au_sp:12.6f}{S_p:12.6f}{O:12.6f}')

print(f'---------------------------------------')
#print(f' Listing Occupancy')
#print(f'---------------------------------------')

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
clist = ['red','blue','green','grey','black','orange']


# ========================================
# PLOTTING
# ========================================
_fs = 20
cm = 1/2.54
#fig, ax = plt.subplots(figsize=(10,12))
#fig, ax = plt.subplots(1,2)
fig, ax = plt.subplots()
#fig.set_size_inches((44*cm,30*cm))
fig.set_size_inches((16*cm,24*cm))
fig.set_size_inches((24*cm,24*cm))
# Fig 1
ax.set_xlim(0,1)
ax.set_xlabel('Occupancy',fontsize=_fs)
ax.set_ylabel('Energy (eV)',fontsize=_fs)
ax.tick_params(axis='both', labelsize=_fs)

for state in alljson.keys():

	soc_ev = alljson[state]['soc_eval']
	occ_list = [ alljson[state]['Au_sp'], alljson[state]['Au_d'], alljson[state]['S_p'], alljson[state]['O'] ]
	values_cum = np.array(occ_list).cumsum().tolist()
	starts = values_cum - np.array(occ_list)
	ax.barh(y=soc_ev,width=occ_list,left=starts,color=clist,height=_height)

#ymin = -7.2
#ymax = -2.7
#ax.set_ylim(ymin,ymax)
#ax.set_ylim(-7.0,-3.5)
ax.set_ylim(-6.7,-3.5)
ax.yaxis.set_major_locator(MultipleLocator(0.5))
ax.yaxis.set_minor_locator(MultipleLocator(0.1))
#ax.set_yticks([])

ax.plot(0,0, color='red', label='Au$_\mathrm{sp}$')#, fontsize=_fs)
ax.plot(0,0, color='blue', label='Au$_\mathrm{d}$')#, fontsize=_fs)
ax.plot(0,0, color='green', label='S$_\mathrm{p}$')#, fontsize=_fs)
ax.plot(0,0, color='grey', label='Others')
ax.legend(fontsize=_fs-2, loc='upper left', ncol=4, frameon=False)
#ax.legend(fontsize=_fs,bbox_to_anchor=(1.01, 1),loc='upper left')
#ax.legend(fontsize=_fs,bbox_to_anchor=(0.5, -0.0),loc='upper left')
'''     
    plot config
'''     
plt.subplots_adjust(
    left = 0.14,
    bottom = 0.074,
    right = 0.862,
    top = 0.97,
    wspace = 0.200,
    hspace = 0.0
)   
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)



#
# ANNOTATION - Transition Arrow
#
_lw = 0.1

offset = 0.05
dx     = 0.15
n      = 0

# INFO branch: a
# 3108        3110
x = offset + dx * n
st1 = ( x, -6.374836 )
en1 = ( x, -5.422019 )
#ax.annotate('',xy=en1,xytext=st1,arrowprops=dict(facecolor='black', linewidth=_lw, arrowstyle='->'))
ax.annotate('',xy=en1,xytext=st1,arrowprops=dict(facecolor='black', linewidth=_lw))
n += 1

# INFO branch: b
# 3109        3111
x = offset + dx * n - 0.07
st1 = ( x, -6.219205 )
en1 = ( x, -4.661404 )
ax.annotate('',xy=en1,xytext=st1,arrowprops=dict(facecolor='black', linewidth=_lw))
n += 1

# INFO branch: c
# 3106		3112
x = offset + dx * n - 0.14
st1 = ( x, -6.521212 )
en1 = ( x, -4.600147 )
ax.annotate('',xy=en1,xytext=st1,arrowprops=dict(facecolor='black', linewidth=_lw))
n += 1

# -------------------------------------------------------------------------------------

# INFO branch: d
# 3103		3113
x = offset + dx * n + 0.09 - 0.1
st1 = ( x, -6.681749 )
en1 = ( x, -4.249339 )
ax.annotate('',xy=en1,xytext=st1,arrowprops=dict(facecolor='black', linewidth=_lw))
n += 1

# INFO branch: e
# 3104		3114
x = offset + dx * n - 0.09 - 0.1
st1 = ( x, -6.648448 )
en1 = ( x, -4.215337 )
ax.annotate('',xy=en1,xytext=st1,arrowprops=dict(facecolor='black', linewidth=_lw))
n += 1

# INFO branch: f
# 3107		3117
x = offset + dx * n + 0.09 - 0.2
st1 = ( x, -6.493112 )
en1 = ( x, -3.735065 )
ax.annotate('',xy=en1,xytext=st1,arrowprops=dict(facecolor='black', linewidth=_lw))
n += 1

# INFO branch: g
# 3105		3115
x = offset + dx * n - 0.09 - 0.2
st1 = ( x, -6.56376 )
en1 = ( x, -3.805426 )
ax.annotate('',xy=en1,xytext=st1,arrowprops=dict(facecolor='black', linewidth=_lw))
n += 1








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
#fig.savefig(f'sample_orbitals.png')

