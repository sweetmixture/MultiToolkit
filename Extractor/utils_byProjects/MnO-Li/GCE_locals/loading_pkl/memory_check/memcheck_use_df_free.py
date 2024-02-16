#!/bin/python

import pickle
import pandas as pd
import psutil

def print_memuse(pid):
	memory_info = pid.memory_info()
	memory_gb = memory_info.rss / (1024 ** 3)
	print(f"Current RAM used by the Python process: {memory_gb:.2f} GB")

pid = psutil.Process()
print_memuse(pid)

pkl_df1 = pd.read_pickle('xrd1.pkl')
print(1)
print_memuse(pid)
print(f'free pkl')
del pkl_df1
print_memuse(pid)

pkl_df2 = pd.read_pickle('xrd2.pkl')
print(2)
print_memuse(pid)
print(f'free pkl')
del pkl_df2
print_memuse(pid)
pkl_df3 = pd.read_pickle('xrd3.pkl')
print(3)
print_memuse(pid)
print(f'free pkl')
del pkl_df3
print_memuse(pid)
pkl_df4 = pd.read_pickle('xrd4.pkl')
print(4)
print_memuse(pid)
print(f'free pkl')
del pkl_df4
print_memuse(pid)
pkl_df5 = pd.read_pickle('xrd5.pkl')
print(5)
print_memuse(pid)
print(f'free pkl')
del pkl_df5
print_memuse(pid)
