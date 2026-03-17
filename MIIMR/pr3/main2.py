from cProfile import label
import numpy as np
import matplotlib.pyplot as plt

#https://cyberleninka.ru/article/n/odnomernyy-filtr-kalmana-v-algoritmah-chislennogo-resheniya-zadachi-optimalnogo-dinamicheskogo-izmereniya/viewer

def filter_moving_average(yy, length):
    return [np.mean(yy[max(0,i-length):i+1]) for i in range(len(yy))]

#def filter_exponential(yy, miu, length=10): #TODO отладить
    #return [ sum([v**(miu*j) for j,v in enumerate(yy[i : max(0,i-length)-1: -1]) ]) for i in range(len(yy))]

def filter_exponential(yy, miu, length=10): #не гасит амплитуду, не срезает пики
    res=[]
    for i in range(len(yy)):
        s, m=0, 0
        for j,v in list(enumerate(yy[i : max(0,i-length)-1: -1])):
            s+=v*miu**j
            m+=miu**j
        res.append(s/(1 if m==0 else m))
    return res


K=0.5 #коэфф. доверия (фильтр доверяет сигналу)
def filter_Kalman_test(yy0):
    res=np.zeros(len(yy0))
    res[0]=yy0[0]
    for i in range(len(yy0)):
        y_=res[max(0,i-1)]
        res[i]=y_ + K*(yy0[i]-y_) #см. формула (10), Шестаков 2021
    return res

def get_w(yy0, yy, i, N): #формула (13), Шестаков 2021
    def get_avg_delta(yy0, yy, i, N):
        tmp=0
        for m in range(N):
            delta=yy0[max(0,i-m)]-yy[max(0,i-m,-1)]
            tmp+=delta
        return tmp/N
    w=0
    for m in range(N):
        delta=yy0[max(0,i-m)]-yy[max(0,i-m,-1)] - get_avg_delta(yy0, yy, i, N)
        w+=delta**2
    return w / (N-1)

def get_sigma2(yy0, i, N):
    m=np.mean(yy0[max(0,i-N):i+1:1])
    return np.sum((np.array(yy0[max(0,i-N):i+1:1])-m)**2)

def filter_Kalman(yy0):
    yy=np.zeros(len(yy0))
    yy[0]=yy0[0]
    P,P_=0.1,0.1 #задаем небольшие значения чтоб не делить на ноль
    #в местах графика с большим шумом коэф. доверия K будет расти, 
    #в стабильных же участках графика будет падать
    K=0.5 
    for i in range(len(yy)):
        y_=yy[max(0,i-1)]
        P_=P+get_w(yy0, yy, i, N=10)
        sigma2=get_sigma2(yy0, i, N=10)
        if i==0: sigma2=0.01
        K=P_/(P_+sigma2)
        P=(1-K)*P_ #см. формула (14), Шестаков 2021
        yy[i]=y_ + K*(yy0[i]-y_) #см. формула (10), Шестаков 2021
        print(K)
    return yy


np.random.seed(1)

# 1. Create data for the x-axis (angles in radians)
# Generate 100 evenly spaced points from 0 to 2*pi
xx = np.linspace(0, 10 * 2 * np.pi, 1000)

# 2. Calculate the sine of all y-axis points
yy = np.sin(xx) + np.random.normal(0, 0.1, 1000)

i=5
length=10
test=yy[i : max(0,i-length): -1]
test2=list(enumerate(test))
print(test2)

yy1 = filter_moving_average(yy, 50)
yy2 = filter_exponential(yy, 0.95)
yy3 = filter_Kalman(yy)

# 3. Plot the data
plt.plot(xx, yy, label="sin(x)")
plt.plot(xx, yy1, label="moving_average")
plt.plot(xx, yy2, label="exponential")
plt.plot(xx, yy3, label="Kalman")

# Optional: Add labels, a title, and a grid for clarity
plt.xlabel('x values (radians)')
plt.legend()
plt.title('Sine Wave Plot')
plt.grid(True)

# 4. Display the plot
plt.show()