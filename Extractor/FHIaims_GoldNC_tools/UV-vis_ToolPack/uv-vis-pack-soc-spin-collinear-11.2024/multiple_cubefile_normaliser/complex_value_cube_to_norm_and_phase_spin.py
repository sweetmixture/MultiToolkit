#### A python script to convert the imaginary and real part of the complex wavefunction
#### to its norm and phase. I use it in combination with complex_value_isosurface.vmd
#### to visualize the complex value wavefunctions.
####
#### Two references performing similar things.
#### ref: J. Phys. Chem. A 2019, 123, 3223
#### ref: Int J Quantum Chem. 2018;118:e25683
####
#### Yi Yao
#### Feb. 2021

from ase.io.cube import read_cube, write_cube
import numpy as np
import sys

f1 = sys.argv[1]
f2 = sys.argv[2]

#### YY: modify the file names here. The first one is the cube file for the imaginary part of the complex wavefunction.
####     the second one is the cube file for the real part of the complex wavefunction.
cube_real = read_cube(open(f1))
cube_imag = read_cube(open(f2))

assert (cube_imag['atoms'] == cube_real['atoms']), "the atoms in the cube files should be the same!"
assert (np.array_equal(cube_imag['origin'], cube_real['origin'])), "the origins in the cube files should be the same!"

data_complex = cube_real['data'] + 1j*cube_imag['data']
data_norm = np.absolute(data_complex)
data_phase = np.angle(data_complex)

#### YY: modify the file names here. The first one is the cube file for the norm of the complex wavefunction.
####     the second one is the cube file for the phase of the complex wavefunction.
write_cube(open("norm4.cube",'w'),cube_imag['atoms'],data=data_norm,origin=cube_imag['origin'])
write_cube(open("phase4.cube",'w'),cube_imag['atoms'],data=data_phase,origin=cube_imag['origin'])
