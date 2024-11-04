import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator
import numpy as np
import sys

# Define the file path of your dataset
#_new_up_filepath = 'upsample.pbe0.log'

dataset = 'b3lyp'
#dataset = 'pbe0'

#_new_up_filepath   = f'upsample.{dataset}.log'
#_new_down_filepath = f'dnsample.{dataset}.log'
_filepath   = f'uv_soc_res.out'

# Read the dataset from the file
trans_state = []
trans_gap = []
trans_int  = []
trans_dipole2 = []
with open(_filepath, 'r') as file:
	for line in file:
		if line.strip():  # Ignore empty lines
			values = line.split()  # Split the line into values

			istate = int(values[0])
			fstate = int(values[1])

			istate_eval = float(values[2])
			fstate_eval = float(values[3])

			egap = fstate_eval - istate_eval

			trans_gap.append(egap)
			trans_int.append(2./3. * egap * float(values[4]))
			trans_state.append((istate,fstate))
			trans_dipole2.append(float(values[4]))
			#upev.append(float(values[2]))  # Third column as x-values
			#uptransI.append(2./3.*float(values[2])*float(values[4]))  # Fourth column as y-values

#
# Shifting Trans Gap
#
shift = float(sys.argv[1]) # 0.301
trans_gap = ( np.array(trans_gap) + shift ).tolist()


print(f'* --------------------------------------------------------')
print(f'* Transition Info')
print(f'* --------------------------------------------------------')
print(f'* is    fs      ∂E            ∑          µ^2')
print(f'* --------------------------------------------------------')

for state,gap,Int,dip2 in zip(trans_state,trans_gap,trans_int,trans_dipole2):
	print(f'{state[0]:6d}{state[1]:6d}{gap:12.6f}{Int:24.12f}{dip2:24.12f}')


_Iscale = 0.00005
_Iscale = 0.00010 # pbe0
_Iscale = 0.000033 # b3lyp
_Iscale = 0.000025 # b3lyp
_Iscale = 0.00003625 # b3lyp
scale_transI = (np.array(trans_int)*_Iscale).tolist()

# Create a figure and a single subplot (axes)
cm = 1/2.54
fig, ax = plt.subplots()
fig.set_size_inches((24*cm,30*cm))
plt.subplots_adjust(
	left = 0.11,
	bottom = 0.08,
	right = 0.95,
	top = 0.96,
	wspace = 0.200,
	hspace = 0.0
)

# Plot scatter plot with lines to 0
#ax.scatter(trans_gap, trans_int, color='b', marker='',s=1)
#for x, y in zip(trans_gap,trans_int):
#	ax.plot([x, x], [0, y], linestyle='-', color='b', linewidth=0.8)
ax.scatter(trans_gap, scale_transI, color='b', marker='',s=1)
for x, y in zip(trans_gap,scale_transI):
	ax.plot([x, x], [0, y], linestyle='-', color='b', linewidth=0.8)


#
# create lorentzian cruve
#
def lorentzian(x, x0, gamma, A):
	return A * gamma**2 / ((x - x0)**2 + gamma**2)

_lgamma = 0.15	# figutrans_intated on GoogleDrive
_lgamma = 0.20	# trial
_lgamma = 0.14	# trial
_lgamma = 0.15	# trial

_lgamma = 0.15	# trial b3lyp
_lgamma = 0.15	# trial b3lyp
_xmin = 0
_xmax = 5
_dpoint= 10000
#
# create empty bin
#
lor = {}	# lorentzian applied
for dp in np.linspace(_xmin,_xmax,_dpoint):
	lor[dp] = 0.

for x0,A in zip(trans_gap,scale_transI):
	for x in lor.keys():
		sig = lorentzian(x,x0,_lgamma,A)
		lor[x] += sig

