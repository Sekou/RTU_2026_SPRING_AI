import re
import sys, pygame, numpy as np

pygame.font.init()
def draw_text(screen, s, x, y, sz=15, c=(0, 0, 0)):  # отрисовка текста
    screen.blit(pygame.font.SysFont('Comic Sans MS', sz).render(s, True, c), (x, y))

def dist(p1, p2): return np.linalg.norm(np.subtract(p1, p2))

sz = (800, 600)
class Pt:
    def __init__(self, x, y, type=-1):
        self.x, self.y, self.type= x, y, type
    def get_pos(self): return [self.x, self.y]
    def draw(self, screen, sz=6):
        colors = [[255,0,0],[0,255,0],[0,0,255],[200,200,0],[200,0,200],[0,200,200], [0,0,0]]
        pygame.draw.rect(screen, colors[self.type], [self.x-sz/2, self.y-sz/2, sz, sz], 0)

def spawn_points(x, y, r, type, num):
    return [Pt(np.random.normal(x, r), np.random.normal(y, r), type) for i in range(num)]

def get_k_neighbours(pt, pts, k):
    ddpp=[[dist(p.get_pos(), pt.get_pos()), p] for p in pts] #пары (удаленность-точка)
    ddpp = sorted(ddpp, key=lambda dp: dp[0]) #сортировка по удаленности
    return [p for d, p in ddpp[:k]]

def infer_type(neighbours):
    return np.argmax(np.bincount([n.type for n in neighbours if n.type!=-1]))

def make_diagram(pts, step=10, k=5):
    for y in range(0, sz[1], step):
        for x in range(0, sz[0], step):
            pt=Pt(x, y)
            neighbours=get_k_neighbours(pt, pts, k)
            pt.type=infer_type(neighbours)
            yield pt

if __name__=="__main__":
    screen, timer, fps = pygame.display.set_mode(sz), pygame.time.Clock(), 20
    pygame.display.set_caption('Animation 2D')
    dt = 1 / fps

    p_mouse=Pt(200,200,1)
    neighbours=[]
    diagram_pts=[]

    pp=spawn_points(300,400, 30, 1, 50)
    pp2=spawn_points(500,350, 30, 2, 50)
    pp3=spawn_points(200,300, 30, 3, 50)
    pts=[*pp, *pp2, *pp3]
    
    while True:
        for ev in pygame.event.get():
            if ev.type==pygame.QUIT: sys.exit(0)
            if ev.type == pygame.KEYDOWN:
                if ev.key == pygame.K_1: 
                    diagram_pts=list(make_diagram(pts, 10, 3))
                if ev.key == pygame.K_2: 
                    diagram_pts=list(make_diagram(pts, 10, 5))
            if ev.type == pygame.MOUSEBUTTONDOWN:
                p_mouse=Pt(*ev.pos)
                neighbours = get_k_neighbours(p_mouse, pts, 5)
                p_mouse.type=infer_type(neighbours)
                if ev.button==3: pts.append(p_mouse)

        screen.fill((255, 255, 255))    
        for p in pts: p.draw(screen)
        for p in neighbours: pygame.draw.line(screen, (200,200,200), p.get_pos(), p_mouse.get_pos(), 1) 
        for p in diagram_pts: p.draw(screen, 2)

        p_mouse.draw(screen)
        
        draw_text(screen, f"Test = {1}", 5, 5)
        pygame.display.flip(), timer.tick(fps)