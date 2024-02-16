#!/bin/python

import pickle
import pandas as pd

import psutil
pid = psutil.Process()
memory_info = pid.memory_info()
memory_gb = memory_info.rss / (1024 ** 3)
print(f"Current RAM used by the Python process: {memory_gb:.2f} GB")


pkl_df1 = pd.read_pickle('xrd1.pkl')
print(1)
memory_info = pid.memory_info()
memory_gb = memory_info.rss / (1024 ** 3)
print(f"Current RAM used by the Python process: {memory_gb:.2f} GB")
pkl_df2 = pd.read_pickle('xrd2.pkl')
print(2)
memory_info = pid.memory_info()
memory_gb = memory_info.rss / (1024 ** 3)
print(f"Current RAM used by the Python process: {memory_gb:.2f} GB")
pkl_df3 = pd.read_pickle('xrd3.pkl')
print(3)
memory_info = pid.memory_info()
memory_gb = memory_info.rss / (1024 ** 3)
print(f"Current RAM used by the Python process: {memory_gb:.2f} GB")
pkl_df5 = pd.read_pickle('xrd4.pkl')
print(4)
memory_info = pid.memory_info()
memory_gb = memory_info.rss / (1024 ** 3)
print(f"Current RAM used by the Python process: {memory_gb:.2f} GB")
pkl_df5 = pd.read_pickle('xrd5.pkl')
print(5)
memory_info = pid.memory_info()
memory_gb = memory_info.rss / (1024 ** 3)
print(f"Current RAM used by the Python process: {memory_gb:.2f} GB")
