import sys, pygame, numpy as np

#Clustering with sLOPE

pygame.font.init()
def draw_text(screen, s, x, y, sz=20, c=(0, 0, 0)):  # отрисовка текста
    screen.blit(pygame.font.SysFont('Comic Sans MS', sz).render(s, True, c), (x, y))

sz = (800, 600)

class Obj: #небольшой объект на экране
    def __init__(self, x, y, sz=50, texture_path=None): 
        self.x0, self.y0, self.x, self.y, self.sz = x, y, x, y, sz
        self.texture=None
        if texture_path is not None:
            self.texture=pygame.image.load(texture_path).convert_alpha()
    def reset_pos(self): self.x, self.y= self.x0, self.y0
    def get_pos(self): return [self.x, self.y]
    def get_bb(self): return [self.x-self.sz/2, self.y-self.sz/2, self.sz, self.sz]
    def set_pos(self, p): self.x, self.y=p
    def draw(self, screen): 
        if self.texture is not None:
            img=pygame.transform.scale(self.texture, (self.sz, self.sz))
            screen.blit(img, (self.x-self.sz/2, self.y-self.sz/2)) 
        else: pygame.draw.rect(screen, (0, 0, 0), self.get_bb(), 2, 2)
    def contains(self, pt):
        return (self.x-self.sz/2)<pt[0]<(self.x+self.sz/2) \
                and (self.y-self.sz/2)<pt[1]<(self.y+self.sz/2)

def get_transaction_vec(objs):
    res, bin=[], objs[-1]
    for i, o in enumerate(objs[:-1]):
        if bin.contains(o.get_pos()):
            res.append(i)
    return res

#https://loginom.ru/blog/clope
class Cluster:
    def __init__(self, transactions):
        self.transactions=transactions
        self.D, self.W, self.H, self.S, self.G, self.Occ, self.Ci=0,0,0,0,0,[], 0
    def calc(self):
        objs=[o for tr in self.transactions for o in tr]
        unique_objs=set(objs)
        self.D=len(unique_objs)
        self.Occ=np.bincount(objs)
        self.S=sum(self.Occ)
        self.W=len(unique_objs)
        self.H=self.S/self.W
        self.G=self.H/self.W
        self.Ci=len(self.transactions)
    def to_str(self):
        return f"D={self.D}, Occ={self.Occ}, S={self.S}, W={self.W}, H={self.H}"

def calc_profit(clusters):
    a=sum(c.G*c.Ci for c in clusters)
    b=sum(c.Ci for c in clusters)
    return a/b
    
def run_clope_iter(all_transactions, clusters=[]):
    if len(clusters)==0:
        clusters=[Cluster([tr]) for tr in all_transactions]
        for c in clusters: c.calc()
        return clusters

if __name__=="__main__":
    screen, timer, fps = pygame.display.set_mode(sz), pygame.time.Clock(), 20
    pygame.display.set_caption('Animation 2D')
    dt = 1 / fps

    obj1=Obj(100,100,50, "cola.png")
    obj2=Obj(100,200,50, "banana.png")
    obj3=Obj(100,300,50, "apple.jpg")
    obj4=Obj(100,400,50, "bread.jpg")
    bin=Obj(600,300,100)
    objs=[obj1, obj2, obj3, obj4, bin]

    dragged_obj=None

    mouse_pos=None

    all_transactions=[]

    clusters=[]
    
    while True:
        for ev in pygame.event.get():
            if ev.type==pygame.QUIT: sys.exit(0)
            if ev.type == pygame.KEYDOWN:
                if ev.key == pygame.K_1: 
                    all_transactions.append(get_transaction_vec(objs)) 
                    for obj in objs: obj.reset_pos()
                if ev.key == pygame.K_2: 
                    with open("transactions.txt", "w") as f:
                        f.write(str(all_transactions))
                if ev.key == pygame.K_3: 
                    with open("transactions.txt", "r") as f:
                        all_transactions=eval(f.read())
                if ev.key==pygame.K_4:
                    clusters=run_clope_iter(all_transactions, clusters)
                if ev.key==pygame.K_5:
                    for c in clusters:
                        print(c.to_str())
                    profit=calc_profit(clusters)
                    print(f"Profit = {profit:.2f}")

            if ev.type == pygame.MOUSEBUTTONDOWN:
                for obj in objs:
                    if obj.contains(ev.pos):
                        dragged_obj=obj
                        break
                mouse_pos=ev.pos
            if ev.type == pygame.MOUSEMOTION:
                mouse_pos=ev.pos
            if ev.type == pygame.MOUSEBUTTONUP:
                dragged_obj=None
                mouse_pos=None

        if dragged_obj is not None:
            dragged_obj.set_pos(mouse_pos)

        screen.fill((255, 255, 255)) 
        
        for obj in objs: obj.draw(screen)
        
        tv=get_transaction_vec(objs)
        draw_text(screen, f"Transaction = {tv}", 5, 5)

        for i, tr in enumerate(all_transactions):
            draw_text(screen, f"{tr}", 500, 5+20*i)
        pygame.display.flip(), timer.tick(fps)

        #template file by S. Diane, RTU MIREA, 2024-2026
