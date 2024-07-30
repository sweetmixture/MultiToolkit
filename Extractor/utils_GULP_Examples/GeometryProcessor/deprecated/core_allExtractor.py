#!/bin/python3
from Extractor.GULP import ExtractGULP

_file = '/work/e05/e05/wkjee/Masters/Zirui2023/MnO/coreOnly/li1/A0/gulp_klmc.gout'

gex = ExtractGULP()
gex.set_output_file(_file)
gex.check_finish_normal()

print('* check status')
print(gex.check_status())

print('* final frac check')
frac = gex.get_final_frac()
print(type(frac))
print(frac)
for item in frac[1]:
	print(item)

