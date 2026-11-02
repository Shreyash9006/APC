#NumPy Mod Operation
import numpy as np

arr = np.array([5, 15, 20])
arr1 = np.array([2, 5, 9])

print("First array:")
print(arr)

print("\nSecond array:")
print(arr1)

print("\nApplying mod() function:")
print(np.mod(arr, arr1))

print("\nApplying remainder() function:")
print(np.remainder(arr, arr1))