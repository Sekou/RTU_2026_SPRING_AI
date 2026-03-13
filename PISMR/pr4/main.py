import sys, pygame, numpy as np, math

pygame.font.init()
def draw_text(screen, s, x, y):
    screen.blit(pygame.font.SysFont('Comic Sans MS', 20).render(s, True, (0,0,0)), (x,y))

sz = (800, 600)

RRT_STEP=min(sz)/10

def rot(v, ang): #функция для поворота на угол
    s, c = math.sin(ang), math.cos(ang)
    return [v[0] * c - v[1] * s, v[0] * s + v[1] * c]

def lim_ang(ang):
    while ang > math.pi: ang -= 2 * math.pi
    while ang <= -math.pi: ang += 2 * math.pi
    return ang

def rot_arr(vv, ang): return [rot(v, ang) for v in vv]# функция для поворота массива на угол

def dist(p1, p2): return np.linalg.norm(np.subtract(p1, p2))

def draw_rot_rect(screen, color, pc, w, h, ang): #точка центра, ширина высота прямоуг и угол поворота прямогуольника
    pts = [[- w/2, - h/2],[+ w/2, - h/2],[+ w/2, + h/2],[- w/2, + h/2]]
    pygame.draw.polygon(screen, color, np.add(rot_arr(pts, ang), pc), 2)

class Robot:
    def __init__(self, x, y, alpha):
        self.x, self.y = x, y
        self.alpha=alpha
        self.L, self.W = 70, 40
        self.speed, self.steer = 0, 0
        self.traj=[] #точки траектории
    def get_pos(self): return [self.x, self.y]
    def clear(self):
        self.traj, self.vals1, self.vals2  = [], [], []
    def draw(self, screen):
        p=np.array(self.get_pos())
        draw_rot_rect(screen, (0,0,0), p, self.L, self.W, self.alpha)
        dx, dy=self.L/3, self.W/3
        dd=rot_arr([[-dx,-dy], [-dx,dy], [dx,-dy], [dx,dy]], self.alpha)
        for d, k in zip(dd, [0,0,1,1]):
            draw_rot_rect(screen, (0, 0, 0), p+d,
                        self.L/5, self.W/5, self.alpha+k*self.steer)
        for i in range(len(self.traj)-1):
            pygame.draw.line(screen, (0,0,255), self.traj[i], self.traj[i+1], 1)
    def sim(self, dt):
        self.added_traj_pt = False
        delta=rot([self.speed*dt, 0], self.alpha)
        self.x+=delta[0]
        self.y+=delta[1]
        if self.steer!=0:
            R = self.L/self.steer
            da = self.speed*dt/R
            self.alpha=lim_ang(self.alpha+da)
        if len(self.traj)==0 or dist(self.get_pos(), self.traj[-1])>10:
            self.traj.append(self.get_pos())
            self.added_traj_pt=True
    def goto(self, pos, dt):
        v=np.subtract(pos, self.get_pos())
        aGoal=math.atan2(v[1], v[0])
        da=lim_ang(aGoal-self.alpha)
        self.steer += 0.5 * da * dt
        maxSteer=1
        if self.steer > maxSteer: self.steer = maxSteer
        if self.steer < -maxSteer: self.steer = -maxSteer
        self.speed = 50

def check_intersection(A,B,C,D): # проверка пересечения двух отрезков
    ccw = lambda A, B, C: (C[1] - A[1]) * (B[0] - A[0]) > (B[1] - A[1]) * (C[0] - A[0])
    return ccw(A,C,D) != ccw(B,C,D) and ccw(A,B,C) != ccw(A,B,D)

class Obj: #небольшой объект на экране
    def __init__(self, x, y, sz): self.x, self.y, self.sz = x, y, sz
    def get_pos(self): return [self.x, self.y]
    def get_bb(self): return [self.x-self.sz/2, self.y-self.sz/2, self.sz, self.sz]
    def get_segments(self): 
        pp=[[self.x+i*self.sz/2, self.y+j*self.sz/2] for i,j in [[-1,-1],[1,-1],[1,1],[-1,1]]]
        return list(zip(pp, pp[1:]+pp[:1]))
    def set_pos(self, p): self.x, self.y=p
    def draw(self, screen): pygame.draw.rect(screen, (0, 0, 0), self.get_bb(), 2, 2)
    def intersects(self, p1, p2): 
        return any([check_intersection(A,B, p1, p2) for A, B in self.get_segments()])