ax.plot(list(lor.keys()), list(lor.values()), color='b', label=f'DFT')
#ax.plot(list(lor.keys()  ), list(lor.values()  ), color='r', label=f'spin↑')
#ax.plot(list(newuplor.keys()  ), list(newuplor.values()  ), color='r', label=f'spin↑ SOC',linestyle='--')
#ax.plot(list(downlor.keys()), list(downlor.values()), color='b', label=f'spin↓')
#ax.plot(list(newdownlor.keys()), list(newdownlor.values()), color='b', label=f'spin↓ SOC',linestyle='--')
#ax.plot(list(sumlor.keys() ), list(sumlor.values() ), color='g', label=f'spin↑ + spin↓')
#ax.plot(list(newsumlor.keys() ), list(newsumlor.values() ), color='g', label=f'spin↑ + spin↓ SOC',linestyle='--')
#plt.show()
#sys.exit()

##
## READ EXP data
##
_exp_scaling = 600.
#
#_exp_file = 'exp.uv.dat'
#expx = []
#expI = []
#with open(_exp_file, 'r') as file:
#	for line in file:
#		if line.strip():  # Ignore empty lines
#			values = line.split()  # Split the line into values
#			expx.append(float(values[0]))  # Third column as x-values
#			expI.append(float(values[1]))  # Fourth column as y-values
###
### USER CONTROL: adjusting 'intensity' of EXP data
###
#expImax = max(expI)
#expI = np.array(expI)
#expI = expI / expImax * _exp_scaling
#ax.plot(expx,expI,color='black',linestyle='--', label=f'Exp.1')

# READ EXP data 2
_exp_file2 = 'exp2.uv.dat'
expx2 = []
expI2 = []
with open(_exp_file2, 'r') as file:
	for line in file:
		if line.strip():  # Ignore empty lines
			values = line.split()  # Split the line into values
			expx2.append(float(values[0]))  # Third column as x-values
			expI2.append(float(values[1]))  # Fourth column as y-values
##
## USER CONTROL: adjusting 'intensity' of EXP data
##
expImax2 = max(expI2)
expI2 = np.array(expI2)
expI2 = expI2 / expImax2 * _exp_scaling
ax.plot(expx2,expI2,color='black',linestyle='-.', label=f'Experimental')


# Legend
_fs = 16
#ax.legend(fontsize=_fs)
ax.legend(fontsize=_fs, loc='upper left')

#ax.set_xlabel('Energy (eV)', fontsize=14)
ax.set_xlabel('$\it{E}$$_\mathrm{f}$ - $\it{E}$$_\mathrm{i}$ (eV)', fontsize=_fs)
ax.set_ylabel('$\it{I}$ (a.u.)', fontsize=_fs)
ax.set_xlim(0.5,4)
ax.set_xlim(0.5,3.25)
ax.set_xlim(0.5,3.5)
ax.set_xlim(0.5,3.0)
ax.set_xlim(0.5,3.5)
ax.set_ylim(bottom=0)
ax.set_ylim(top=400.)
ax.set_yticks([])

ax.tick_params(axis='x', labelsize=14)	# Corrected line

ax.xaxis.set_minor_locator(MultipleLocator(0.1))
ax.xaxis.set_major_locator(MultipleLocator(0.5))

#ax.set_title('Scatter Plot with Lines to 0')
#ax.legend()
#ax.grid(True)
# Show the plot
plt.show()

_file_name = 'transFig_SOC'
_file_png = _file_name + f'.{dataset}' + '.png'
_file_pdf = _file_name + f'.{dataset}' + '.pdf'
#try:
#	_file_name = sys.argv[1]	# if nothing then failed
#	_file_png = _file_name + f'.{dataset}' + '.png'
#	_file_pdf = _file_name + f'.{dataset}' + '.pdf'
#except:
#	pass

#fig.savefig(f'{_file_png}', dpi=800, bbox_inches='tight')
#fig.savefig(f'{_file_pdf}', format='pdf', dpi=800, bbox_inches='tight')
sys.exit()
