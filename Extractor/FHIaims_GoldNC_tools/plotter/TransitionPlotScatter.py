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

# CREATE DUMMY INTENSITY
dummy_int = [ 10. for i in range(len(uptranslist)) ]

ax.scatter(uptranslist,dummy_int,color='r',marker='',s=1)
ax.scatter(downtranslist,dummy_int,color='b',marker='',s=1)
for x,y in zip(uptranslist,dummy_int):
	ax.plot([x,x],[0,y],linestyle='-',color='r',linewidth=0.8)
for x,y in zip(downtranslist,dummy_int):
	ax.plot([x,x],[0,y],linestyle='-',color='b',linewidth=0.8)

#
# create lorentzian cruve
#
def lorentzian(x, x0, gamma, A):
	return A * gamma**2 / ((x - x0)**2 + gamma**2)

_lgamma = 0.15
_xmin = 0
_xmax = 5
_dpoint= 10000
#
# create empty bin
#
uplor = {}
downlor = {}
sumlor = {}
for dp in np.linspace(_xmin,_xmax,_dpoint):
	uplor[dp] = 0.
	downlor[dp] = 0.
	sumlor[dp] = 0.

for x0,A in zip(uptranslist,dummy_int):
	for x in uplor.keys():
		sig = lorentzian(x,x0,_lgamma,A)
		uplor[x] += sig
for x0,A in zip(downtranslist,dummy_int):
	for x in downlor.keys():
		sig = lorentzian(x,x0,_lgamma,A)
		downlor[x] += sig

for key, uplorv, downlorv in zip(sumlor.keys(),uplor.values(),downlor.values()):
	sumlor[key] = uplorv + downlorv

#ax.scatter(uplor.keys(), uplor.values(), color='g', label='Data Points',s=1)
ax.plot(uplor.keys(), uplor.values(), color='r', label=f'spin↑')
ax.plot(downlor.keys(), downlor.values(), color='b', label=f'spin↓')
ax.plot(sumlor.keys(), sumlor.values(), color='g', label=f'spin↑ + spin↓')

# READ EXP data
_exp_file = 'exp.uv.dat'
expx = []
expI = []
with open(_exp_file, 'r') as file:
	for line in file:
		if line.strip():  # Ignore empty lines
			values = line.split()  # Split the line into values
			expx.append(float(values[0]))  # Third column as x-values
			expI.append(float(values[1]))  # Fourth column as y-values
##
## USER CONTROL: adjusting 'intensity' of EXP data
##
expImax = max(expI)
expI = np.array(expI)
expI = expI / expImax * 330.
ax.plot(expx,expI,color='black',linestyle='--', label=f'Expr.')

# Legend
_fs = 16
ax.legend(fontsize=_fs)

#ax.set_xlabel('Energy (eV)', fontsize=14)
ax.set_xlabel('$\it{E}$$_\mathrm{f}$ - $\it{E}$$_\mathrm{i}$ (eV)', fontsize=_fs)
ax.set_ylabel('$\it{I}$ (a.u.)', fontsize=_fs)
ax.set_xlim(0.5,4)
ax.set_xlim(0.5,3.25)
ax.set_xlim(0.5,3.5)
ax.set_ylim(bottom=0)
ax.set_yticks([])

ax.tick_params(axis='x', labelsize=14)  # Corrected line

ax.xaxis.set_minor_locator(MultipleLocator(0.1))
ax.xaxis.set_major_locator(MultipleLocator(0.5))



plt.show()

_file_name = 'transFigNoDP'
_file_png = _file_name + '.png'
_file_pdf = _file_name + '.pdf'
try:
    _file_name = sys.argv[1]    # if nothing then failed
    _file_png = _file_name + '.png'
    _file_pdf = _file_name + '.pdf'
except:
    pass

print('saving')
fig.savefig(f'{_file_png}', dpi=800, bbox_inches='tight')
fig.savefig(f'{_file_pdf}', format='pdf', dpi=800, bbox_inches='tight')

sys.exit()















upbins = np.histogram_bin_edges(uptranslist,bins='fd')
#ble = upbins[0]
#bre = upbins[-1]
#bin_count = 120
#dbin = (bre - ble)/bin_count
#bins = []
#for i in range(bin_count):
#	 bins.append(ble + float(i)*dbin)
#upbins = np.array(bins)

downbins = np.histogram_bin_edges(downtranslist,bins='fd')
#ble = downbins[0]
#bre = downbins[-1]
#bin_count = 120
#dbin = (bre - ble)/bin_count
#bins = []
#for i in range(bin_count):
#	 bins.append(ble + float(i)*dbin)
#downbins = np.array(bins)

bwa = 0.38
stat = 'density' # 'probability'
sns.histplot(uptranslist,  kde=True,kde_kws={'bw_adjust': bwa},stat=stat,color='black',element='step',bins=upbins)
sns.histplot(downtranslist,kde=True,kde_kws={'bw_adjust': bwa},stat=stat,color='gray',element='step',bins=downbins)

_imagefile = 'NoSelectionRule'
fig.savefig(f'{_imagefile}.png', dpi=1200, bbox_inches='tight')
fig.savefig(f'{_imagefile}.pdf', format='pdf', dpi=1200, bbox_inches='tight')
plt.show()

_file_name = 'transFigNoDP'
_file_png = _file_name + '.png'
_file_pdf = _file_name + '.pdf'
try:
    _file_name = sys.argv[1]    # if nothing then failed
    _file_png = _file_name + '.png'
    _file_pdf = _file_name + '.pdf'
except:
    pass

print('saving')
fig.savefig(f'{_file_png}', dpi=800, bbox_inches='tight')
fig.savefig(f'{_file_pdf}', format='pdf', dpi=800, bbox_inches='tight')

sys.exit()
