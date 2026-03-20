import  numpy as np
import  matplotlib.pyplot as plt


def interpolate(x, x1, x2, y1, y2): return y1+(y2-y1)/(x2-x1)*(x-x1)

np.random.seed(1)

xx = np.linspace(0, 20 * np.pi, 1000)

yy = np.sin(xx) + np.random.normal(0, 0.1, 1000)


print(f"x = {xx[15]}, y = {yy[15]}")
print(f"x = {xx[16]}, y = {yy[16]}")

x_mid = (xx[15]+xx[16])/2 #интерполяция
y_mid = interpolate(x_mid, xx[15], xx[16], yy[15], yy[16])
print(f"mid: x = {x_mid}, y = {y_mid}")

x_out=(xx[16]+xx[17])/2 #экстраполяция
y_out=interpolate(x_out, xx[15], xx[16], yy[15], yy[16])
print(f"out: x = {x_out}, y = {y_out}")

#https://scipy-lectures.org/intro/scipy/auto_examples/plot_interpolation.html
from scipy.interpolate import interp1d
import numpy as np
xx = np.array([0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
yy = np.array([0, 1, 4, 9, 7, 10, 11, 3, 4, 5, 11])

# Создание функции интерполяции
linear_interp = interp1d(xx, yy, kind='linear')
cubic_interp = interp1d(xx, yy, kind='cubic')

tt = np.linspace(0, 10, 50)

# Вычисление значений
y_linear = linear_interp(tt)
y_cubic = cubic_interp(tt)

plt.plot(xx, yy, 'o', ms=6, label='measures')
plt.plot(tt, y_linear, label="linear")
plt.plot(tt, y_cubic, label="cubic")

plt.legend(loc="upper right")
plt.xlabel("x")
plt.ylabel("y")
plt.title("Interpolation")
plt.grid(True)
plt.show()



