#!/bin/python3
import os,sys
from Extractor.GULP import ExtractGULP

_file = '/work/e05/e05/wkjee/Masters/Zirui2023/MnO/shelOnly/li1/A0/gulp_klmc.gout'
_file = '/work/e05/e05/wkjee/Masters/Zirui2023/MnO/coreOnly/li1/A0/gulp_klmc.gout'

gex = ExtractGULP()
gex.set_output_file(_file)
gex.check_finish_normal()

print(f'* check status')
print(f'status:',gex.check_status())

print(f'')
print(f'Extracting ...')
print(f'')
# ------------------------------------- INITIAL 
ilvec = gex.get_initial_lvectors()[1]
ien = gex.get_initial_energy()[1]
ienf= gex.get_initial_energy_full()[1]	# IP / elec re / elec im / elec full
iconf = gex.get_initial_frac_cosh()[1]	# core-shell (cosh)


print(f' * * * INITIAL * * * ')
print(f'initial energy : {ien:9f}')
print(f'initial energy decomp: ',ienf)

print(f'lattice vectors')
for vec in ilvec:
	print(vec)
print(f'configuration')
for atom in iconf:
	print(atom)

# ------------------------------------- FINAL
flvec = gex.get_final_lvectors()[1]
print(flvec)	# if 'conp' done --> flvec == None !!!
fen = gex.get_final_energy()[1]
fenf= gex.get_final_energy_full()[1]	# IP / elec re / elec im / elec full
fconf = gex.get_final_frac_cosh()[1]	# core-shell (cosh)
print(f'')
print(f' * * * FINAL * * *')
print(f'final  energy : {fen:9f}')
print(f'final  energy decomp: ',fenf)

print(f'lattice vectors')
if flvec is not None:
	for vec in flvec:
		print(vec)
print(f'configuration')
for atom in fconf:
	print(atom)













sys.exit()

print('* final frac check')
frac = gex.get_final_frac()
print(type(frac))
print(frac)
for item in frac[1]:
	print(item)

