#!/bin/python

import pickle
import pandas as pd

import psutil
pid = psutil.Process()
memory_info = pid.memory_info()
memory_gb = memory_info.rss / (1024 ** 3)
print(f"Current RAM used by the Python process: {memory_gb:.2f} GB")


with open('xrd1.pkl','rb') as f:
	pkl_df1 = pickle.load(f)
print(1)
memory_info = pid.memory_info()
memory_gb = memory_info.rss / (1024 ** 3)
print(f"Current RAM used by the Python process: {memory_gb:.2f} GB")
# --
with open('xrd2.pkl','rb') as f:
	pkl_df2 = pickle.load(f)
print(2)
memory_info = pid.memory_info()
memory_gb = memory_info.rss / (1024 ** 3)
print(f"Current RAM used by the Python process: {memory_gb:.2f} GB")
# --
with open('xrd3.pkl','rb') as f:
	pkl_df2 = pickle.load(f)
print(3)
memory_info = pid.memory_info()
memory_gb = memory_info.rss / (1024 ** 3)
print(f"Current RAM used by the Python process: {memory_gb:.2f} GB")
# --
with open('xrd4.pkl','rb') as f:
	pkl_df4 = pickle.load(f)
print(4)
memory_info = pid.memory_info()
memory_gb = memory_info.rss / (1024 ** 3)
print(f"Current RAM used by the Python process: {memory_gb:.2f} GB")
# --
with open('xrd5.pkl','rb') as f:
	pkl_df5 = pickle.load(f)
print(5)
memory_info = pid.memory_info()
memory_gb = memory_info.rss / (1024 ** 3)
print(f"Current RAM used by the Python process: {memory_gb:.2f} GB")
