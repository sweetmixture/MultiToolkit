import pandas as pd

# ! key goes to column name !
df = pd.DataFrame({"Name" : [ "A", "B", "C"],
                   "h" : [169, 175, 160],
                   "w" : [90, 70, 85]})
df = df.set_index('Name')
df.to_csv("output_pd.csv")

my_list = [True, True, True, True, True, False]

if False in my_list:

	print('Yea~')

'''
	Possible Outcome

	Name,h,w
	A,169,90
	B,175,70
	C,160,85
'''
