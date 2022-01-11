from math import *
import numpy as np
import matplotlib.pyplot as plt
import xlsxwriter
from scipy.interpolate import interpolate

C = 10 ** -7
L = 0.1
R = 429.5

# voltage amplitude
E = 4

# resonant frequency
f_rez = (sqrt(1 / (C * L) - R ** 2 / (2 * L ** 2))) / (2 * pi)
print('Resonant frequency:', f_rez)

workbook = xlsxwriter.Workbook('model.xlsx')
U_f_sheet = workbook.add_worksheet("Dependence U from f")
U_f_sheet.write('A1', 'f, Hz')
U_f_sheet.write('B1', 'X, Om')
U_f_sheet.write('C1', 'I0, A')
U_f_sheet.write('D1', 'U, V')
col = 0

# array of frequencies
f_arr = np.arange(f_rez - 500, f_rez + 500, 50)
for row in range(len(f_arr)):
    U_f_sheet.write(row + 1, col, f_arr[row])

col += 1
# array of impedance
X_arr = []
for i in range(len(f_arr)):
    X_arr.append(sqrt(R ** 2 + (f_arr[i] * 2 * pi * L - 1 / (f_arr[i] * 2 * pi * C)) ** 2))
    U_f_sheet.write(i + 1, col, X_arr[i])

col += 1
# array of current amplitude
I0_arr = []
# array of out voltage amplitude
U_arr = []
for i in range(len(f_arr)):
    I0_arr.append(E / X_arr[i])
    U_f_sheet.write(i + 1, col, I0_arr[i])
    U_arr.append(I0_arr[i] / (f_arr[i] * 2 * pi * C))
    U_f_sheet.write(i + 1, col + 1, U_arr[i])

fig, axs = plt.subplots(1, 2, constrained_layout=True)
fig.set_figheight(5)
fig.set_figwidth(10)
axs[0].plot(f_arr, U_arr, '-')
axs[0].set_title('Dependence of the amplitude of the output voltage\n on the frequency of the input')
axs[0].set_xlabel('f, Hz')
axs[0].set_ylabel('U out, V')

U_delta_height = max(U_arr) / sqrt(2)

first = min(U_arr[:10], key=lambda x: abs(x - max(U_arr) / sqrt(2)))
second = min(U_arr[10:], key=lambda x: abs(x - max(U_arr) / sqrt(2)))

Q_graph = f_rez / (f_arr[np.where(U_arr == second)] - f_arr[np.where(U_arr == first)])
Q_calculated = 1 / R * sqrt(L / C)

print('Quality factor according to the graph:', Q_graph)
print('Quality factor according to the calculations:', Q_calculated)

C_arr = [1, 3, 10, 30, 100, 300]
C_arr = [c * 10 ** -9 for c in C_arr]

f_rez_arr = [(sqrt(1 / (c * L) - R ** 2 / (2 * L ** 2))) / (2 * pi) for c in C_arr]

C_arr = [c ** -1 for c in C_arr]
f_rez_arr = [f ** 2 for f in f_rez_arr]

func = interpolate.interp1d(C_arr, f_rez_arr)
cnew = np.arange(C_arr[-1], C_arr[0], 1e8)
fnew = func(cnew)

axs[1].plot(C_arr, f_rez_arr, 'o', cnew, fnew, '-')
axs[1].set_title('Dependence of the square of the resonant frequency\n on the reverse capacitance')
axs[1].set_xlabel('C^-1, 1/F')
axs[1].set_ylabel('f rez^2, Hz^2')

k = (fnew[0] - fnew[1]) / (cnew[0] - cnew[1])
b = fnew[1] - k * cnew[1]

R_graph = sqrt(abs(b) * 4 * k)

print('Сoil inductance according to the graph:', k)
print('Active resistance according to the graph:', R_graph)

f_C_sheet = workbook.add_worksheet("Dependence f from C")
f_C_sheet.write('A1', 'C^-1, 1/F')
f_C_sheet.write('B1', 'f rez^2, Hz^2')
for i in range(len(C_arr)):
    f_C_sheet.write(i+1, 0, C_arr[i])
    f_C_sheet.write(i+1, 1, f_rez_arr[i])

plt.show()
workbook.close()
