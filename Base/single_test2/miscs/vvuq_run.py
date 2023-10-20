import os,sys
import easyvvuq as uq
import chaospy as cp
from easyvvuq.actions import CreateRunDirectory, Encode, Decode, CleanUp, ExecuteLocal, Actions

from easyvvuq.actions import QCGPJPool
from easyvvuq.actions.execute_qcgpj import EasyVVUQParallelTemplate

###################################
Nnodes   = 1
Ncores   = 128
Sigma    = 0.01		# 0.5 X
Nsamples = 6
###################################

# print SLURM array task id
try:
        print('Array Task ID: {}'.format(sys.argv[1]))
        task_name = sys.argv[1]
except:
        print('argv not found')
        task_name = ''

# CsSnBr info

L = [ 12.6326, 12.6326, 12.6326 ]

encoder = uq.encoders.GenericEncoder(template_fname='aims.geometry.template',delimiter='$',target_filename='geometry.in')
encoder2= uq.encoders.GenericEncoder(template_fname='aims.control.template',delimiter='$',target_filename='control.in')
multiencoder = uq.encoders.MultiEncoder(encoder,encoder2)
'''
	Setting up encoders,

	template 1 - FHIaims control.in
	template 2 - FHIaims geometry.in
'''
#Cs = [ [ 0 for i in range(3) ] for j in range(8) ] 
Cs = [ 0 for j in range(8) ] 
Cs[0] = [ 0.00000, 0.00000, 0.00000 ]
Cs[1] = [ 0.00000, 0.00000, 0.50000 ]
Cs[2] = [ 0.00000, 0.50000, 0.00000 ]
Cs[3] = [ 0.00000, 0.50000, 0.50000 ]
Cs[4] = [ 0.50000, 0.00000, 0.00000 ]
Cs[5] = [ 0.50000, 0.00000, 0.50000 ]
Cs[6] = [ 0.50000, 0.50000, 0.00000 ]
Cs[7] = [ 0.50000, 0.50000, 0.50000 ]
'''
atom_frac       0.25000 0.25000 0.25000 Pb
atom_frac       0.25000 0.25000 0.75000 Pb
atom_frac       0.25000 0.75000 0.25000 Pb
atom_frac       0.25000 0.75000 0.75000 Pb
atom_frac       0.75000 0.25000 0.25000 Pb
atom_frac       0.75000 0.25000 0.75000 Pb
atom_frac       0.75000 0.75000 0.25000 Pb
atom_frac       0.75000 0.75000 0.75000 Pb
atom_frac       0.25000 0.25000 0.00000 I
atom_frac       0.25000 0.25000 0.50000 I
atom_frac       0.25000 0.75000 0.00000 I
atom_frac       0.25000 0.75000 0.50000 I
atom_frac       0.75000 0.25000 0.00000 I
atom_frac       0.75000 0.25000 0.50000 I
atom_frac       0.75000 0.75000 0.00000 I
atom_frac       0.75000 0.75000 0.50000 I
atom_frac       0.25000 0.00000 0.25000 I
atom_frac       0.25000 0.00000 0.75000 I
atom_frac       0.25000 0.50000 0.25000 I
atom_frac       0.25000 0.50000 0.75000 I
atom_frac       0.75000 0.00000 0.25000 I
atom_frac       0.75000 0.00000 0.75000 I
atom_frac       0.75000 0.50000 0.25000 I
atom_frac       0.75000 0.50000 0.75000 I
atom_frac       0.00000 0.25000 0.25000 I
atom_frac       0.00000 0.25000 0.75000 I
atom_frac       0.00000 0.75000 0.25000 I
atom_frac       0.00000 0.75000 0.75000 I
atom_frac       0.50000 0.25000 0.25000 I
atom_frac       0.50000 0.25000 0.75000 I
atom_frac       0.50000 0.75000 0.25000 I
atom_frac       0.50000 0.75000 0.75000 I
'''
params = { 
	"lx" : {"type":"float","default":L[0]},"ly" : {"type":"float","default":L[1]},"lz" : {"type":"float","default":L[2]},	# lattice vectors

	"a1x" : {"type":"float","default":Cs[0][0]}, "a1y" : {"type":"float","default":Cs[0][1]}, "a1z" : {"type":"float","default":Cs[0][2]},
	"a2x" : {"type":"float","default":Cs[1][0]}, "a2y" : {"type":"float","default":Cs[1][1]}, "a2z" : {"type":"float","default":Cs[1][2]},
	"a3x" : {"type":"float","default":Cs[2][0]}, "a3y" : {"type":"float","default":Cs[2][1]}, "a3z" : {"type":"float","default":Cs[2][2]},
	"a4x" : {"type":"float","default":Cs[3][0]}, "a4y" : {"type":"float","default":Cs[3][1]}, "a4z" : {"type":"float","default":Cs[3][2]},
	"a5x" : {"type":"float","default":Cs[4][0]}, "a5y" : {"type":"float","default":Cs[4][1]}, "a5z" : {"type":"float","default":Cs[4][2]},
	"a6x" : {"type":"float","default":Cs[5][0]}, "a6y" : {"type":"float","default":Cs[5][1]}, "a6z" : {"type":"float","default":Cs[5][2]},
	"a7x" : {"type":"float","default":Cs[6][0]}, "a7y" : {"type":"float","default":Cs[6][1]}, "a7z" : {"type":"float","default":Cs[6][2]},
	"a8x" : {"type":"float","default":Cs[7][0]}, "a8y" : {"type":"float","default":Cs[7][1]}, "a8z" : {"type":"float","default":Cs[7][2]}
}

