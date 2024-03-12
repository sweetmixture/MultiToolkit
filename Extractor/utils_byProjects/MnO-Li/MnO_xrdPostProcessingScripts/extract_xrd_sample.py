#!/bin/python

import sys
import pandas as pd

pkl = sys.argv[1]
taskid = int(sys.argv[2])
df = pd.read_pickle(pkl)
#print(df)
xrd = df[taskid]
#print(xrd)

tth = xrd['twotheta']
ints= xrd['intensity']

for tt,i in zip(tth,ints):

	print(tt,i)
