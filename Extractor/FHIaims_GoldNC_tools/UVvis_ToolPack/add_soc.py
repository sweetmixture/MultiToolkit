import sys,os,json

_soc_file = 'SOC_eigenvalues.dat'

_selected_up   = 'selected_up.json'
_selected_dn = 'selected_down.json'

# load json
upjson = None
dnjson = None
with open(_selected_up,'r') as f:
	upjson = json.load(f)
with open(_selected_dn,'r') as f:
	dnjson = json.load(f)

# load SOC
with open(_soc_file,'r') as f:

	# find starting part
	for line in f:
		if 'State' in line:
			break;
	# find perturbed (SOC) eigenvalues
	for line in f:
		
		if line.strip() == '':
			break

		ls = line.split()
		evalue = float(ls[2])
		soc_evalue = float(ls[3])

		# find matching eval in upjson
		for key in upjson.keys():
			upeval = float(upjson[key]['eval'])
			err = abs((upeval - evalue)/upeval * 100.)
			# get perturbed evalue
			if err < 0.005:
				upjson[key]['soc_eval'] = soc_evalue
				upjson[key]['soc_err']  = (upjson[key]['eval'] - soc_evalue)/soc_evalue * 100.
		# find matching eval in dnjson
		for key in dnjson.keys():
			dneval = float(dnjson[key]['eval'])
			err = abs((dneval - evalue)/dneval * 100.)
			# get perturbed evalue
			if err < 0.005:
				dnjson[key]['soc_eval'] = soc_evalue
				dnjson[key]['soc_err']  = (dnjson[key]['eval'] - soc_evalue)/soc_evalue * 100.

# dumping soc info added json
_soc_up = 'soc_' + _selected_up
_soc_dn = 'soc_' + _selected_dn
with open(_soc_up,'w') as f:
	json.dump(upjson,f,indent=4)
with open(_soc_dn,'w') as f:
	json.dump(dnjson,f,indent=4)


# processing simpleUV.up.out
_uv_file = 'simpleUV.up.out'
_uv_soc_file = 'soc_simpleUV.up.out'
_soc_result = []
with open(_uv_file,'r') as f:
	for line in f:
		if '0  20  40  60  80 100 120 140 160 180 200 220 240 260' in line:
			ls = line.split()[14:]

			istate = ls[0]
			fstate = ls[1]
			transE = float(ls[2])
			transI = float(ls[3])

			soc_ieval = upjson[istate]['soc_eval']
			soc_feval = upjson[fstate]['soc_eval']
			soc_transE = soc_feval - soc_ieval

			_soc_result.append([istate,fstate,transE,soc_transE,transI])

with open(_uv_soc_file,'w') as f:
	for item in _soc_result:
		# istat fstat transE soc_transE transI
		#     0     1      2          3      4
		f.write(f'{item[0]:6s}{item[1]:6s}{item[2]:20.12f}{item[3]:20.12f}{item[4]:24.12e}\n')
# * END OF UP

# processing simpleUV.dn.out
_uv_file = 'simpleUV.dn.out'
_uv_soc_file = 'soc_simpleUV.dn.out'
_soc_result = []
with open(_uv_file,'r') as f:
	for line in f:
		if '0  20  40  60  80 100 120 140 160 180 200 220 240 260' in line:
			ls = line.split()[14:]

			istate = ls[0]
			fstate = ls[1]
			transE = float(ls[2])
			transI = float(ls[3])

			soc_ieval = dnjson[istate]['soc_eval']
			soc_feval = dnjson[fstate]['soc_eval']
			soc_transE = soc_feval - soc_ieval

			_soc_result.append([istate,fstate,transE,soc_transE,transI])

with open(_uv_soc_file,'w') as f:
	for item in _soc_result:
		# istat fstat transE soc_transE transI
		#     0     1      2          3      4
		f.write(f'{item[0]:6s}{item[1]:6s}{item[2]:20.12f}{item[3]:20.12f}{item[4]:24.12e}\n')
# * END OF DOWN
