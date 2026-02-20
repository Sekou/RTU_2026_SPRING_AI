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

def infer_type(pt, centers):
    dd=[dist(c.get_pos(), pt.get_pos()) for c in centers]
    return centers[np.argmin(dd)].type

def find_nearest_centers(pts, centers):
    for p in pts: p.type=infer_type(p, centers)

def shift_centers(pts, centers):
    for c in centers:
        pp=[p.get_pos() for p in pts if p.type==c.type]
        c.x, c.y = np.mean(pp, axis=0)

def make_diagram(centers, step=10):
    for y in range(0, sz[1], step):
        for x in range(0, sz[0], step):
            pt=Pt(x, y)
            pt.type=infer_type(pt, centers)
            yield pt

if __name__=="__main__":
    screen, timer, fps = pygame.display.set_mode(sz), pygame.time.Clock(), 20
    pygame.display.set_caption('Animation 2D')
    dt = 1 / fps

    p_mouse=Pt(200,200,-1)

    pp=spawn_points(300,400, 30, -1, 50)
    pp2=spawn_points(500,350, 30, -1, 50)
    pp3=spawn_points(200,300, 30, -1, 50)
    pts=[*pp, *pp2, *pp3]

    centers=[Pt(250,250,0), Pt(350,280,1), Pt(450,220,2)]
    diagram_pts=[]
    
    while True:
        for ev in pygame.event.get():
            if ev.type==pygame.QUIT: sys.exit(0)
            if ev.type == pygame.KEYDOWN:
                if ev.key == pygame.K_1: find_nearest_centers(pts, centers)
                if ev.key == pygame.K_2: shift_centers(pts, centers)
                if ev.key == pygame.K_3: 
                    diagram_pts=list(make_diagram(centers, 10))
            if ev.type == pygame.MOUSEBUTTONDOWN:
                p_mouse=Pt(*ev.pos)
                p_mouse.type=infer_type(p_mouse, centers)

        screen.fill((255, 255, 255))    
        for p in pts: p.draw(screen)
        for p in centers: p.draw(screen, 10)
        for p in diagram_pts: p.draw(screen, 2)
        p_mouse.draw(screen, 4) 
        
        draw_text(screen, f"Test = {1}", 5, 5)
        pygame.display.flip(), timer.tick(fps)