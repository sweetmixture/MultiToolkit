#!/bin/python

from concurrent.futures import ProcessPoolExecutor
import pandas as pd

task = [ i*5 for i in range(100) ]

def taskfunc(i):

	print(i)

	return i
results = []
with ProcessPoolExecutor(max_workers=10) as executor:
	for result in executor.map(taskfunc,task):
		results.append(result)
print(results)


df =
