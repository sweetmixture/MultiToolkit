import pickle

my_dict = {'I':0, 'my':1, 'me':2, 'mine':3}
with open('mydict.pkl', 'wb') as tf:
	pickle.dump(my_dict, tf)