class RRTNode:
    def __init__(self, x, y, prev_pt=None): 
        self.x, self.y, self.prev_pt, self.next_pts = x, y, prev_pt, []
    def get_pos(self): return [self.x, self.y]
    def draw(self, screen): 
        pygame.draw.circle(screen, (255, 0, 255), self.get_pos(), 3, 2)
        if self.prev_pt is not None: 
            pygame.draw.line(screen, (0, 0, 0), self.get_pos(), self.prev_pt.get_pos(), 1)
    def gen_next_pt_test(self):
        x, y=np.random.normal(self.x, RRT_STEP*10), np.random.normal(self.y, RRT_STEP*10)
        dx,dy=x-self.x, y-self.y
        v=[dx, dy]/np.linalg.norm([dx, dy])*RRT_STEP
        n=RRTNode(self.x+v[0], self.y+v[1], self)
        self.next_pts.append(n)
        return n
    def gen_next_pt(self, target, save=True):
        dx,dy=target[0]-self.x, target[1]-self.y
        v=[dx, dy]/np.linalg.norm([dx, dy])*RRT_STEP
        n=RRTNode(self.x+v[0], self.y+v[1], self)
        if save: self.next_pts.append(n)
        return n

#модифицированная версия RRT
def run_RRT_iter_test(nodes, objs):
    ind = np.random.randint(len(nodes))
    nodes.append(nodes[ind].gen_next_pt_test())

#отличие от run_RRT_iter_test - в том, что отрезки никогда не пересекутся
def run_RRT_iter(nodes, goal, objs):
    #target=[np.random.randint(v) for v in sz]
    target=[np.random.normal(goal[0], RRT_STEP), np.random.normal(goal[1], RRT_STEP)]
    dd=[dist(target, n.get_pos()) for n in nodes]
    ind = np.argmin(dd)
    nodes.append(nodes[ind].gen_next_pt(target))

#отличие: проверка на препятствия
def run_RRT_iter2(nodes, goal, objs):
    collision=True
    while collision:
        #target=[np.random.randint(v) for v in sz] #БЕЗ ЭВРИСТИКИ
        target=[np.random.normal(goal[0], RRT_STEP), np.random.normal(goal[1], RRT_STEP)] #С ЭВРИСТИКОЙ
        dd=[dist(target, n.get_pos()) for n in nodes]
        ind = np.argmin(dd)
        pt=nodes[ind].gen_next_pt(target, False) #False - добавлять узел будем вручную
        segment=[pt.get_pos(), nodes[ind].get_pos()]
        collision=any([o.intersects(*segment) for o in objs])
    nodes.append(pt)
    nodes[ind].next_pts.append(pt)

if __name__=="__main__":
    screen, timer, fps = pygame.display.set_mode(sz), pygame.time.Clock(), 20

    robot=Robot(100, 100, 1)
    objs = [Obj(300, 400, 50), Obj(400, 370, 50), Obj(500, 300, 50), Obj(200, 250, 50), Obj(450, 200, 50)]

    time=0
    start = robot.get_pos()
    goal = [600,400]

    nodes=[RRTNode(*start)]
    route=[]

    while True:
        for ev in pygame.event.get():
            if ev.type==pygame.QUIT: sys.exit(0)
            if ev.type==pygame.KEYDOWN: 
                if ev.key==pygame.K_1: run_RRT_iter(nodes, objs)
                if ev.key==pygame.K_2: run_RRT_iter2(nodes, goal, objs)
                if ev.key==pygame.K_3: 
                    nodes=[RRTNode(*start)]
                    while True:
                        dd=[dist(n.get_pos(),goal) for n in nodes]
                        nearest=nodes[np.argmin(dd)]
                        if min(dd)<RRT_STEP: break
                        run_RRT_iter2(nodes, goal, objs)
                    route=[nearest]
                    while nearest.prev_pt is not None: 
                        route.insert(0, nearest.prev_pt)
                        nearest=nearest.prev_pt

        dt=1/fps
        screen.fill((255, 255, 255))
        robot.goto(goal, dt)
        robot.sim(dt)
        robot.draw(screen)
        for obj in objs: obj.draw(screen)
        for n in nodes: n.draw(screen)
        if len(route): 
            pygame.draw.lines(screen, (0,0,255), False, [n.get_pos() for n in route], 2)

        pygame.draw.circle(screen, (0,255,0), start, 5, 2)
        pygame.draw.circle(screen, (255,0,0), goal, 5, 2)
        draw_text(screen, f"Time = {time:.3f}", 5, 5)
       
        pygame.display.flip(), timer.tick(fps)
        time+=dt

#template file by S. Diane, RTU MIREA, 2024-2026
