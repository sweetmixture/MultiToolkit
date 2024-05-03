# 03.2024 W.JEE
# KLMC Solid Soultion
#
# this script collect general information from task-farming GULP run : should be used for final result production 
#
# !!! TO USE THIS SCRIPT, YOU MUST INSTALL ;https://github.com/sweetmixture/MultiToolkit.git;
#
# ! as a result of this script, you will get a 'csv' file that can be further used for : 'rdf'/'xrd' simulations
# ! result csv file will contain ...
#   lattice parameters : a,b,c,alp,beta,gamma,volume,bulkmod,compressibility,dielectric constants
#
# > 'RDF' radial distribution function - see :
# > 'XRD' X-ray diffraction simulations- see :
#

from Extractor.GULP import ExtractGULP
from concurrent.futures import ProcessPoolExecutor
import os,sys
import pandas as pd

# USER DEFINE ----
_csv_filename = 'summary.csv' # final csv file name (saving results)
_max_threads = 32 # number of cpus to use
_max_value = 100 # ending output tag (number of GULP outputs to extract, e.g., A0 ~ A${_max_value})
# USER DEFINE ----

def get_gulp_output(fname,__gtol):

	root = os.getcwd()
	fpath = os.path.join(root,fname)

	eg = ExtractGULP()
	fcheck = eg.set_output_file(fpath)

	if fcheck :

		finish_check = eg.check_finish_normal()
		gnorm_check, gnorm = eg.get_final_gnorm(gnorm_tol=__gtol)
	
		checklist = [] 

		if finish_check == True and gnorm_check == True:

			# Final Energy 
			lenergy, energy = eg.get_final_energy()		
			checklist.append(lenergy)
			# Final Lattice Parameters
			llparams, lparams = eg.get_final_lparams()
			checklist.append(llparams)
			# Final Volume
			lvolume, volume = eg.get_final_lvolume()
			checklist.append(lvolume)	
			# Final Bulk Modulus
			lbulkmod, bulkmod = eg.get_bulkmod()
			checklist.append(lbulkmod)
			# Final Youngs Modulus
			lymod, ymod = eg.get_youngsmod()
			checklist.append(lymod)
			# Final Compressibility
			lcompr, compr = eg.get_compress()
			checklist.append(lcompr)
			# Final static dielec
			lsdielec, sdielec = eg.get_sdielec()
			checklist.append(lsdielec)
			# Final high freq dielec
			lhdielec, hdielec = eg.get_hdielec()
			checklist.append(lhdielec)
		else:
			eg.reset()
			return False, None
		
		if False in checklist:	# any fail(s) detected
			eg.reset()
			return False, None
		else:					# all checklist True
			eg.reset()
			ret = {	'energy': energy,
					# lattice params
					'a'     : lparams[0],
					'b'     : lparams[1],
					'c'     : lparams[2],
					'alp'   : lparams[3],
					'bet'   : lparams[4],
					'gam'   : lparams[5],
					# volume
					'vol'   : volume,
					# Modulus
					'bulkmod'	: bulkmod[1],
					'ymod'		: ymod[1],
					# Compress
					'comp'		: compr,
					# static dielec
					'sd1'		: sdielec[0][0][0],
					'sd2'		: sdielec[0][0][1],
					'sd3'		: sdielec[0][0][2],
					'sd4'		: sdielec[0][1][1],
					'sd5'		: sdielec[0][1][2],
					'sd6'		: sdielec[0][2][2],
					'sde1'		: sdielec[1][0],
					'sde2'		: sdielec[1][0],
					'sde3'		: sdielec[1][0],
					# high freq dielec
					'hd1'		: hdielec[0][0][0],
					'hd2'		: hdielec[0][0][1],
					'hd3'		: hdielec[0][0][2],
					'hd4'		: hdielec[0][1][1],
					'hd5'		: hdielec[0][1][2],
					'hd6'		: hdielec[0][2][2],
					'hde1'		: hdielec[1][0],
					'hde2'		: hdielec[1][0],
					'hde3'		: hdielec[1][0],
			}
			return True, ret
	else:
		eg.reset()
		return False, None

if __name__ == '__main__':

	_MAX_ITEM = _max_value

	dir_path = os.getcwd()	#sys.argv[1]	# only req input parameter -> summary directory path abs
	#dir_path = sys.argv[1]	# only req input parameter -> summary directory path abs
	'''
	e = []
	a = []
	b = []
	c = []
	alp = []
	bet = []
	gam = []
	vol = []
	bulkmod = []
	ymod	= []
	comp	= []
	sd1	= []
	sd2 = []
	sd3 = []
	sd4 = []
	sd5 = []
	sd6 = []
	sde1 = []
	sde2 = []
	sde3 = []
	hd1	= []
	hd2 = []
	hd3 = []
	hd4 = []
	hd5 = []
	hd6 = []
	hde1 = []
	hde2 = []
	hde3 = []

	taskid = []
	'''

	def process_file(file_id):

		gdir  = 'A' + str(file_id)
		gpath = os.path.join(dir_path,gdir)
		gfile = 'gulp_klmc.gout'
		gpath = os.path.join(gpath,gfile)
		
		lres, res = get_gulp_output(gpath,0.000005)

		if lres :
			'''
			e.append(res['energy'])
			taskid.append(file_id)

			a.append(res['a'])
			b.append(res['b'])
			c.append(res['c'])
			alp.append(res['alp'])
			bet.append(res['bet'])
			gam.append(res['gam'])
			vol.append(res['vol'])
		
			bulkmod.append(res['bulkmod'])
			ymod.append(res['ymod'])
			comp.append(res['comp'])
		
			sd1.append( res['sd1'])
			sd2.append( res['sd2'])
			sd3.append( res['sd3'])
			sd4.append( res['sd4'])
			sd5.append( res['sd5'])
			sd6.append( res['sd6'])
			sde1.append(res['sde1'])
			sde2.append(res['sde2'])
			sde3.append(res['sde3'])

			hd1.append( res['sd1'])
			hd2.append( res['sd2'])
			hd3.append( res['sd3'])
			hd4.append( res['sd4'])
			hd5.append( res['sd5'])
			hd6.append( res['sd6'])
			hde1.append(res['sde1'])
			hde2.append(res['sde2'])
			hde3.append(res['sde3'])

			# res is json including all above

			'''
			res.update({'taskid': file_id})
			return res	# res is already 'json' format (dict)
		else:
			return None

	results = []
	with ProcessPoolExecutor(max_workers=_max_threads) as executor:
		#results = list(executor.map(process_file,range(_MAX_ITEM)))
		#print(f"Processed {len(results)} out of {_MAX_ITEM} directories ({len(results) / _MAX_ITEM * 100:.2f}% complete).")

		for result in executor.map(process_file,range(_MAX_ITEM)):		# execute 'process_file'
			if result:	# if result != None
				results.append(result)
				print(f"Processed {len(results)} out of {_MAX_ITEM} directories ({len(results) / _MAX_ITEM * 100:.2f}% complete).")
				#print(result)

	results = [res for res in results if res is not None]

	df = pd.DataFrame(results)

	df.set_index('energy',inplace=True)
	df = df.sort_values(by='energy',ascending=True)

	#df.to_csv(sys.argv[1])
	df.to_csv(f'{_csv_filename}')

	print(df)

	# python this_source.py /path/to/result/ output.csv 1> stdout.s 2> stderr.s
