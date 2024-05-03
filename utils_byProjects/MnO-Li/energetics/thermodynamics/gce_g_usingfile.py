import numpy as np
import sys

_T = 300

def get_gasx(_T):

	_file = f'x_u_T{_T}.0.out'

	with open(_file,'r') as f:

		data = np.loadtxt(f,skiprows=1,dtype=np.float128)

		xlist  = data[:,0]  # col 1
		ulist  = data[:,1]  # col 2
		#_ulist = data[:,2]  # col 3


	of = open(f'{_file}.g','w')
	#
	# integate for x [0:x]
	#
	for k,x in enumerate(xlist):

		#print(x,xlist[k])

		if k+1 == len(xlist):
			break

		int_xrange = xlist[:k+2]
		int_yrange = ulist[:k+2]

		I = np.trapz(int_yrange,int_xrange)

		of.write('%20.12e  %20.12e\n' % (int_xrange[-1],I))

	of.close()


# --------------------------------------------------------
get_gasx(_T)
