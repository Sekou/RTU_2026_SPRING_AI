# TODO: можно ли отойти от логики Цетлина и генерировать связи автоматически как у муравья Лэнгтона?
# TODO: реализовать нейросетевое обучение по аналогии с автоматным и сравнить
from select import select
import sys, pygame, numpy as np, math

# https://stratum.ac.ru/education/textbooks/modelir/lection42.html

pygame.font.init()


def draw_text(screen, s, x, y, sz=20, color=(0, 0, 0)):  # отрисовка текста
    screen.blit(pygame.font.SysFont('Comic Sans MS', sz).render(s, True, (0, 0, 0)), (x, y))

def lim_ang(ang, arc=3.141592653589793):  # ограничение угла в пределах +/-pi
    ang = ang % (2 * arc);
    return ang + (2 * arc if ang < -arc else -2 * arc if ang > arc else 0)

def dist(p1, p2): return np.linalg.norm(np.subtract(p2, p1))  # расстояние между точками

# отрисовка стрелки по 2 точкам
def draw_arrow2(screen, color, p0, p1, w):
    angle=math.atan2(p1[1]-p0[1],p1[0]-p0[0])
    p2 = [p1[0] - 10 * math.cos(angle + 0.5), p1[1] - 10 * math.sin(angle + 0.5)]
    p3 = [p1[0] - 10 * math.cos(angle - 0.5), p1[1] - 10 * math.sin(angle - 0.5)]
    for a,b in [[p0, p1], [p1, p2], [p1, p3]]: pygame.draw.line(screen, color, a, b, w)

class Robot:
    def __init__(self, x, y):
        self.radius, self.color = 20, (0, 0, 0)
        self.x, self.y, self.a, self.vlin, self.vrot = x, y, 0, 0, 0
        self.vlin_, self.vrot_ = 0, 0
        self.history = []  # история наград

    def get_pos(self): return [self.x, self.y]

    def draw(self, screen):
        p1 = np.array(self.get_pos())
        pygame.draw.circle(screen, self.color, p1, self.radius, 2)
        s, c = math.sin(self.a), math.cos(self.a)
        pygame.draw.line(screen, self.color, p1, p1 + [self.radius * c, self.radius * s], 2)

    def contains(self, obj): return dist(self.get_pos(), obj.get_pos()) < self.radius

    def calc_reward(self):
        return max(abs(self.vlin_) / 50, abs(self.vrot_) / 1)  # редуцированная нечеткая логка

    def get_avg_reward(self, num_records):
        return np.mean(self.history[-min(num_records, len(self.history)):])

    def sim(self, dt, objs):
        oo = [o for o in objs if self.contains(o)]
        self.vlin_, self.vrot_ = self.vlin / (1 + len(oo)), self.vrot / (1 + len(oo))
        s, c = math.sin(self.a), math.cos(self.a)
        self.x, self.y = self.x + c * self.vlin_ * dt, self.y + s * self.vlin_ * dt
        self.a = lim_ang(self.a + self.vrot_ * dt)
        self.history.append(self.calc_reward())

    def get_signal(self, delay=20): #сигнал обучения для автомата
        i1, i2=max(0, len(self.history)-delay), len(self.history)-1
        return np.sign(self.history[i2]-self.history[i1])

def draw_plot(screen, arr, y0, k=50, w=800):  # [*arr,*arr], [0]*2
    arr = arr if 2 < len(arr) < w else [0, 0] if len(arr) < 2 else arr[-min(w, len(arr)):]
    for i, (v1, v2) in enumerate(zip(arr[:-1], arr[1:])):
        pygame.draw.line(screen, (0, 0, 255), [i, y0 - v1 * k], [i + 1, y0 - v2 * k], 1)


class Obj:  # небольшой объект на экране
    def __init__(self, x, y): self.x, self.y, self.sz = x, y, 20
    def get_pos(self): return [self.x, self.y]
    def get_bb(self): return [self.x - self.sz / 2, self.y - self.sz / 2, self.sz, self.sz]
    def set_pos(self, p): self.x, self.y = p
    def draw(self, screen): pygame.draw.rect(screen, (255, 190, 0), self.get_bb())