# Set UQ Execute 
#execute = ExecuteLocal('mpirun -np {} /home/uccawkj/fhi-aims.221103/build/aims.221103.scalapack.mpi.x'.format(Ncores),'FHIaims.out','FHIaims.err')
execute = ExecuteLocal(f'srun --nodes=1 --ntasks={Ncores} --cpus-per-task=1 /work/y07/shared/apps/core/fhiaims/210716.3/bin/aims.mpi.x','FHIaims.out','FHIaims.err')

# Set UQ Action


# Run!
actions = Actions(CreateRunDirectory(root=os.getcwd(), flatten=True),Encode(multiencoder),execute)

# Generation Test
#actions = Actions(CreateRunDirectory(root=os.getcwd(), flatten=True),Encode(multiencoder))

# Set UQ Campaign
campaign = uq.Campaign(name=f'run_{task_name}_',params=params,actions=actions)

# Set UQ Sampler + push to UQ Campaign
vary = {

	#"lx" : cp.Normal(L[0],Sigma),
	#"ly" : cp.Normal(L[1],Sigma),
	#"lz" : cp.Normal(L[2],Sigma)

	"a1x" : cp.Normal(Cs[0][0],Sigma), "a1y" : cp.Normal(Cs[0][1],Sigma), "a1z" : cp.Normal(Cs[0][2],Sigma),
	"a2x" : cp.Normal(Cs[1][0],Sigma), "a2y" : cp.Normal(Cs[1][1],Sigma), "a2z" : cp.Normal(Cs[1][2],Sigma),
	"a3x" : cp.Normal(Cs[2][0],Sigma), "a3y" : cp.Normal(Cs[2][1],Sigma), "a3z" : cp.Normal(Cs[2][2],Sigma),
	"a4x" : cp.Normal(Cs[3][0],Sigma), "a4y" : cp.Normal(Cs[3][1],Sigma), "a4z" : cp.Normal(Cs[3][2],Sigma),
	"a5x" : cp.Normal(Cs[4][0],Sigma), "a5y" : cp.Normal(Cs[4][1],Sigma), "a5z" : cp.Normal(Cs[4][2],Sigma),
	"a6x" : cp.Normal(Cs[5][0],Sigma), "a6y" : cp.Normal(Cs[5][1],Sigma), "a6z" : cp.Normal(Cs[5][2],Sigma),
	"a7x" : cp.Normal(Cs[6][0],Sigma), "a7y" : cp.Normal(Cs[6][1],Sigma), "a7z" : cp.Normal(Cs[6][2],Sigma),
	"a8x" : cp.Normal(Cs[7][0],Sigma), "a8y" : cp.Normal(Cs[7][1],Sigma), "a8z" : cp.Normal(Cs[7][2],Sigma)
}
#"bx" : cp.Normal(B[0],Sigma), "by" : cp.Normal(B[1],Sigma), "bz" : cp.Normal(B[2],Sigma)

sampler = uq.sampling.RandomSampler(vary=vary,max_num=Nsamples)
campaign.set_sampler(sampler)

print('Before trying QCGPJPool')
try:
        with QCGPJPool(
                #qcgpj_executor=QCGPJExecutor(resources=f"node1:{Ncores},node2:{Ncores}"),
                template=EasyVVUQParallelTemplate(),
                template_params={'numNodes':Nnodes,'numCores':Ncores}
                ) as qcgpj:
            campaign.execute(pool=qcgpj).collate()

        # One simple fomr would be ... Not provinding Node/Core controls
        # with QCGPJPool() as qcgpj:
        #       campaign.execute(pool=qcgpj).collate()

            # this works for numNodes:1, if the code runs on a head node (i.e., only available resource is '1')
            # say on thomas.rc ... 12 jobs will be on running concurrently
except Exception as e:
    print(e)
