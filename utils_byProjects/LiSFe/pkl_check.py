import pickle
import sys

pklfile = sys.argv[1]
taskid = int(sys.argv[2])


with open(pklfile,'rb') as f:
	rdf_pkl = pickle.load(f)	# f: rdf{size}.pkl filepath

print(f' * -------')
print(f' * loading rdf done')
print(f' * length: {len(rdf_pkl)}')
print(f' * -------')
#
# using 'taskid' to access rdf data
#
rdf_data = rdf_pkl[taskid]

r = rdf_data['r']
rSS = rdf_data['SS']

for r,rss in zip(r,rSS):
	print(f'{r:10.6f} {rss:20.12f}')
'''
	examples>
		r = rdf_data['r']	 : <list> r values
		r = rdf_data['MnMn'] : <list> rdf values of 'MnMn'
		...

	pairlist = []
	pair = ['S','S']
	pairlist.append(pair)
	pair = ['S','Li']
	pairlist.append(pair)
	pair = ['S','Fe']
	pairlist.append(pair)
	pair = ['Li','Li']
	pairlist.append(pair)
	pair = ['Li','Fe']
	pairlist.append(pair)
	pair = ['Fe','Fe']

'''
