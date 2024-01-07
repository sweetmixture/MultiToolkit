#!/bin/python

from concurrent.futures import ProcessPoolExecutor
import pandas as pd
import pickle

task = [ (i*5,'abc') for i in range(100) ]

def taskfunc(args):
	i, value = args
	print(i,value)

	return i, value
results = {}
with ProcessPoolExecutor(max_workers=10) as executor:
	for result in executor.map(taskfunc,task):
		results[result[0]] = result[1]
print(results)

with open('output.pkl','wb') as f:
	pickle.dump(results,f)


#df = pd.read_csv('/work/e05/e05/wkjee/Masters/Zirui2023/MnO/conpshell/li12/nconp12.csv')
#print(df['taskid'].tolist())
