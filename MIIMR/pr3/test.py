import numpy as np

arr=[1, 2, 3, 4, 5]

print(arr[0:5:1][::-1])
print(arr[4:0:-1])


yy0=[1,2,2,3, 5, 2, 2, 2, 2, 2, 2, 2]
m=np.mean(yy0)
N=4
i=5
v=np.sum( (np.array(yy0[max(0,i-N):i+1:1]) - m) **2)**0.5

def get_sigma(yy0, i, N):
    m=np.mean(yy0[max(0,i-N):i+1:1])
    return np.sum((np.array(yy0[max(0,i-N):i+1:1])-m)**2)**0.5


print(v)
print(get_sigma(yy0, 5, 4))