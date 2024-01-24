'''
    ! data access through pkl
    import pickle
    rdf_pkl = pickle.load(f)    # f: rdf{size}.pkl filepath
    #
    # using 'taskid' to access rdf data
    #
        rdf_data = rdf_pkl[taskid]
        examples>
            r = rdf_data['r']    : <list> r values
            r = rdf_data['MnMn'] : <list> rdf values of 'MnMn'
            ...
'''

import sys

import pickle
import numpy as np
import matplotlib.pyplot as plt
from scipy.ndimage import gaussian_filter1d

#
# essential inputs
#
#	(1) pkl file
#	(2) taskid
#
# possible output
#
#	(1) 'rdfout.png' 
#
pklfile = sys.argv[1]
gm_task = int(sys.argv[2])

#with open('rdf1.pkl','rb') as f:
with open(pklfile,'rb') as f:
	rpkl = pickle.load(f)

# gm 12511

gmrdf = rpkl[gm_task]

r = gmrdf['r']
LiLi = gmrdf['LiLi']
TcTc = gmrdf['TcTc']
LiTc = gmrdf['LiTc']
MnMn = gmrdf['MnMn']

sigma = 1.0
sLiLi = gaussian_filter1d(np.array(LiLi),sigma=sigma)
sTcTc = gaussian_filter1d(np.array(TcTc),sigma=sigma)
sLiTc = gaussian_filter1d(np.array(LiTc),sigma=sigma)
sMnMn = gaussian_filter1d(np.array(MnMn),sigma=sigma)

plt.plot(r, sLiLi, label='LiLi', color='green')
plt.plot(r, sTcTc, label='TcTc', color='gray')
plt.plot(r, sLiTc, label='LiTc', color='blue')
#plt.plot(r, sMnMn, label='MnMn', color='black')

#plt.xlim([0,8])
#plt.ylim([0,25])
plt.legend()
#plt.savefig('rdfout.png',bbox_inches='tight')
plt.show()

