
with open("fruit","r") as f:

	pattern = "banana is"
	for line in f:
		if pattern in line:
			print(f'pattern found {pattern} -> call break')
			break

	
	f.seek(0)		# file pointer 'f' back to the beginning
	line = iter(f)

	print(next(line,).strip().split())
	print(next(line,).strip())
	print(next(line,).strip())
	print(next(line,).strip())
	#print(next(line,))

	# using default value in next()
	#print(next(line,False).strip().split())
	#print(next(line,False).strip())
	#print(next(line,False).strip())
	#print(next(line,False).strip())
	#print(next(line,False))
