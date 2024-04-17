#
#	04.2024 W.Jee 
#
#	KLMC3 profiler
#
#	(1) MPI log files: master.log / workgroup_*.log
#	(2) GULP log files ?
#
# ----------------------------------------------------------

import sys,os
from concurrent.futures import ProcessPoolExecutor
from TimeManager import klmc_get_time, gulp_get_time

class Profiler():

	def __init__(self,root):

		self.root = root

		if not os.path.exists(self.root):
			print(f'Error: class Profiler() root path does not exist',file=sys.stderr)
			sys.exit(1)

		#
		# KLMC3 task-farming log
		#

		# ! workgroup
		self._max_workgroup = 99999
		self._workgroup_file_prefix = 'workgroup_'
		self.workgroup_log_plist = []	# plist - path list

		# loadindg 'worklog_*.log'
		for i in range(self._max_workgroup):

			wlogfile = self._workgroup_file_prefix + f'{i}' + '.log'
			wlogfile = os.path.join(self.root,wlogfile)
		
			if os.path.exists(wlogfile):
				self.workgroup_log_plist.append(wlogfile)
			else:
				break
		
		# ! master
		self._master_file = 'master.log'
		self.master_log_plist = []
	
		mlogfile = os.path.join(self.root,self._master_file)

		if os.path.exists(mlogfile):
			self.master_log_plist.append(mlogfile)
		else:
			print(f'Error: class Profiler() master.log file does not exist',file=sys.stderr)
			sys.exit(1)

		self.master_count = len(self.master_log_plist)
		self.workgroup_count = len(self.workgroup_log_plist)

		# HC-PRINT
		print(f'-----------------------------------------------')
		print(f'* Initiating KLMC3 task-farming profiler')
		print(f'-----------------------------------------------')
		print(f'number of master    files: {len(self.master_log_plist)}')
		print(f'number of workgroup files: {len(self.workgroup_log_plist)}')
		print(f'')


		'''
			Reserved Keys for 'self.master_log_json'


			tf_start_t : time starting taskfarm (just after finished taskfarm configuration)
		'''
		self.master_log_json = {}

		for k in range(len(self.workgroup_log_plist)):

			self.master_log_json[k] = {}
		'''
			key 'k<int>' workgroup_id: include info for send/recv from workgroup
			{0: {}, 1: {}, 2: {}, 3: {}, 4: {}, 5: {}, 6: {}, ...

			 ! workgroup
			{  0:	  {	 ! keys
						taskid<int> : { 'send_t<str>'   : datetime_object<dict>,
									    'recv_t<str>'   : datetime_object<dict>,
									    'elap_t<str>'   : time<float>,
									    'send_success<str>': None and True/False<bool>,
									    'recv_success<str>': None and True/False<bool>,
									  },
					  ...
				
					  }, 1: {}, 2: {}, 3: {}, 4: {}, 5: {}, 6: {}, ...

								key<int>
			master_worker_json[ workgroup_id<int> ][ taskid<int> ].keys() : 'send_t', 'recv_t', 'elap_t', ....
		'''

		self.is_cpu_per_workgroup = False
		self.cpu_per_workgroup = None
		#
		# First scanning MPI_SEND
		#
		with open(self.master_log_plist[0],'r') as f:

			#for line in f:
			for k,line in enumerate(f):

				# logging taskfarm start time
				if 'Task envelopes setting finish' in line:	# HC
					ls = line.split()
					tf_start_t = ls[0] + ' ' + ls[1]
					self.master_log_json['tf_start_t'] = klmc_get_time(tf_start_t)	# save time object

				# logging taskfarm MPI_Send messages to 'x' workgroup_id
				_l = 0
				_l_max = 9 # HC : search next '9' lines (This is hard coded must be updated as the form of taskfarm changes)
				if 'task send' in line:

					# saved items --------------------
					_workgroup_check = None
					_task_id_check = None

					workgroup_id = None			
					task_id = None
					send_time_obj = None
					# saved items --------------------

					while _l < _l_max:

						next_line = next(f,None)

						# MPI_Send timing (master >>>>>>>> worker)
						if 'MPI_Send' in next_line:	# HC
							ls = next_line.split()
							tf_send_t = ls[0] + ' ' + ls[1]
							#print(time_string)
							try:
								send_time_obj = klmc_get_time(tf_send_t)
							except:
								send_time_obj = None

						# get workgroup id
						if (not _workgroup_check) and ('workgroup' in next_line):	# HC
							_workgroup_check = True
							ls = next_line.split()
							workgroup_id = ls[3]	# HC
							#print(next_line)

							if not self.is_cpu_per_workgroup:
								self.cpu_per_workgroup = int(ls[7])
								self.cpu_per_taskfarm = self.workgroup_count * self.cpu_per_workgroup
								self.master_log_json['cpu_per_workgroup'] = self.cpu_per_workgroup
								self.master_log_json['cpu_per_taskfarm'] = self.cpu_per_taskfarm

						# get task id
						if (not _task_id_check) and ('task_id' in next_line):	# HC
							_task_id_check = True
							ls = next_line.split()
							task_id = ls[3]			# HC
							#print(next_line)

						if _workgroup_check and _task_id_check:
							#print(_workgroup_check,_task_id_check,'break!')
							#print('next line:',next_line)
							#if workgroup_id == '15':
							#	print('yes',workgroup_id)
							break

						_l += 1
					# --------------- end (while) checking send
					if not (None in [send_time_obj,_workgroup_check,_task_id_check]):

						# create 'task_id<int>' dict
						self.master_log_json[ int(workgroup_id) ][ int(task_id) ] = {}

						self.master_log_json[ int(workgroup_id) ][ int(task_id) ]['send_t'] = send_time_obj
						self.master_log_json[ int(workgroup_id) ][ int(task_id) ]['recv_t'] = None
						self.master_log_json[ int(workgroup_id) ][ int(task_id) ]['elap_t'] = None
						self.master_log_json[ int(workgroup_id) ][ int(task_id) ]['send_success'] = True
						self.master_log_json[ int(workgroup_id) ][ int(task_id) ]['recv_success'] = None			# None -> Unknown
						self.master_log_json[ int(workgroup_id) ][ int(task_id) ]['sendrecv_success'] = None

					#print(master_log_json)
					#print(f'workgroup : {workgroup_id} / taskid : {task_id}')			

				# logging 'kill(die) message to workgroups'
				_l = 0
				_l_max = 4 # HC : search next '9' lines (This is hard coded must be updated as the form of taskfarm changes)
				if 'kill workgroups' in line: # HC

					# saved items --------------------
					_workgroup_check = None
					_task_id_check = None

					workgroup_id = None			
					task_id = None
					send_time_obj = None
					# saved items --------------------

					while _l < _l_max:

						next_line = next(f,None)

						# MPI_Send timing (master >>>>>>>> worker)
						if 'MPI_Send' in next_line:	# HC
							ls = next_line.split()
							tf_send_t = ls[0] + ' ' + ls[1]
							#print(time_string)
							try:
								send_time_obj = klmc_get_time(tf_send_t)
							except:
								send_time_obj = None

						# get workgroup id
						if (not _workgroup_check) and ('workgroup' in next_line):	# HC
							_workgroup_check = True
							ls = next_line.split()
							workgroup_id = ls[3]	# HC
							#print(next_line)

						# get task id
						if (not _task_id_check) and ('task_id' in next_line):	# HC
							_task_id_check = True
							ls = next_line.split()
							task_id = ls[3]			# HC
							#print(next_line)

						if _workgroup_check and _task_id_check:
							#print(_workgroup_check,_task_id_check,'break!')
							#print('next line:',next_line)
							#if workgroup_id == '15':
							#	print('yes',workgroup_id)
							break

						_l += 1
					# --------------- end (while) checking send
					if not (None in [send_time_obj,_workgroup_check,_task_id_check]):

						# create 'task_id<int>' dict
						self.master_log_json[ int(workgroup_id) ][ int(task_id) ] = {}

						self.master_log_json[ int(workgroup_id) ][ int(task_id) ]['send_t'] = send_time_obj			# tf-interface measured: task MPI_SEND
						self.master_log_json[ int(workgroup_id) ][ int(task_id) ]['recv_t'] = None					# tf_interface measured: task MPI_RECV

						self.master_log_json[ int(workgroup_id) ][ int(task_id) ]['exe_t'] = None					# tf-interface measured: app executed time	
						self.master_log_json[ int(workgroup_id) ][ int(task_id) ]['ret_t'] = None					# tf-interface measured: app returned time
						self.master_log_json[ int(workgroup_id) ][ int(task_id) ]['elap_t'] = None					# tf-interface measured: app returned t - app executed t
						self.master_log_json[ int(workgroup_id) ][ int(task_id) ]['mpi_overhead'] = None			# tf-interface measured: (recv_t - send_t) - elap_t

						self.master_log_json[ int(workgroup_id) ][ int(task_id) ]['send_success'] = True			# tf-interface : logging MPI_SEND
						self.master_log_json[ int(workgroup_id) ][ int(task_id) ]['recv_success'] = None			# tf-interface : logging MPI_RECV
						self.master_log_json[ int(workgroup_id) ][ int(task_id) ]['sendrecv_success'] = None

						# application timing: only valid when send/recv succeeded!!!
						self.master_log_json[ int(workgroup_id) ][ int(task_id) ]['app_elap_t'] = None				# application level, app measured elapsed time


					#print(master_log_json)
					#print(f'workgroup : {workgroup_id} / taskid : {task_id}')			

		#
		# Second scanning MPI_RECV
		#
		with open(self.master_log_plist[0],'r') as f:

			#for line in f:
			for k,line in enumerate(f):

				# logging taskfarm MPI_Recv messages to 'x' workgroup_id
				_l = 0
				_l_max = 7 # HC : search next '9' lines (This is hard coded must be updated as the form of taskfarm changes)
				if 'task result recv' in line:

					# saved items --------------------
					_workgroup_check = None
					_task_id_check = None
					_task_execute_return_check = None

					workgroup_id = None			
					task_id = None
					recv_time_obj = None

					task_execute_time_obj = None
					task_return_time_obj = None
					# saved items --------------------

					while _l < _l_max:

						next_line = next(f,None)

						# MPI_Send timing (master >>>>>>>> worker)
						if 'MPI_Recv' in next_line:	# HC
							ls = next_line.split()
							tf_recv_t = ls[0] + ' ' + ls[1]
							#print(time_string)
							try:
								recv_time_obj = klmc_get_time(tf_recv_t)
							except:
								recv_time_obj = None

						# get workgroup id
						if (not _workgroup_check) and ('workgroup' in next_line):	# HC
							_workgroup_check = True
							ls = next_line.split()
							workgroup_id = ls[3]	# HC
							#print(next_line)

						# get task id
						if (not _task_id_check) and ('task_id' in next_line):	# HC
							_task_id_check = True
							ls = next_line.split()
							task_id = ls[3]			# HC
							#print(next_line)

						# get start_t / end_t (measured by task-farm)
						if 'task starts' in next_line:	# HC
							_task_execute_return_check = True

							ls = next_line.split()	# index 4,5 / 10,11

							task_execute_t = ls[4] + ' ' + ls[5]
							task_return_t  = ls[10]+ ' ' + ls[11]	

							task_execute_time_obj = klmc_get_time(task_execute_t)
							task_return_time_obj = klmc_get_time(task_return_t)

						if not None in [_workgroup_check,_task_id_check,_task_execute_return_check]:
							#print(_workgroup_check,_task_id_check,'break!')
							#print('next line:',next_line)
							#if workgroup_id == '15':
							#	print('yes',workgroup_id)
							break

						_l += 1
					# --------------- end (while) checking send
					if not (None in [recv_time_obj,_workgroup_check,_task_id_check,_task_execute_return_check]):

						# Must be readily created during MPI_SEND scanning ... 'task_id<int>' dict
						#self.master_log_json[ int(workgroup_id) ][ int(task_id) ]['send_t'] = send_time_obj			# tf-interface measured: task MPI_SEND
						self.master_log_json[ int(workgroup_id) ][ int(task_id) ]['recv_t'] = recv_time_obj				# tf_interface measured: task MPI_RECV

						self.master_log_json[ int(workgroup_id) ][ int(task_id) ]['exe_t'] = task_execute_time_obj		# tf-interface measured: app executed time	
						self.master_log_json[ int(workgroup_id) ][ int(task_id) ]['ret_t'] = task_return_time_obj		# tf-interface measured: app returned time
						self.master_log_json[ int(workgroup_id) ][ int(task_id) ]['elap_t'] = (							# tf-interface measured: app returned t - app executed t
							task_return_time_obj['abs'] - task_execute_time_obj['abs'] )
						self.master_log_json[ int(workgroup_id) ][ int(task_id) ]['mpi_overhead'] = (					# tf-interface measured: (recv_t - send_t) - elap_t
							(recv_time_obj['abs'] - self.master_log_json[ int(workgroup_id) ][ int(task_id) ]['send_t']['abs']) - self.master_log_json[ int(workgroup_id) ][ int(task_id) ]['elap_t'] )

						#self.master_log_json[ int(workgroup_id) ][ int(task_id) ]['send_success'] = True			# tf-interface : logging MPI_SEND
						self.master_log_json[ int(workgroup_id) ][ int(task_id) ]['recv_success'] = True			# tf-interface : logging MPI_RECV
						if self.master_log_json[ int(workgroup_id) ][ int(task_id) ]['send_success']:
							self.master_log_json[ int(workgroup_id) ][ int(task_id) ]['sendrecv_success'] = True

						# application timing: only valid when send/recv succeeded!!!
						#self.master_log_json[ int(workgroup_id) ][ int(task_id) ]['app_elap_t'] = None				# application level, app measured elapsed time

	# Getters ----------------------------------------------
	def get_config(self):
		return self.master_count, self.workgroup_count

	def get_master_log(self):
		return self.master_log_json

	def print_workgroup_log(self,workgroup_id):

		print(f'# printing workgroup_id {workgroup_id} log')
		for key in self.master_log_json[workgroup_id].keys():
			print(f' task_id: {key}, {self.master_log_json[workgroup_id][key]}')

	# END class Profiler() init()

if __name__=='__main__':

	# variables start ------
	logpath = '/work/e05/e05/wkjee/Masters/Zirui2023/MnO/conpshell/li24/log'						# Complete set small
	logpath = '/work/e05/e05/wkjee/SolidSolution/Batteries/IronPhospate/ProductionMax72/p64/log'	# In-complete set
	logpath = '/work/e05/e05/wkjee/SolidSolution/Batteries/IronPhospate/ProductionMax36/p33/log'	# Complete set mideum


	# variables end --------

	kp = Profiler(root=logpath)

	mcount,wcount = kp.get_config()
	master_log = kp.get_master_log()

	#print(master_log[0].keys())

	#workgroup_id = 15
	#for key in master_log[workgroup_id].keys():
	#	print(f'{key} | ',master_log[workgroup_id][key])
	#for k in range(wcount):
	#	print(master_log[k][-1])

	workgroup_id = 15
	kp.print_workgroup_log(workgroup_id)

	print('')
	workgroup_id = 9
	kp.print_workgroup_log(workgroup_id)

	print(master_log[workgroup_id].keys())


