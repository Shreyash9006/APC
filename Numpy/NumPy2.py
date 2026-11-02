#NumPy Reciprocal Function
import numpy as np

arr = np.array([25, 1.33, 1, 1, 100])

print("Our array is:")
print(arr)

print("\nAfter applying reciprocal function:")
print(np.reciprocal(arr))

arr2 = np.array([25], dtype=int)

print("\nThe second array is:")
print(arr2)

print("\nAfter applying reciprocal function:")
print(np.reciprocal(arr2))