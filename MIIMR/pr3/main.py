import numpy as np
import matplotlib.pyplot as plt

# 1. Create data for the x-axis (angles in radians)
# Generate 100 evenly spaced points from 0 to 2*pi
x = np.linspace(0, 10*2 * np.pi, 1000)

# 2. Calculate the sine of all y-axis points
y = np.sin(x)

# 3. Plot the data
plt.plot(x, y)

# Optional: Add labels, a title, and a grid for clarity
plt.xlabel('x values (radians)')
plt.ylabel('sin(x)')
plt.title('Sine Wave Plot')
plt.grid(True)

# 4. Display the plot
plt.show()