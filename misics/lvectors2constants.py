import numpy as np

# Example usage:
A = np.array([
[8.887711,    0.011848,   0.000000],
[0.012595,    9.537254,   0.000000],
[0.000000,    0.000000,   8.573353]
], dtype=float)

# Perform QR decomposition using numpy's qr function
Q, R = np.linalg.qr(A)

print("Orthogonal matrix Q:")
print(Q)

print("\nUpper triangular matrix R:")
print(R)

print("a=",np.linalg.norm(R[0]))
print("b=",np.linalg.norm(R[1]))
print("c=",np.linalg.norm(R[2]))

#al = np.arccos(np.rad2deg(np.dot(R[1],R[2])/np.linalg.norm(R[1])/np.linalg.norm(R[2])))
al = np.arccos(np.dot(R[1],R[2])/np.linalg.norm(R[1])/np.linalg.norm(R[2]))
be = np.arccos(np.dot(R[0],R[2])/np.linalg.norm(R[0])/np.linalg.norm(R[2]))
ga = np.arccos(np.dot(R[0],R[1])/np.linalg.norm(R[0])/np.linalg.norm(R[1]))

al = np.arccos(np.dot(A[1],A[2])/np.linalg.norm(A[1])/np.linalg.norm(A[2]))
be = np.arccos(np.dot(A[0],A[2])/np.linalg.norm(A[0])/np.linalg.norm(A[2]))
ga = np.arccos(np.dot(A[0],A[1])/np.linalg.norm(A[0])/np.linalg.norm(A[1]))
print("al = ",np.rad2deg(al))
print("be = ",np.rad2deg(be))
print("ga = ",np.rad2deg(ga))



print("--------")
print("a  = 8.887719")
print("b  = 9.537262")
print("c  = 8.573353")
print("al = 90.000000")
print("be = 90.000000")
print("ga = 89.847953")
#print(np.cos(np.deg2rad(180.)))


