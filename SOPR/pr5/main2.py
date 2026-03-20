import sys, pygame, numpy as np, math

pygame.font.init()
def draw_text(screen, s, x, y, sz=20, color=(0,0,0)): #отрисовка текста
    screen.blit(pygame.font.SysFont('Comic Sans MS', sz).render(s, True, (0,0,0)), (x,y))
def lim_ang(ang, arc=3.141592653589793): # ограничение угла в пределах +/-pi
    ang=ang%(2*arc); return ang + (2*arc if ang<-arc else -2*arc if ang>arc else 0)
def rot(v, ang): return np.dot([[-v[1], v[0]], v],[math.sin(ang), math.cos(ang)]) # поворот вектора на угол
def rot_arr(vv, ang): return [rot(v, ang) for v in vv] # функция для поворота массива на угол
# отрисовка стрелки по точке и углу
def draw_arrow(screen, color, p0, ang, lenpx, w):
    p1 = [p0[0] + lenpx * math.cos(ang), p0[1] + lenpx * math.sin(ang)]
    p2 = [p1[0] - 10 * math.cos(ang + 0.5), p1[1] - 10 * math.sin(ang + 0.5)]
    p3 = [p1[0] - 10 * math.cos(ang - 0.5), p1[1] - 10 * math.sin(ang - 0.5)]
    for a,b in [[p0, p1], [p1, p2], [p1, p3]]: pygame.draw.line(screen, color, a, b, w)
def check_intersection(A,B,C,D): # проверка пересечения двух отрезков
    ccw = lambda A, B, C: (C[1] - A[1]) * (B[0] - A[0]) > (B[1] - A[1]) * (C[0] - A[0])
    return ccw(A,C,D) != ccw(B,C,D) and ccw(A,B,C) != ccw(A,B,D)

class Robot:
    def __init__(self, x, y):
        self.radius, self.color=20, (0,0,0)
        self.x, self.y, self.a, self.vlin, self.vrot=x,y,0, 0,0
    def get_pos(self): return [self.x, self.y]
    def draw(self, screen):
        p1=np.array(self.get_pos())
        pygame.draw.circle(screen, self.color, p1, self.radius, 2)
        s,c=math.sin(self.a), math.cos(self.a)
        pygame.draw.line(screen, self.color, p1, p1+[self.radius*c, self.radius*s],2)
    def sim(self, dt):
        s,c=math.sin(self.a), math.cos(self.a)
        self.x, self.y=self.x+c*self.vlin*dt, self.y+s*self.vlin*dt
        self.a=lim_ang(self.a+self.vrot*dt)

class Bar: #балка
    def __init__(self, x, y, ang, L, W): 
        self.x, self.y, self.ang, self.L, self.W = x, y, ang, L, W
        self.a, self.v, self.m=np.zeros(2), np.zeros(2), 1
        self.eps, self.w, self.J=0, 0, 500
        self.F, self.M=np.zeros(2), 0
    def reset(self): self.F, self.M=np.zeros(2), 0
    def get_pos(self): return [self.x, self.y]
    def get_all_pts(self): 
        pp=[[i*self.L/2, j*self.W/2] for i,j in [[-1,-1],[1,-1],[1,1],[-1,1]]]
        return np.add(rot_arr(pp, self.ang), self.get_pos())
    def local_to_global_pt(self, pt): return np.array(rot(pt, self.ang)) + self.get_pos()
    def set_pos(self, p): self.x, self.y=p
    def draw(self, screen):
        pp=self.get_all_pts()
        pygame.draw.lines(screen, (0, 0, 0), True, pp, 2)
        draw_arrow(screen, (255,0,0), self.get_pos(), math.atan2(*self.F[::-1]), 20, 2)
        c, m = ((0,255,0), self.M) if self.M>=0 else ((255,0,0), -self.M)
        pygame.draw.circle(screen, c, self.get_pos(), m/100, 2)
    def apply_force(self, local_pt, global_F):
        self.F+=global_F
        lF=np.linalg.norm(local_pt)
        vec=np.array(local_pt)/np.linalg.norm(local_pt)
        vec=rot(vec, self.ang)
        vec2=rot(vec, np.pi/2)
        F=np.dot(vec2, global_F)
        self.M+=F*lF
    def sim(self, dt):
        self.a=np.array(self.F)/self.m
        self.v+=self.a*dt
        self.v*=0.9
        self.x,self.y=self.x+self.v[0]*dt,self.y+self.v[1]*dt
        self.eps=self.M/self.J
        self.w+=self.eps*dt
        self.w*=0.85
        self.ang=self.ang+self.w*dt
    def intersects(self, segment):
        pts=self.get_all_pts()
        for a,b in zip(pts, list(pts[1:])+list(pts[:1])):
            if check_intersection(a, b, *segment):
                return True
        return False

def dist(p1, p2): return np.linalg.norm(np.subtract(p2, p1)) # расстояние между точками

class Node:
    def __init__(self, x, y): self.x, self.y, self.edges=x, y, []
    def get_pos(self): return [self.x, self.y]
    def draw(self, screen):
        pygame.draw.circle(screen, (255,0,0), self.get_pos(), 7, 1)
        for e in self.edges: pygame.draw.line(screen, (255,0,0), e.n1.get_pos(), e.n2.get_pos(), 1)
class Edge:
    def __init__(self, n1, n2): self.n1,self.n2,self.w=n1, n2, dist(n1.get_pos(), n2.get_pos())
