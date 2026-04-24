import sys, pygame, numpy as np

#Implementing recomender system
#смысл рекомендации - по пересекающимся товарм подтянуть дополнительные товары 

pygame.font.init()
def draw_text(screen, s, x, y, sz=20, c=(0, 0, 0)):  # отрисовка текста
    screen.blit(pygame.font.SysFont('Comic Sans MS', sz).render(s, True, c), (x, y))

sz = (800, 600)

class Obj: #небольшой объект на экране
    def __init__(self, x, y, sz=50, texture_path=None): 
        self.x0, self.y0, self.x, self.y, self.sz = x, y, x, y, sz
        self.features=[]
        self.texture=None
        if texture_path is not None:
            self.texture=pygame.image.load(texture_path).convert_alpha()
            # Iterate through every pixel
            for x in range(self.texture.get_width()):
                for y in range(self.texture.get_height()):
                    # Check if the pixel is white
                    if np.mean(self.texture.get_at((x, y))[:3])>240:
                        # Set pixel to transparent (RGBA: 255, 255, 255, 0)
                        self.texture.set_at((x, y), (255, 255, 255, 0))

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

class Person(Obj):
    def __init__(self, x, y, sz=50, texture_path=None): 
        super().__init__(x, y, sz, texture_path)
        self.selected=False
        self.transactions=[]
    def draw(self, screen): 
        super().draw(screen)
        if self.selected: 
            pygame.draw.circle(screen, (255, 0, 0), self.get_pos(), self.sz/2, 2)

def get_transaction_vec(objs):
    res, bin=[], objs[-1]
    for i, o in enumerate(objs[:-1]):
        if bin.contains(o.get_pos()):
            res.append(i)
    return res

if __name__=="__main__":
    screen, timer, fps = pygame.display.set_mode(sz), pygame.time.Clock(), 20
    pygame.display.set_caption('Animation 2D')
    dt = 1 / fps

    people=[Person(300+80*i,100, 60, f"people/{i+1}.jpeg") for i in range(3)]
    objs=[Obj(100,100+60*i,50, f"img/{i+1}.jpeg") for i in range(8)]
    xy=[o.get_pos() for o in objs]

    bin=Obj(600,300,100)
    objs_=[*objs, bin]

    dragged_obj=None

    mouse_pos=None

    all_transactions=[]

    def get_current_person_id():
        for i,p in enumerate(people):
            if p.selected: return i
        return -1

    def make_common_matrix(people):
        res=[]
        for p in people:
            history=[]
            for tr in p.transactions: history.extend(tr)
            row=np.bincount(history)
            res.append(row)
        print(res)
        return res

    while True:
        for ev in pygame.event.get():
            if ev.type==pygame.QUIT: sys.exit(0)
            if ev.type == pygame.KEYDOWN:
                if ev.key == pygame.K_1: 
                    id=get_current_person_id()
                    if id>=0:
                        person=people[id]
                        person.transactions.append(get_transaction_vec(objs_)) 
                        for obj in objs: obj.reset_pos()
                if ev.key == pygame.K_2: 
                    with open("transactions.txt", "w") as f:
                        f.write(str([p.transactions for p in people]))
                if ev.key == pygame.K_3: 
                    with open("transactions.txt", "r") as f:
                        all_transactions=eval(f.read(str([p.transactions for p in people])))
                        for tr,p in zip(all_transactions, people):
                            people.transactions=tr
                if ev.key == pygame.K_4: 
                    with open("transactions.txt", "r") as f:
                        all_transactions=eval(f.read(str([p.transactions for p in people])))
                        for tr,p in zip(all_transactions, people):
                            people.transactions=tr
                if ev.key == pygame.K_5:
                    make_common_matrix()        

            if ev.type == pygame.MOUSEBUTTONDOWN:
                for obj in objs:
                    if obj.contains(ev.pos):
                        dragged_obj=obj
                        break
                for p in people:
                    if p.contains(ev.pos):
                        for p2 in people: p2.selected=False
                        p.selected=True
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
        
        for obj in objs_: obj.draw(screen)
        for human in people: human.draw(screen)
        
        tv=get_transaction_vec(objs_)
        draw_text(screen, f"Transaction = {tv}", 5, 5)

        for i, (x,y) in enumerate(xy):
            draw_text(screen, f"{i}", x-35, y-15)

        for j, p in enumerate(people):
            for i, tr in enumerate(p.transactions):
                draw_text(screen, f"{tr}", 280+j*80, 150+20*i)

        pygame.display.flip(), timer.tick(fps)

        #template file by S. Diane, RTU MIREA, 2024-2026
