from select import select
import sys, pygame, numpy as np

pygame.font.init()
def draw_text(screen, s, x, y, sz=15, с=(0, 0, 0)):  # отрисовка текста
    screen.blit(pygame.font.SysFont('Comic Sans MS', sz).render(s, True, с), (x, y))

sz = (800, 600)

class Workzone:
    def __init__(self, x, y, cubes=["Blue", "Green", "Red"]):
        self.cubes=cubes
        self.x, self.y=x, y
    def draw(self, screen):
        for i in range(len(self.cubes)):
            name=self.cubes[i]
            c=(255, 0, 0) if name=="Red" else (0, 255, 0) if name=="Green" else (0, 0, 255)
            pygame.draw.rect(screen, c, [self.x+i*25, self.y, 20, 20], 0)
    def change(self, i1, i2): self.cubes[i1], self.cubes[i2]=self.cubes[i2], self.cubes[i1]
    def copy(self): return Workzone(self.x, self.y, [*self.cubes])
    def get_str(self): return ", ".join(self.cubes)

class Node:
    def __init__(self, workzone, level=0, label="", parent=None):
        self.workzone=workzone
        self.next_nodes=[]
        self.level=level
        self.label=label
        self.parent=parent
    def get_str(self):
        return f"{self.level}: {self.label}: {self.workzone.get_str()}"
    def get_childs_recursively(self):
        for n in self.next_nodes: 
            yield n #возврат текущего элемента с зацепкой для возврата в контекст исполнения данной функции
            for child in n.get_childs_recursively():
                yield child
    def get_local_ind(self):
        return self.parent.next_nodes.index(self) if self.parent else 0

class EventGraph:
    def __init__(self):
        self.root_node=None
    def get_all_nodes(self):
        return [self.root_node]+list(self.root_node.get_childs_recursively())
    def construct_recursively(self, node, num_levels):
        if num_levels<=0: return
        for i in range(len(node.workzone.cubes)-1):
            wz=node.workzone.copy()
            wz.change(i, i+1)
            n=Node(wz, node.level+1, f"change({i},{i+1})", node)
            node.next_nodes.append(n)
            self.construct_recursively(n, num_levels-1)
    def construct(self, cube_list):
        wz=Workzone(100,100, cube_list)
        self.root_node=Node(wz)
        self.construct_recursively(self.root_node, 4)
    def draw(self, screen):
        x0, y0 = self.root_node.workzone.x, self.root_node.workzone.y
        for n in self.get_all_nodes():
            y=(n.parent.workzone.y+50) if n.parent else 50
            dy=n.parent.get_local_ind()*25 if n.parent else 0
            num=len(n.parent.next_nodes) if n.parent else 0
            ind=n.get_local_ind()
            x=(n.parent.workzone.x+100*(ind-(num-1)/2)) if n.parent else 400
            n.workzone.x, n.workzone.y=x, y+dy
            n.workzone.draw(screen)
            (x_,y_)=(n.parent.workzone.x, n.parent.workzone.y) if n.parent else (x0,y0)
            pygame.draw.line(screen, (0,0,0), [x_,y_], (n.workzone.x, n.workzone.y), 2)

def main():
    screen = pygame.display.set_mode(sz)
    pygame.display.set_caption('Animation 2D')
    timer = pygame.time.Clock()
    fps = 20; dt=1/fps

    #wz=Workzone(100,100)
    #wz2=Workzone(100,250)
    #wz2.change(0,1)

    eg = EventGraph()
    eg.construct(["Blue", "Green", "Red"])

    test=eg.get_all_nodes()
    print([n.get_str() for n in test])
    
    while True:
        for ev in pygame.event.get():
            if ev.type==pygame.QUIT: sys.exit(0)
            if ev.type == pygame.KEYDOWN:
                if ev.key == pygame.K_r: print("Hi")                

        screen.fill((255, 255, 255))     
        draw_text(screen, f"Test = {1}", 5, 5)
        #wz.draw(screen)
        #wz2.draw(screen)

        eg.draw(screen)

        pygame.display.flip()
        timer.tick(fps)

main()
