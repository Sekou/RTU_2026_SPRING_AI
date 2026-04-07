import sys, pygame, numpy as np, math

pygame.font.init()
def draw_text(screen, s, x, y, sz=15, c=(0, 0, 0)):  # отрисовка текста
    screen.blit(pygame.font.SysFont('Comic Sans MS', sz).render(s, True, c), (x, y))
def dist(p1, p2): return np.linalg.norm(np.subtract(p1, p2)) #расстояние между точками
def rot(v, ang): return np.dot([[-v[1], v[0]], v],[math.sin(ang), math.cos(ang)]) # поворот вектора на угол
def rot_arr(vv, ang): return [rot(v, ang) for v in vv] # функция для поворота массива на угол
def lim_ang(ang, arc=3.141592653589793): # ограничение угла в пределах +/-pi
    return ang%(2*arc)+2*arc*(int(ang%(2*arc)<-arc)-int(ang%(2*arc)>arc))
def draw_rot_rect(screen, color, pc, w, h, ang): #точка центра, ширина, высота и угол поворота прямогуольника
    pts = [[- w/2, - h/2],[+ w/2, - h/2],[+ w/2, + h/2],[- w/2, + h/2]]
    pygame.draw.polygon(screen, color, np.add(rot_arr(pts, ang), pc), 2)

sz = (800, 600)

class Cell:
    def __init__(self, x, y, sz, v0=0, fixed=False):
        self.x, self.y, self.sz, self.v, self.fixed = x, y, sz, v0, fixed
    def draw(self, screen):
        if self.v==100:
            pygame.draw.circle(screen, (0,255,0), (self.x, self.y), 7, 2 )
        if self.v<0:
            pygame.draw.rect(screen, (220,220,220), [self.x-self.sz/2, self.y-self.sz/2, self.sz+2, self.sz+2])
        pygame.draw.rect(screen, (0,0,0), [self.x-self.sz/2, self.y-self.sz/2, self.sz+2, self.sz+2], 2)
        draw_text(screen, f"{self.v:.1f}", self.x-self.sz//3, self.y)

class Grid:
    def __init__(self, x, y, sz, nx, ny):
        self.x, self.y, self.sz, self.nx, self.ny = x, y, sz, nx, ny
        self.cells=[]
        for iy in range(self.ny):
            row=[]
            for ix in range(self.nx):
                row.append(Cell(x+ix*sz, y+iy*sz, sz))
            self.cells.append(row)

    def add_obstacle(self, ix, iy):
        self.cells[iy][ix].v=-1
        self.cells[iy][ix].fixed=True

    def add_goal(self, ix, iy):
        self.cells[iy][ix].v=100
        self.cells[iy][ix].fixed=True

    def draw(self, screen):
        for iy in range(self.ny):
            for ix in range(self.nx):
                self.cells[iy][ix].draw(screen)

    def step_value_iter(self, gamma=0.3):
        vv=[]
        for iy in range(self.ny): vv.append([self.cells[iy][ix].v for ix in range(self.nx)])
        for iy in range(self.ny):
            for ix in range(self.nx):
                cell=self.cells[iy][ix]
                if cell.fixed: continue
                nbrs=[ix,iy]+np.array([[-1,-1],[-1,0],[-1,1],[0,-1],[0,1],[1,-1], [1,0], [1,1]])
                nbrs=[[ix,iy] for ix,iy in nbrs if 0<=ix<self.nx and 0<=iy<self.ny]
                max_nbr_v=0
                for jx,jy in nbrs:
                    cell2=self.cells[jy][jx]
                    R=cell2.v if cell2.fixed else 0 
                    max_nbr_v = max(max_nbr_v, R, cell2.v)
                vv[iy][ix]=(1-gamma)*cell.v + gamma*max_nbr_v #широко известная формула метода Value Iteration
        for iy in range(self.ny):
            for ix in range(self.nx):
                self.cells[iy][ix].v=vv[iy][ix]

if __name__=="__main__":
    screen, timer, fps =  pygame.display.set_mode(sz), pygame.time.Clock(), 20
    pygame.display.set_caption('Animation 2D')
    dt = 1 / fps
    #cell=Cell(200, 200, 100)
    grid=Grid(100, 100, 50, 10,6)
    grid.add_goal(9,5)

    grid.add_obstacle(3,3)
    grid.add_obstacle(4,3)
    grid.add_obstacle(5,3)
    grid.add_obstacle(6,3)
    grid.add_obstacle(6,2)

    while True:
        for ev in pygame.event.get():
            if ev.type==pygame.QUIT: sys.exit(0)
            if ev.type == pygame.KEYDOWN:
                if ev.key == pygame.K_1: grid.step_value_iter(0.3)

        screen.fill((255, 255, 255))     
        #cell.draw(screen)
        grid.draw(screen)

        draw_text(screen, f"Test = {1}", 5, 5)
        pygame.display.flip(), timer.tick(fps)

#template file by S. Diane, RTU MIREA, 2024-2026