import sys, pygame, numpy as np, math
#рассмотреть эвристику проверки пересеечения прогнозируемой дуги со стороной квадрата - как сигнала к изменениею управления
#рассмотреть прогноз выраженный в частичном следовании точке через одну p_goal=0.7*p_next+0.3*p_next_next

pygame.font.init()
def draw_text(screen, s, x, y):
    screen.blit(pygame.font.SysFont('Comic Sans MS', 20).render(s, True, (0,0,0)), (x,y))

sz = (800, 600)

def rot(v, ang): #функция для поворота на угол
    s, c = math.sin(ang), math.cos(ang)
    return [v[0] * c - v[1] * s, v[0] * s + v[1] * c]

def lim_ang(ang):
    while ang > math.pi: ang -= 2 * math.pi
    while ang <= -math.pi: ang += 2 * math.pi
    return ang

def rot_arr(vv, ang): return [rot(v, ang) for v in vv]# функция для поворота массива на угол

def dist(p1, p2): return np.linalg.norm(np.subtract(p1, p2))

def project_pt(segm, pt): # точка-проекция точки на отрезок
    v1, v2=np.subtract(segm[1], segm[0], dtype=float), np.subtract(pt, segm[0], dtype=float)
    return segm[0] + np.dot(v1, v2)*v1/np.dot(v1,v1)

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
    def sim_ahead(self, dt, nsteps, speed_, steer_):
        traj=[[self.x, self.y]]
        speed, steer=speed_, steer_
        x,y,alpha=self.x, self.y, self.alpha
        for i in range(nsteps):
            delta=rot([speed*dt, 0], alpha)
            x+=delta[0]
            y+=delta[1]
            if steer!=0:
                R = self.L/steer
                da = speed*dt/R
                alpha=lim_ang(alpha+da)
            traj.append([x,y])
        return traj
    def goto(self, pos, dt):
        v=np.subtract(pos, self.get_pos())
        aGoal=math.atan2(v[1], v[0])
        da=lim_ang(aGoal-self.alpha)
        self.steer += 0.5 * da * dt
        maxSteer=1
        if self.steer > maxSteer: self.steer = maxSteer
        if self.steer < -maxSteer: self.steer = -maxSteer
        self.speed = 50

if __name__=="__main__":
    screen, timer, fps = pygame.display.set_mode(sz), pygame.time.Clock(), 20

    robot=Robot(100, 100, 1)

    time=0
    ind=0
    goals = [[200,150], [600,150], [600,550], [200,550]]

    E=0

    MODE="None"
    while True:
        for ev in pygame.event.get():
            if ev.type==pygame.QUIT: sys.exit(0)
        dt=1/fps
        screen.fill((255, 255, 255))

        robot.goto(goals[ind], dt)
        if dist(robot.get_pos(), goals[ind])<50:
            ind=(ind+1)%4

        p_near=project_pt([goals[ind-1], goals[ind]], robot.get_pos())
        E+=dist(p_near, robot.get_pos())
        
        robot.sim(dt)

        def get_err(pos): 
            e1=dist(project_pt([goals[ind-1], goals[ind]], pos), pos)
            e2=dist(project_pt([goals[ind], goals[(ind+1)%len(goals)]], pos), pos)
            return 0.7*e1+0.3*e2

        if dist(robot.get_pos(), goals[ind])>100:
            MODE="PREDICT"
            control_variants=[]
            for a_steer in np.arange(-1,1,0.1):
                traj=robot.sim_ahead(dt, 50, 50, a_steer)
                e=np.mean([get_err(pt) for pt in traj])
                control_variants.append([e, a_steer, traj])

            control_variants=sorted(control_variants)
            best_traj=control_variants[0][2]
            robot.steer=control_variants[0][1]
        else: MODE="STANDARD"

        robot.draw(screen)

        for g in goals:
            pygame.draw.circle(screen, (255,0,0), g, 5, 2)
        for g in goals:
            pygame.draw.circle(screen, (0,255,0), p_near, 5, 2)
            pygame.draw.line(screen, (0,255,0), robot.get_pos(), p_near, 1)

        for i in range(len(goals)):
            pygame.draw.line(screen, (255,0,0), goals[i-1], goals[i], 2)

        for cv in control_variants:
            traj=cv[2]
            for i in range(1,len(traj)):
                color=(255,0,255) if traj==best_traj else (0,255,255)
                pygame.draw.line(screen, color, traj[i-1], traj[i], 2)

        draw_text(screen, f"Time = {time:.3f}", 5, 5)
        draw_text(screen, f"E = {E:.3f}", 5, 25)
        draw_text(screen, f"{MODE}", robot.x, robot.y-35)


       
        pygame.display.flip(), timer.tick(fps)
        time+=dt

#template file by S. Diane, RTU MIREA, 2024-2026