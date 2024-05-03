### 05.2024
### tentative supporting test scripts
###

# print Carteisian: 'drlist' default saving cartesian
def print_delta_r(drlist,elemlist=None):

	if elemlist == None:
		for k,dr in enumerate(drlist,start=1):
			print(f'{dr:16.12f}',end='')
			if k%3 == 0:
				print('')

	if elemlist is not None:
		for k,elem in enumerate(elemlist):
			print(f'{elem:5.3s}',end='')
			for l in range(3):
				print(f'{drlist[k*3+l]:16.12f}',end='')
			print('')

def print_delta_r_sign(signlist,elemlist=None):

	if elemlist == None:
		for k, sign in enumerate(signlist,start=1):
			print(f'{sign:4d}',end='')
			if k%3 == 0:
				print('')
	
	if elemlist is not None:
		for k,elem in enumerate(elemlist):
			print(f'{elem:5.3s}',end='')
			for l in range(3):
				print(f'{signlist[k*3+l]:4d}',end='')
			print('')