class Graph:
    def __init__(self, objs, step):
        pts = [[[x, y] for x in range(0,sz[0],step)] for y in range(0,sz[1],step) ]
        self.nodes=[[ Node(*p) for p in line] for line in pts]
        def get_nbrs(ix, iy, nodes):
            inds=[[-1,-1], [0,-1], [1,-1],[-1,0], [1,0], [-1,1], [0,1], [1,1]]
            inds=[[x+ix, y+iy] for x, y in inds]
            inds=[[x, y] for x, y in inds if 0<=y<len(nodes) and 0<=x<len(nodes[y])] #ИСПРАВЛЕНА ОШИБКА nodes вместо inds
            p1=self.nodes[iy][ix].get_pos()
            print("p1=", p1)
            print("p2p2=",[self.nodes[i][j].get_pos() for j,i in inds])
            collisions = [objs[0].intersects([p1, self.nodes[i][j].get_pos()]) for j,i in inds]
            print(collisions)
            inds=[i for i,c in zip(inds,collisions) if not c]
            print(inds)
            return [nodes[y][x] for x, y in inds]
        print(len(pts))
        for i in range(len(self.nodes)):
            for j in range(len(self.nodes[0])):
                nbrs=get_nbrs(j, i, self.nodes)
                #print(i, j, "=", len(nbrs))
                for nb in nbrs:
                    self.nodes[i][j].edges.append(Edge(self.nodes[i][j], nb))
                    nb.edges.append(Edge(nb, self.nodes[i][j]))
    def get_all_nodes(self): return [n for row in self.nodes for n in row]
    def draw(self, screen):
        for i in range(len(self.nodes)):
            for n in self.nodes[i]:
                n.draw(screen)
    def find_route(self, n1, n2):
        all_nodes=self.get_all_nodes()
        for n in all_nodes: 
            n.visited, n.D, n.route = False, 100500, []
        n1.D, n1.route, wave = 0, [n1], [n1]
        while len(wave):
            v=wave.pop(np.argmin([n.D for n in wave]))
            v.visited, next = True, [e for e in v.edges if not e.n2.visited]
            for e in next: #если текущ. вершина лучше соседа, то обновл. соседа
                if e.n2.D > v.D+e.w: e.n2.D, e.n2.route=v.D+e.w, v.route+[e.n2]
                if not e.n2 in wave: wave.append(e.n2) #берем соседа в фронт поиска
        return list(reversed(n2.route))


def build_graph(obstacles, step):
    pass

if __name__=="__main__":
    sz, timer, fps = (800, 600), pygame.time.Clock(), 20
    screen, dt = pygame.display.set_mode(sz), 1 / fps
    robot = Robot(200, 200)
    robot2 = Robot(200, 400)

    obstacle=Bar(400,300, 0, 200,150)
    objs=[obstacle]

    bar = Bar(400, 250, 1, 200, 30)

    graph=Graph(objs, 100)

    route=None

    line=[[400, 300], [500, 400]]

    while True:
        for ev in pygame.event.get():
            if ev.type==pygame.QUIT: sys.exit(0)
            if ev.type == pygame.KEYDOWN:
                if ev.key==pygame.K_1:
                    route=graph.find_route(graph.nodes[0][0],graph.nodes[-1][-1])
                #robot.vlin = 50 if ev.key == pygame.K_w else -50 if ev.key == pygame.K_s else robot.vlin
                #robot.vrot = -1 if ev.key == pygame.K_a else 1 if ev.key == pygame.K_d else robot.vrot
                #robot2.vlin = 50 if ev.key == pygame.K_i else -50 if ev.key == pygame.K_k else robot2.vlin
                #robot2.vrot = -1 if ev.key == pygame.K_j else 1 if ev.key == pygame.K_l else robot2.vrot

                robot2.vlin=robot.vlin = 50 if ev.key == pygame.K_w else -50 if ev.key == pygame.K_s else robot.vlin
                robot2.vrot=robot.vrot = -1 if ev.key == pygame.K_a else 1 if ev.key == pygame.K_d else robot.vrot

        robot.sim(dt)
        robot2.sim(dt)

        #bar.ang+=0.05

        bar.reset()
        #bar.apply_force((bar.L/2, 0), (10,0))
        pF=bar.local_to_global_pt((bar.L/2, 0))
        delta=np.subtract(robot.get_pos(), pF)
        bar.apply_force((bar.L/2, 0), delta*10)

        pF2=bar.local_to_global_pt((-bar.L/2, 0))
        delta2=np.subtract(robot2.get_pos(), pF2)
        bar.apply_force((-bar.L/2, 0), delta2*10)

        bar.sim(dt)

        screen.fill((255, 255, 255))
        robot.draw(screen)
        robot2.draw(screen)
        obstacle.draw(screen)
        graph.draw(screen)
        
        if route is not None:
            for i in range(1, len(route)):
                pygame.draw.line(screen, (0,0,255), route[i-1].get_pos(), route[i].get_pos(), 2)

        inters=objs[0].intersects(line)
        color = (255, 255, 0) if inters else (0, 255, 0)
        pygame.draw.line(screen, color, *line, 5) #отладка (методом упрощения проблемы - minimal working example)
        pp=objs[0].get_all_pts()
        for i in range(len(pp)):
            pygame.draw.line(screen, (0,255,255), pp[i-1], pp[i], 2)

        inters2=[check_intersection(pp[i-1], pp[i], *line) for i in range(len(pp))]
        print(inters2)

        bar.draw(screen)

        draw_text(screen, f"Test = {1}", 5, 5)
        pygame.display.flip(), timer.tick(fps)

#template file by S. Diane, RTU MIREA, 2024-2025
