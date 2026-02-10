from cmath import exp
from select import select
import sys, pygame, numpy as np, math

pygame.font.init()
def draw_text(screen, s, x, y, sz=20, color=(0,0,0)): #отрисовка текста
    screen.blit(pygame.font.SysFont('Comic Sans MS', sz).render(s, True, (0,0,0)), (x,y))
def lim_ang(ang, arc=3.141592653589793): # ограничение угла в пределах +/-pi
    ang=ang%(2*arc); return ang + (2*arc if ang<-arc else -2*arc if ang>arc else 0)

#NEW
class Landmark:
    def __init__(self, x, y):
            self.x, self.y=x,y
    def get_pos(self): return [self.x, self.y]
    def draw(self, screen):
        pygame.draw.circle(screen, (0,0,255), self.get_pos(), 5, 2)

class Particle:
    def __init__(self, x, y, robot, landmarks):
        self.x, self.y=x,y
    def calc_confidence(self, measurements):
        #ожидания по измерениям дальности
        self.expectations=[np.linalg.norm(np.subtract(self.get_pos(), lm.get_pos())) for lm in landmarks]
        err=sum((a-b)**2 for a, b in zip(self.expectations, measurements))
        self.q=math.exp(-0.00001*err)
    def get_pos(self): return [self.x, self.y]
class Robot:
    def __init__(self, x, y):
        self.radius, self.color=20, (0,0,0)
        self.x, self.y, self.a, self.vlin, self.vrot=x,y,0, 0, 0
        self.particles=[]
    def get_pos(self): return [self.x, self.y]
    def draw(self, screen):
        p1=np.array(self.get_pos())
        pygame.draw.circle(screen, self.color, p1, self.radius, 2)
        s,c=math.sin(self.a), math.cos(self.a)
        pygame.draw.line(screen, self.color, p1, p1+[self.radius*c, self.radius*s],2)
        for p in self.particles: pygame.draw.circle(screen, (200,0,200), p.get_pos(), 3, 1)
        pygame.draw.circle(screen, (0,0,0), self.get_filtered_location(), 3, 2)
    def sim(self, dt):
        s,c=math.sin(self.a), math.cos(self.a)
        prev_pos=self.x, self.y
        self.x, self.y=self.x+c*self.vlin*dt, self.y+s*self.vlin*dt
        self.a=lim_ang(self.a+self.vrot*dt)
        self.shift_particles(self.get_pos(), prev_pos)
    def measure_distance(self, lm): #с погрешностью
        L=np.linalg.norm(np.subtract(robot.get_pos(), lm.get_pos()))
        return L+np.random.normal(0,20)
    def init_particles(self, landmarks):
        self.particles=[Particle(np.random.normal(self.x,30), np.random.normal(self.y,30), self, landmarks) for i in range(50)]
    def shift_particles(self, pos, prev_pos):
        delta=np.subtract(pos, prev_pos)
        for p in self.particles: p.x, p.y=p.get_pos()+delta
    def update_particles(self, landmarks):
        measurements=[self.measure_distance(lm) for lm in landmarks]
        #рассчет достоверности частиц
        for p in self.particles: p.calc_confidence(measurements)
        #сортировка по убыванию достоверности частиц
        num0=len(self.particles)
        self.particles=sorted(self.particles, key=lambda p: -p.q)
        self.particles=self.particles[:len(self.particles)//2]
        best=self.particles[:]
        while len(self.particles)<num0:
            p0=np.random.choice(best)
            p_new=Particle(p0.x+np.random.normal(0,5), p0.y+np.random.normal(0,5), self, landmarks)
            self.particles.append(p_new)
    def get_filtered_location(self):
        return np.mean([p.get_pos() for p in self.particles], axis=0)

def draw_sight_lines(screen, robot, landmarks):
    for lm in landmarks:
        pygame.draw.line(screen, (200,200,200), robot.get_pos(), lm.get_pos(), 1)
        #L=np.linalg.norm(np.subtract(robot.get_pos(), lm.get_pos()))
        L = robot.measure_distance(lm)
        p=np.mean([robot.get_pos(), lm.get_pos()], axis=0)
        draw_text(screen, f"{L:.1f}", *p)

if __name__=="__main__":
    sz, timer, fps = (800, 600), pygame.time.Clock(), 20
    screen, dt = pygame.display.set_mode(sz), 1 / fps
    robot = Robot(200, 200)
    landmarks=[Landmark(100,100), Landmark(400,400)]
    robot.init_particles(landmarks)

    MODE="None"

    while True:
        for ev in pygame.event.get():
            if ev.type==pygame.QUIT: sys.exit(0)
            if ev.type == pygame.KEYDOWN:
                robot.vlin = 50 if ev.key == pygame.K_w else -50 if ev.key == pygame.K_s else robot.vlin
                robot.vrot = -1 if ev.key == pygame.K_a else 1 if ev.key == pygame.K_d else robot.vrot
                if ev.key==pygame.K_1:
                    MODE="Localize"

        robot.sim(dt)
        if MODE=="Localize": 
            robot.update_particles(landmarks)

        screen.fill((255, 255, 255))
        robot.draw(screen)
        for lm in landmarks: 
            lm.draw(screen)
        draw_sight_lines(screen, robot, landmarks)

        draw_text(screen, f"Test = {1}", 5, 5)
        pygame.display.flip(), timer.tick(fps)

#template file by S. Diane, RTU MIREA, 2024-2025