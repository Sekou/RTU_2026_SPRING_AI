#TODO: можно ли отойти от логики Цетлина и генерировать связи автоматически как у муравья Лэнгтона?
#TODO: реализовать нейросетевое обучение по аналогии с автоматным и сравнить
from select import select
import sys, pygame, numpy as np, math
#https://stratum.ac.ru/education/textbooks/modelir/lection42.html

pygame.font.init()
def draw_text(screen, s, x, y, sz=20, color=(0,0,0)): #отрисовка текста
    screen.blit(pygame.font.SysFont('Comic Sans MS', sz).render(s, True, (0,0,0)), (x,y))
def lim_ang(ang, arc=3.141592653589793): # ограничение угла в пределах +/-pi
    ang=ang%(2*arc); return ang + (2*arc if ang<-arc else -2*arc if ang>arc else 0)
def dist(p1, p2): return np.linalg.norm(np.subtract(p2, p1)) # расстояние между точками

class Robot:
    def __init__(self, x, y):
        self.radius, self.color=20, (0,0,0)
        self.x, self.y, self.a, self.vlin, self.vrot=x,y,0, 0,0
        self.vlin_, self.vrot_ = 0,0
        self.history=[] #история наград
    def get_pos(self): return [self.x, self.y]
    def draw(self, screen):
        p1=np.array(self.get_pos())
        pygame.draw.circle(screen, self.color, p1, self.radius, 2)
        s,c=math.sin(self.a), math.cos(self.a)
        pygame.draw.line(screen, self.color, p1, p1+[self.radius*c, self.radius*s],2)
    def contains(self, obj): return dist(self.get_pos(), obj.get_pos())<self.radius
    def calc_reward(self): 
        return max( abs(self.vlin_)/50, abs(self.vrot_)/1 ) #редуцированная нечеткая логка
    def get_avg_reward(self, num_records):
        return np.mean(self.history[-min(num_records, len(self.history)):])
    def sim(self, dt, objs):
        oo=[o for o in objs if self.contains(o)]
        self.vlin_, self.vrot_=self.vlin/(1+len(oo)), self.vrot/(1+len(oo))
        s,c=math.sin(self.a), math.cos(self.a)
        self.x, self.y=self.x+c*self.vlin_*dt, self.y+s*self.vlin_*dt
        self.a=lim_ang(self.a+self.vrot_*dt)
        self.history.append(self.calc_reward())

def draw_plot(screen, arr, y0, k=50, w=800): #[*arr,*arr], [0]*2
    arr=arr if 2<len(arr)<w else [0,0] if len(arr)<2 else arr[-min(w, len(arr)):]
    for i, (v1,v2) in enumerate(zip(arr[:-1], arr[1:])):
        pygame.draw.line(screen, (0,0,255), [i,y0-v1*k], [i+1,y0-v2*k], 1)

class Obj: #небольшой объект на экране
    def __init__(self, x, y): self.x, self.y, self.sz = x, y, 20
    def get_pos(self): return [self.x, self.y]
    def get_bb(self): return [self.x-self.sz/2, self.y-self.sz/2, self.sz, self.sz]
    def set_pos(self, p): self.x, self.y=p
    def draw(self, screen): pygame.draw.rect(screen, (255, 190, 0), self.get_bb())

class State: #состояние конечного автомата
    def __init__(self, name, x, y):
        self.sz, self.x, self.y=45, x, y
        self.name=name
        self.next_a=[] #соседние состояния на случай положит. подкрепл.
        self.next_b=[] #соседние состояния на случай отрицат. подкрепл.
    def get_pos(self): return [self.x, self.y]
    def sim(self, reward): pass
    def draw(self, screen): 
        pygame.draw.circle(screen, (255,0,255), self.get_pos(), self.sz/2, 2)
        draw_text(screen, self.name, self.x-10, self.y-10)
    
class FSM: #Finite State Machine - конечный автомат
    def __init__(self):
        self.states=[]
        self.active_state=None
    def sim(self, reward): pass
    def draw(self, screen): pass

if __name__=="__main__":
    sz, timer, fps = (800, 600), pygame.time.Clock(), 20
    screen, dt = pygame.display.set_mode(sz), 1 / fps
    robot = Robot(200, 200)

    s=State("S10", 500,500)

    np.random.seed(1)
    objs=[ Obj(i,i) for i in range(50,600,50) ] +\
         [ Obj(600-i,i) for i in range(50,600,50) ] +\
             [ Obj(600, 400),  Obj(650, 400),  Obj(700, 400)  ] +\
                 [ Obj(650, 200),  Obj(700, 200),  Obj(750, 200)  ] +\
                 [ Obj(np.random.randint(50,750), np.random.randint(50,550)) for i in range(30)]

    while True:
        for ev in pygame.event.get():
            if ev.type==pygame.QUIT: sys.exit(0)
            if ev.type == pygame.KEYDOWN:
                robot.vlin = 50 if ev.key == pygame.K_w else -50 if ev.key == pygame.K_s else robot.vlin
                robot.vrot = -1 if ev.key == pygame.K_a else 1 if ev.key == pygame.K_d else robot.vrot

        robot.sim(dt,objs)

        screen.fill((255, 255, 255))
        robot.draw(screen)
        draw_plot(screen, robot.history, 599, 50)
        for o in objs: o.draw(screen)

        s.draw(screen)

        draw_text(screen, f"AvgRew({sz[0]}) = {robot.get_avg_reward(sz[0]):.2f}", 5, 5)
        pygame.display.flip(), timer.tick(fps)

#template file by S. Diane, RTU MIREA, 2024-2025
