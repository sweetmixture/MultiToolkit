from KLMCGeometryHandler import KLMCGeometryHandler

_prefix = 'full_qubo_'
#_prefix = 'na_only_qubo_'
_suffix = '.cif'

files = []

klmc_index = 0
for index in range(4,72,4):

	filename = _prefix + str(index) + _suffix

	# get geometry
	lattice = KLMCGeometryHandler(filename)

	# opti conp ...
	keywords = 'opti conp property full nosymm phon comp'
	#keywords = 'opti conp dist'
	#keywords = 'single dist'

	# opti conv
	#keywords = 'opti conv'

	optionfile = '/work/e05/e05/wkjee/Software/MultiToolkit/utils_byProjects/KLMCtools/StdGeometry_toGULP/low_E_structures/gulp_NFP_footer'

	outfile = 'A'+str(klmc_index)+'.gin'
	lattice.write_gulp_input(keywords=keywords,optionfile=optionfile,fileout=outfile)
	klmc_index += 1
