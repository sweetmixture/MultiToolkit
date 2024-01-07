#!/bin/python

from concurrent.futures import ProcessPoolExecutor
import pandas as pd

task = [ (i*5,'abc') for i in range(100) ]

def taskfunc(args):
	i, value = args
	print(i,value)

	return i
results = []
with ProcessPoolExecutor(max_workers=10) as executor:
	for result in executor.map(taskfunc,task):
		results.append(result)
#print(results)


df = pd.read_csv('/work/e05/e05/wkjee/Masters/Zirui2023/MnO/conpshell/li12/nconp12.csv')

#print(df['taskid'].tolist())
