from math import *
import numpy as np
import matplotlib.pyplot as plt

C = 10 ** -7
L = 0.1
R = 429.5

# voltage amplitude
E = 4

# resonant frequency
f_rez = (sqrt(1 / (C * L) - R ** 2 / (2 * L ** 2))) / (2 * pi)

f_arr = np.arange(f_rez - 500, f_rez + 500, 50)

X_arr = []
for i in range(len(f_arr)):
    X_arr.append(sqrt(R ** 2 + (f_arr[i] * 2 * pi * L - 1 / (f_arr[i] * 2 * pi * C)) ** 2))

I0_arr = []
U_arr = []
for i in range(len(f_arr)):
    I0_arr.append(E / X_arr[i])
    U_arr.append(I0_arr[i] / (f_arr[i] * 2 * pi * C))

plt.figure(figsize=(12, 7))
plt.subplot(221)
f_U_dependence = plt.plot(f_arr, U_arr)

C_arr = [1, 3, 10, 30, 100, 300]
C_arr = [c * 10 ** -9 for c in C_arr]

f_from_C_arr = [(sqrt(1 / (c * L) - R ** 2 / (2 * L ** 2))) / (2 * pi) for c in C_arr]

U_delta_height = max(U_arr) / sqrt(2)

fvalues, uvalues = f_U_dependence[0].get_xdata(), f_U_dependence[0].get_ydata()

first = min(uvalues[:10], key=lambda x: abs(x - max(uvalues) / sqrt(2)))
second = min(uvalues[10:], key=lambda x: abs(x - max(uvalues) / sqrt(2)))

Q_graph = f_rez / (fvalues[np.where(uvalues == second)] - fvalues[np.where(uvalues == first)])
Q_calculated = 1 / R * sqrt(L / C)

C_reversed = [c ** -1 for c in C_arr]
f_from_C_arr_squared = [f ** 2 for f in f_from_C_arr]

A = np.c_[C_reversed, np.ones(len(C_reversed))]
p, residuals, rank, svals = np.linalg.lstsq(A, f_from_C_arr_squared)

plt.subplot(222)
plt.plot(C_reversed, f_from_C_arr_squared, 'o', C_reversed, A.dot(p), '.')
plt.show()

k = (A.dot(p)[0] - A.dot(p)[1]) / (C_reversed[0] - C_reversed[1])
b = A.dot(p)[1] - k * C_reversed[1]

R_graph = sqrt(abs(b) * 4 * k)