class State:  # состояние конечного автомата
    def __init__(self, name, x, y):
        self.sz, self.x, self.y = 45, x, y
        self.name = name
        self.next_a = []  # соседние состояния на случай положит. подкрепл.
        self.next_b = []  # соседние состояния на случай отрицат. подкрепл.
    def get_pos(self): return [self.x, self.y]
    def sim(self, reward): pass
    def draw(self, screen):
        pygame.draw.circle(screen, (255, 0, 255), self.get_pos(), self.sz / 2, 2)
        draw_text(screen, self.name, self.x - 10, self.y - 10)
        for s in self.next_a: draw_arrow2(screen, (0,255,0), self.get_pos(), s.get_pos(), 2)
        for s in self.next_b: draw_arrow2(screen, (255,0,0), self.get_pos(), s.get_pos(), 2)

class FSM:  # Finite State Machine - конечный автомат
    def __init__(self):
        self.states = []
        self.active_state = None
        self.construct()
    def connect_branch(self, states):
        for s1, s2 in zip(states[:-1], states[1:]):
            s1.next_a.append(s2), s2.next_b.append(s1)
        states[-1].next_a.append(states[-1])
    def construct(self):
        states1=[State("S10", 400, 270), State("S11", 400, 220), State("S12", 400, 170)] #вперед
        states2 = [State("S20", 370, 330), State("S21", 330, 370), State("S22", 290, 410)] #по часовой
        states3 = [State("S30", 430, 330), State("S31", 470, 370), State("S32", 510, 410)] #против часовой
        self.states=[states1, states2, states3]
        for branch in self.states: self.connect_branch(branch)
        states1[0].next_b.append(states2[0]), states2[0].next_b.append(states3[0]), states3[0].next_b.append(states1[0])
        self.active_state=states1[0]
    def sim(self, signal):
        if signal>0: self.active_state=self.active_state.next_a[0]
        if signal<0: self.active_state=self.active_state.next_b[0]
    def draw(self, screen):
        for branch in self.states:
            for s in branch: s.draw(screen)
        pygame.draw.circle(screen, (0,255,255), self.active_state.get_pos(), self.active_state.sz/2, 4)

if __name__ == "__main__":
    sz, timer, fps = (800, 600), pygame.time.Clock(), 20
    screen, dt, time = pygame.display.set_mode(sz), 1 / fps, 0
    robot = Robot(200, 200)

    k_time=5 #ускорение симуляции

    t_last_learn=time

    #s = State("S10", 500, 500)
    fsm=FSM()

    np.random.seed(1)
    objs = [Obj(i, i) for i in range(50, 600, 50)] + \
           [Obj(600 - i, i) for i in range(50, 600, 50)] + \
           [Obj(600, 400), Obj(650, 400), Obj(700, 400)] + \
           [Obj(650, 200), Obj(700, 200), Obj(750, 200)] + \
           [Obj(np.random.randint(50, 750), np.random.randint(50, 550)) for i in range(30)]

    while True:
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT: sys.exit(0)
            if ev.type == pygame.KEYDOWN:
                robot.vlin = 50 if ev.key == pygame.K_w else -50 if ev.key == pygame.K_s else robot.vlin
                robot.vrot = -1 if ev.key == pygame.K_a else 1 if ev.key == pygame.K_d else robot.vrot

        for itime in range(k_time):
            if fsm.active_state in fsm.states[0]: robot.vlin, robot.vrot = 50, 0 # вперед
            if fsm.active_state in fsm.states[1]: robot.vlin, robot.vrot = 50, 1 # по часовой
            if fsm.active_state in fsm.states[2]: robot.vlin, robot.vrot = 50, -1 # против часовой

            robot.x=0 if robot.x>sz[0] else sz[0] if robot.x<0 else robot.x
            robot.y=0 if robot.y>sz[1] else sz[1] if robot.y<0 else robot.y

            robot.sim(dt, objs)

            if time-t_last_learn>0.5:
                fsm.sim(robot.get_signal())
                t_last_learn=time

            time += dt

        screen.fill((255, 255, 255))
        robot.draw(screen)
        draw_plot(screen, robot.history, 599, 50)
        for o in objs: o.draw(screen)

        #s.draw(screen)
        fsm.draw(screen)

        draw_text(screen, f"AvgRew({sz[0]}) = {robot.get_avg_reward(sz[0]):.2f}", 5, 5)
        draw_text(screen, f"LearnSign = {robot.get_signal()}", 5, 25)
        pygame.display.flip(), timer.tick(fps)


# template file by S. Diane, RTU MIREA, 2024-2026
