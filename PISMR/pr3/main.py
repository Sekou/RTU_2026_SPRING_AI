import itertools
import sys, pygame
import numpy as np
import math

pygame.font.init()
font = pygame.font.SysFont('Comic Sans MS', 20)
def drawText(screen, s, x, y):
    surf=font.render(s, True, (0,0,0))
    screen.blit(surf, (x,y))

sz = (800, 600)

def rot(v, ang): #функция для поворота на угол
    s, c = math.sin(ang), math.cos(ang)
    return [v[0] * c - v[1] * s, v[0] * s + v[1] * c]

def limAng(ang):
    while ang > math.pi: ang -= 2 * math.pi
    while ang <= -math.pi: ang += 2 * math.pi
    return ang

def rotArr(vv, ang): # функция для поворота массива на угол
    return [rot(v, ang) for v in vv]

def dist(p1, p2):
    return np.linalg.norm(np.subtract(p1, p2))

def drawRotRect(screen, color, pc, w, h, ang): #точка центра, ширина высота прямоуг и угол поворота прямогуольника
    pts = [
        [- w/2, - h/2],
        [+ w/2, - h/2],
        [+ w/2, + h/2],
        [- w/2, + h/2],
    ]
    pts = rotArr(pts, ang)
    pts = np.add(pts, pc)
    pygame.draw.polygon(screen, color, pts, 2)

class Link:
    def __init__(self, L=20, ang=0, pos=[0,0]):
        self.pos=pos
        self.L=L
        self.ang=ang
        self.global_ang=0
        self.ext_ang=0 #NEW!!!
        self.vrot=0
    def get_end_pos(self):
        a=self.ext_ang+self.global_ang
        return np.array(self.pos) + [self.L*math.cos(a), self.L*math.sin(a)]
    def sim(self, dt):
        self.ang+=self.vrot*dt
    def draw(self, screen):
        pygame.draw.line(screen, (0,0,0), self.pos, self.get_end_pos(), 2)

class Manipulator:
    def __init__(self, pos0, num_links, L0):
        self.pos0=pos0
        self.links=[Link(L0 / (1+i), 0, pos0) for i in range(num_links)]
    def sim(self, dt):
        for l in self.links: l.sim(dt)
        self.upd_poses()
    def upd_poses(self):
        self.links[0].pos=self.pos0
        self.links[0].global_ang=self.links[0].ext_ang + self.links[0].ang
        for i in range(1,len(self.links)): 
            self.links[i].global_ang = self.links[i-1].global_ang + self.links[i].ang
            self.links[i].pos=self.links[i-1].get_end_pos() 
    def draw(self, screen):
        for l in self.links: l.draw(screen)

    def get_end_pos(self):#NEW!!!
        return self.links[-1].get_end_pos()
    def solve_ik(self, goal):
        for l in self.links[::-1]:
            d=np.array(l.pos) - goal
            e1=e0=np.linalg.norm(self.get_end_pos()-np.array(goal))            
            eta=0.01
            for i in range(10):
                delta=limAng(math.atan2(d[1], d[0]) - l.global_ang)
                l.ang+=eta*np.sign(delta)
                l.global_ang+=eta*np.sign(delta)
                e1=np.linalg.norm(l.get_end_pos()-np.array(goal))
                if e1>e0:
                    l.ang-=eta*np.sign(delta)
                    l.global_ang-=eta*np.sign(delta)
                    break
class Robot:
    def __init__(self, x, y, alpha):
        self.x=x
        self.y=y
        self.alpha=alpha
        self.L=70
        self.W=40
        self.speed=0
        self.steer=0
        self.traj=[] #точки траектории
        self.last_da=0
        self.manip=Manipulator(self.getPos(), 3, 50)
        
    def getPos(self):
        return [self.x, self.y]
    def clear(self):
        self.traj = []
        self.vals1 = []
        self.vals2 = []

    def draw(self, screen):
        p=np.array(self.getPos())
        drawRotRect(screen, (0,0,0), p,
                    self.L, self.W, self.alpha)
        dx=self.L/3
        dy=self.W/3
        dd=[[-dx,-dy], [-dx,dy], [dx,-dy], [dx,dy]]
        dd=rotArr(dd, self.alpha)
        kRot=[0,0,1,1]
        for d, k in zip(dd, kRot):
            drawRotRect(screen, (0, 0, 0), p+d,
                        self.L/5, self.W/5, self.alpha+k*self.steer)
        for i in range(len(self.traj)-1):
            pygame.draw.line(screen, (0,0,255), self.traj[i], self.traj[i+1], 1)
        self.manip.draw(screen)
    def sim(self, dt):
        self.addedTrajPt = False
        delta=[self.speed*dt, 0]
        delta=rot(delta, self.alpha)
        self.x+=delta[0]
        self.y+=delta[1]
        if self.steer!=0:
            R = self.L/self.steer
            da = self.speed*dt/R
            self.alpha+=da
        
        self.manip.pos0=self.getPos()
        self.manip.links[0].global_ang=self.alpha
        self.manip.sim(dt)

        p=self.getPos()
        if len(self.traj)==0 or dist(p, self.traj[-1])>10:
            self.traj.append(self.getPos())
            self.addedTrajPt=True

    def goto(self, pos, dt):
        v=np.subtract(pos, self.getPos())
        aGoal=math.atan2(v[1], v[0])
        da=limAng(aGoal-self.alpha)
        self.steer += (2 * da + 1 *(da-self.last_da)/dt )* dt
        maxSteer=1
        if self.steer > maxSteer: self.steer = maxSteer
        if self.steer < -maxSteer: self.steer = -maxSteer
        self.speed = 50
        self.last_da=da

if __name__=="__main__":
    screen = pygame.display.set_mode(sz)
    timer = pygame.time.Clock()
    fps = 20

    robot=Robot(100, 100, 1)


    manip=Manipulator((200, 200), 3, 50)

    time=0
    goal = [600,400]

    while True:
        for ev in pygame.event.get():
            if ev.type==pygame.QUIT:
                sys.exit(0)
            if ev.type==pygame.MOUSEBUTTONDOWN:
                goal=ev.pos
        dt=1/fps
        screen.fill((255, 255, 255))

        #robot.goto(goal, dt)

        robot.manip.solve_ik(goal)
        robot.sim(dt)

        manip.solve_ik(goal)
        manip.sim(dt)

        robot.draw(screen)
        manip.draw(screen)
        
        pygame.draw.circle(screen, (255,0,0), goal, 5, 2)

        drawText(screen, f"Time = {time:.3f}", 5, 5)
       
        pygame.display.flip()
        timer.tick(fps)
        time+=dt

#template file by S. Diane, RTU MIREA, 2024