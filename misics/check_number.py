
def isfloat(string):

	try:
		fval = float(string)
		return True
	except ValueError as e:
		return False

a = "-0.213"
a = "-.713"

print(isfloat(a))

print(float(a))
