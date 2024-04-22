from Profiler import Profiler
import numpy as np
import sys

log1 = '/work/e05/e05/wkjee/Software/MultiToolkit/KLMC3_Profiler/jsonfiles/set2_log.json'
config1 = '/work/e05/e05/wkjee/Software/MultiToolkit/KLMC3_Profiler/jsonfiles/set2_config.json'

#
# load pre-calculated profiling result from files: log1 / config1
#
kd = Profiler(root=None,master_log=log1,config_log=config1)

# get self.master_log_json
log = kd.get_master_log()

# workgroup_count
workgroup_count = len(log.keys())

# Get timing for the following contents
app_elap_t = [ [] for i in range(workgroup_count) ]			# application level elapsed time
app_launch_oh = [ [] for i in range(workgroup_count) ]		# application laucnh overhead : including task unpacking after recv / task packing before sendback
mpi_oh = [ [] for i in range(workgroup_count) ]				# master <-> worker mpi-overhead

for k,key in enumerate(log.keys()): # k: workgroup idex, key: workgroup
	for task_id in log[key].keys():

		if task_id != "-1":	# "-1" is flag to workgroup die - not recored
			app_elap_t[k].append( log[key][task_id]['app_elap_t'] )
			app_launch_oh[k].append( log[key][task_id]['app_launch_overhead'] )
			mpi_oh[k].append( log[key][task_id]['mpi_overhead'] )

# data check 1
#for k,key in enumerate(log.keys()):
#	l1 = len(app_elap_t[k])
#	l2 = len(app_launch_oh[k])
#	l3 = len(mpi_oh[k])
#	print(l1,l2,l3)
#
#print('APP-ELAP-T',app_elap_t[0],end='\n')
#print('APP_LOH',app_launch_oh[0],end='\n')
#print('MPI_OH',mpi_oh[0],end='\n')

# INDEXING
# Red (application level elapt) : ‘app_elap_t’
# Green: ‘app_launch_overhead’
# Blue: ’mpi_overhead’

#print(log.keys()) # keys() : list[workgroup ids]
#kd.print_workgroup_log('9')

#
# find mean & std
#
app_elap_t_mean = []
app_launch_oh_mean = []
mpi_oh_mean = []
app_elap_t_std = []
app_launch_oh_std = []
mpi_oh_std = []

for list_item in app_elap_t:
	app_elap_t_mean.append(np.mean(list_item))
	app_elap_t_std.append(np.std(list_item))

print(app_elap_t_mean,app_elap_t_std)


sys.exit(1)

sum_app_elap_t = [ 0. for i in range(len(log.keys())) ]	# len -> number of workgroups
sum_mpi_overhead = [ 0. for i in range(len(log.keys())) ]	# len -> number of workgroups
sum_launch_overhead = [ 0. for i in range(len(log.keys())) ]	# len -> number of workgroups
for k,key in enumerate(log.keys()):

	for task_id in log[key].keys():

		#print(key,task_id)
		try:
			sum_app_elap_t[k] += log[key][task_id]['app_elap_t']
			sum_mpi_overhead[k] += log[key][task_id]['mpi_overhead']
			sum_launch_overhead[k] += log[key][task_id]['app_launch_overhead']
		except:
			pass
#print(total_t)
print('app elap t     max:', max(sum_app_elap_t))
print('mpi overhead   max:', max(sum_mpi_overhead))
print('launch overhed max:', max(sum_launch_overhead))

total_t = (np.array(sum_app_elap_t) + np.array(sum_mpi_overhead) + np.array(sum_launch_overhead)).tolist()
print('total t        max:', max(total_t))
