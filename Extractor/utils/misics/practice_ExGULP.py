#!/bin/bash

from Extractor.GULP import ExtractGULP
import os

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
		return False, None

if __name__ == '__main__':

	testfile = './summary_li1/A9302.gout'
	lres, res = get_gulp_output(testfile,1.E-6)
	if lres :
		print(res)

	testfile = 'A123.gout'
	lres, res = get_gulp_output(testfile,1.E-6)
	if lres :
		print(res)

	

