import os,sys,random

def process_file(file_path,i,size):
	root = os.getcwd()
	header_file = "/work/e05/e05/wkjee/Masters/Zirui2023/MnO/shelOnly/new_header"
	footer_file = "/work/e05/e05/wkjee/Masters/Zirui2023/MnO/shelOnly/new_footer"
	
	with open(file_path, "r") as target_input:
		lines = target_input.readlines()
	
		end_line   = None
		for l,line in enumerate(lines):
			if 'shel' in line:
				end_line = l
				break
	
		geometry_lines = lines[:l]
		geometry_lines = geometry_lines[7:]
	
		# shuffleing Tc <-> Mn
		linelist = []
		for line in geometry_lines:
			ls = line.split()
			if ls[0] == 'Mn':
				ls[0] = 'null'
			if ls[0] == 'Tc':
				ls[0] = 'null'
			linelist.append(ls)

		random_intlist= random.sample(range(1,25),size)
		print(random_intlist)

		count = 0
		for line in linelist:
			if line[0] == 'null':
				count += 1
				if count in random_intlist:
					line[0] = 'Tc'

		for line in linelist:
			if line[0] == 'null':
				line[0] = 'Mn'

		geometry_lines = []
		for line in linelist:
			line.append('\n')
			string = ' '.join(line)
			geometry_lines.append(string)

	
	with open("geometry", "w") as geometry_file:
		geometry_file.writelines(geometry_lines)
	
	with open(f"{header_file}", "r") as header_content, \
		open(f"{root}/shuffle_run/A{i}.gin", "w") as output_file, \
		open(f"{footer_file}", "r") as footer_content:
	
		output_file.write(header_content.read())
		output_file.writelines(geometry_lines)
		output_file.write(footer_content.read())

	print(f"progressing ... {i}")

if __name__ == "__main__":
	
	size = int(sys.argv[1])
	taskid = sys.argv[2]

	target_shuffle = f'/work/e05/e05/wkjee/Masters/Zirui2023/MnO/conpshell/li{size}/A{taskid}/gulp.res'

	sta = 0
	max_value = 2000
	#max_value = 1000

	os.makedirs("shuffle_run", exist_ok=True)
	#os.makedirs("shuffle_run_phon", exist_ok=True)
	
	for i in range(max_value):
		process_file(target_shuffle,i,size)
	
	# Cleaning
	os.remove("geometry")

