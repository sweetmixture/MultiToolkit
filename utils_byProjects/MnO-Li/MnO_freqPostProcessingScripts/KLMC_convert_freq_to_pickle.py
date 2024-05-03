#
#   03.2024 W.Jee 
#
#   KLMC Solid Solution: scripts for production phase
#
'''
	* After collecting frequencies in text (human readable) format
	ㄴ'KLMC_get_freq_by_taskid.py' generated this text file

	converting the file into 'pickle' binaray for later use.
	ㄴGrand Canonical Ensemble (GCE) analysis + XRD / RDF
'''
# USER DEFINE ----
_text_filename = 'klmc_freq_summary.txt'
_pkl_filename = 'klmc_freq_summary.pkl'
# USER DEFINE ----


# ------------------------------------------------------------
import pickle, sys

taskidlist = []
freqlist = []

freq_summary = {}
with open(f'{_text_filename}','r') as f:
	for line in f:

		ls = line.split()

		taskid = int(ls[0])
		freqlist = [ float(item) for item in ls[1:] ]
	
		freq_summary[taskid] = freqlist

with open(f'{_pkl_filename}','wb') as f:
	pickle.dump(freq_summary,f)
