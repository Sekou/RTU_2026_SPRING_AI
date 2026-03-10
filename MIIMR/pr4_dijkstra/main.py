import sys, pygame, numpy as np

from torch import dtype

pygame.font.init()

def draw_text(screen, s, x, y, sz=15, c=(0, 0, 0)):  # отрисовка текста
    screen.blit(pygame.font.SysFont('Comic Sans MS', sz).render(s, True, c), (x, y))

sz = (800, 600)

def get_normal(p1, p2): #вращает вектор по часовой стрелке
    v=np.subtract(p2, p1)
    return np.array([v[1],-v[0]])/np.linalg.norm(v)

class Ngon:
    def __init__(self, pts):
        self.pts=pts
        self.inflated=[]
    def draw(self, screen):
        for i in range(len(self.pts)): # for p1,p2 in zip(self.pts, self.pts[1:]+self.pts[:1]):
            pygame.draw.line(screen, (0,0,0), self.pts[i-1], self.pts[i], 2)
        if len(self.inflated):
            for i in range(len(self.inflated)):
                pygame.draw.line(screen, (0, 0, 255), self.inflated[i - 1], self.inflated[i], 1)
    def inflate(self, r):
        vv=[] #TODO: сделать запас по радиусу или 3-ю точку посередине между p1 p2
        for i in range(len(self.pts)):
            p1, p2 = self.pts[i-1], self.pts[i]
            n=get_normal(p1, p2)
            vv.extend([p1+n*r, p2+n*r])
        self.inflated=vv
        return vv
    def check_collision(self, p1, p2):
        pp=self.inflated if len(self.inflated) else self.pts
        for i in range(len(pp)):
            # u=np.array(np.subtract(p2, p1), dtype=np.float64)
            # u*=0.1/np.linalg.norm(u) #TODO отладить соединения чтоб правильно создавались
            if check_intersection(pp[i - 1], pp[i], p1, p2): return True
        return False

def dist(p1, p2): return np.linalg.norm(np.subtract(p1, p2))
def check_intersection(A,B,C,D): # проверка пересечения двух отрезков
    ccw = lambda A, B, C: (C[1] - A[1]) * (B[0] - A[0]) > (B[1] - A[1]) * (C[0] - A[0])
    return ccw(A,C,D) != ccw(B,C,D) and ccw(A,B,C) != ccw(A,B,D)
# def get_segm_intersection(A, B, C, D): # поиск точки пересечения двух отрезков
#     (x1, y1), (x2, y2), (x3, y3), (x4, y4) = A, B, C, D
#     denom = (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4)
#     if denom == 0: return None  # отрезки параллельны или совпадают
#     t = ((x1 - x3) * (y3 - y4) - (y1 - y3) * (x3 - x4)) / denom
#     u = -((x1 - x2) * (y1 - y3) - (y1 - y2) * (x1 - x3)) / denom
#     if 0 <= t <= 1 and 0 <= u <= 1: return (x1 + t * (x2 - x1), y1 + t * (y2 - y1))
#     return None


class Node:
    def __init__(self, x, y):
        self.x, self.y, self.edges=x, y, []
    def init_dijkstra(self): self.visited, self.D, self.route= False, 100500, [] #для Дейкстры
    def get_pos(self): return [self.x, self.y]
    def draw(self, screen):
        pygame.draw.circle(screen, (255,0,0), self.get_pos(), 7, 1)
        for e in self.edges: pygame.draw.line(screen, (255,0,0), e.n1.get_pos(), e.n2.get_pos(), 1)
class Edge:
    def __init__(self, n1, n2): self.n1=n1; self.n2=n2; self.w=dist(n1.get_pos(), n2.get_pos())
class Graph:
    def __init__(self, start, goal, objs):
        pts = [] #TODO сократить 2 строки в 1
        for ng in objs: pts.extend(ng.inflated)
        self.nodes=[Node(*start)] + [Node(x,y) for x,y in pts] + [Node(*goal)]
        for i in range(len(self.nodes)):
            #TODO: понять пч пересечения ищутся только в 1 сторону
            for j in range(i+1, len(self.nodes)):
            # for j in range(i, len(self.nodes)):
            # for j in range(len(self.nodes)): #БОЛЕЕ НАДЕЖНЫЙ ВАРИАНТ
                if not any([o.check_collision(self.nodes[j].get_pos(), self.nodes[i].get_pos()) for o in objs]):
                    self.nodes[i].edges.append(Edge(self.nodes[i], self.nodes[j]))
                    self.nodes[j].edges.append(Edge(self.nodes[j], self.nodes[i]))
    def draw(self, screen):
        for n in self.nodes: n.draw(screen)
    def find_route(self, n1, n2):
        for n in self.nodes: n.init_dijkstra()
        n1.route=[self.nodes[0]]
        n1.D=0
        wavefront=[n1]
        while len(wavefront):
            dd=[n.D for n in wavefront]
            v=wavefront[np.argmin(dd)]
            del wavefront[np.argmin(dd)]
            v.visited=True
            for e in v.edges:
                if not e.n2.visited:
                    if e.n2.D > v.D+e.w: #если вершина лучше соседа, то обновляем соседа по ней
                        e.n2.D=v.D+e.w
                        e.n2.route=[e.n2] if len(v.route)==0 else (v.route+[e.n2])
                    wavefront.append(e.n2) #берем соседа в фронт поиска
        res=list(reversed(n2.route))
        return res

if __name__ == "__main__":
    screen, timer, fps = pygame.display.set_mode(sz), pygame.time.Clock(), 20
    pygame.display.set_caption('Animation 2D')
    dt = 1 / fps

    ngons=[Ngon([[300,350],[400,450],[250,450]]),
           Ngon([[500,400],[650,400],[650,500],[500,500]])]

    for n in ngons: n.inflate(20)

    g=Graph([50,50], [750, 550], ngons)

    route=[]
    while True:
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT: sys.exit(0)
            if ev.type == pygame.KEYDOWN:
                if ev.key == pygame.K_1:
                    route=g.find_route(g.nodes[0], g.nodes[-1])

        screen.fill((255, 255, 255))
        for n in ngons: n.draw(screen)
        g.draw(screen)
        for i in range(1, len(route)):
            pygame.draw.line(screen, (100,100,255), route[i - 1].get_pos(), route[i].get_pos(), 4)

        draw_text(screen, f"Test = {1}", 5, 5)
        pygame.display.flip(), timer.tick(fps)
