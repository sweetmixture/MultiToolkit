import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator
from Profiler import Profiler
import numpy as np
import sys

log1 = '/Users/woongkyujee/Desktop/PAX_Generic/PAX_Lancaster04.24/SOURCE/Plots/jsonfiles/set5_log.json'
config1 = '/Users/woongkyujee/Desktop/PAX_Generic/PAX_Lancaster04.24/SOURCE/Plots/jsonfiles/set5_config.json'

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

# get KLMC start time
log_config = kd.get_master_config()
time0 = log_config['start_t']['abs']
#print(time0)
init_delay = [ time0*-1. for i in range(workgroup_count) ]

for k,key in enumerate(log.keys()): # k: workgroup idex, key: workgroup
	for m,task_id in enumerate(log[key].keys()):

		# for the first launch
		if m == 0:
			init_delay[k] += log[key][str(k)]['send_t']['abs']

		if task_id != "-1":	# "-1" is flag to workgroup die - not recored
			app_elap_t[k].append( log[key][task_id]['app_elap_t'] )
			app_launch_oh[k].append( log[key][task_id]['app_launch_overhead'] )
			mpi_oh[k].append( log[key][task_id]['mpi_overhead'] )

#print(init_delay)
print(f' Max init delay: {max(init_delay)}')
print(f' init_delay/nworkgroups : {max(init_delay)/workgroup_count}')
#sys.exit(1)
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
app_elap_t_sum = []
app_launch_oh_sum = []
mpi_oh_sum = []
app_elap_t_std = []
app_launch_oh_std = []
mpi_oh_std = []

for list_item in app_elap_t:
	app_elap_t_sum.append(np.sum(list_item))
	app_elap_t_std.append(np.std(list_item))
#print(app_elap_t_sum)
#print('\n\n\n')
#print(app_elap_t_std)
for list_item in app_launch_oh:
	app_launch_oh_sum.append(np.sum(list_item))
	app_launch_oh_std.append(np.std(list_item))
for list_item in mpi_oh:
	mpi_oh_sum.append(np.sum(list_item))
	mpi_oh_std.append(np.std(list_item))


sum_all = np.add(app_elap_t_sum,app_launch_oh_sum)
sum_all = np.add(sum_all,mpi_oh_sum)
sum_all = np.add(sum_all,init_delay)

print(f' sum all max     : {max(sum_all.tolist())}')
print(f' sum all min     : {min(sum_all.tolist())}')
print(f' sum all average : {np.mean(sum_all)}')
print(f' sum max - ave   : {max(sum_all.tolist()) - np.mean(sum_all)}')

#
# bar plotting -------------------------------------------
#
# Plot configuration
cm = 1/2.54
fig, ax = plt.subplots(figsize=(24*cm, 20*cm))
plt.subplots_adjust(left=0.125, bottom=0.125, right=0.96, top=0.96, wspace=0.200, hspace=0.0)


N = workgroup_count
ind = np.arange(N)    # the x locations for the groups
width = 0.60          # the width of the bars

# Create bar plots
#p1 = ax.bar(ind, app_elap_t_sum, width, color='#d62728', yerr=app_elap_t_std)
#p2 = ax.bar(ind, app_launch_oh_sum, width, bottom=app_elap_t_sum, yerr=app_launch_oh_std)
#p3 = ax.bar(ind, mpi_oh_sum, width, bottom=np.add(app_elap_t_sum, app_launch_oh_sum), yerr=mpi_oh_std)

p1 = ax.bar(ind, app_elap_t_sum, width, color='red', bottom=init_delay) # yerr=app_elap_t_std)
p2 = ax.bar(ind, app_launch_oh_sum, width, color='green', bottom=np.add(init_delay,app_elap_t_sum)) # yerr=app_launch_oh_std)
p3 = ax.bar(ind, mpi_oh_sum, width, color='blue', bottom=np.add(init_delay,np.add(app_elap_t_sum, app_launch_oh_sum))) # yerr=mpi_oh_std)

#ax.axvline(x=12./24., color='black', linestyle='--') #label='Reference line')
#ax.axhline(y=3844.08074, color='black', linestyle='--') #label='Reference line')

ax.axhline(y=max(sum_all.tolist()), color='black', linestyle='--') #label='Reference line')
ax.axhline(y=np.mean(sum_all), color='black', linestyle='-.') #label='Reference line')
# Customize plot
_lfs = 14
_fs = 12

ax.set_ylabel('Time (s)',fontsize=_lfs)
ax.set_xlabel('Worker ID', fontsize=_lfs)

#ax.set_xticks(ind,fontsize=_fs)
#ax.set_xticklabels(('G1', 'G2', 'G3', 'G4', 'G5'))
#ax.set_yticks(np.arange(0, 81, 10))
#ax.legend((p1[0], p2[0], p3[0]), ('Men', 'Women', 'Neutral'))

ax.tick_params(axis='x', labelsize=_fs)  # Corrected line
ax.tick_params(axis='y', labelsize=_fs)  # Corrected line

ax.set_ylim(np.mean(sum_all)-np.mean(sum_all)*0.1,max(sum_all.tolist())+max(sum_all.tolist())*0.01)

# Show plot
plt.show()

fig.savefig(f'A1.png', dpi=1200, bbox_inches='tight')
#fig.savefig(f'A1.pdf', format='pdf', dpi=1200, bbox_inches='tight')

sys.exit(1)
