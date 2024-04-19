from Profiler import Profiler
import numpy as np

log1 = '/work/e05/e05/wkjee/Software/MultiToolkit/KLMC3_Profiler/set2_log.json'
config1 = '/work/e05/e05/wkjee/Software/MultiToolkit/KLMC3_Profiler/set2_config.json'

kd = Profiler(root=None,master_log=log1,config_log=config1)

log = kd.get_master_log()
print(log.keys())
#kd.print_workgroup_log('9')



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
