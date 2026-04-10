import sys, pygame, numpy as np, math
import itertools

pygame.font.init()
def draw_text(screen, s, x, y, sz=15, c=(0, 0, 0)):  # отрисовка текста
    screen.blit(pygame.font.SysFont('Comic Sans MS', sz).render(s, True, c), (x, y))
def dist(p1, p2): return np.linalg.norm(np.subtract(p1, p2)) #расстояние между точками
def rot(v, ang): return np.dot([[-v[1], v[0]], v],[math.sin(ang), math.cos(ang)]) # поворот вектора на угол
def rot_arr(vv, ang): return [rot(v, ang) for v in vv] # функция для поворота массива на угол
def lim_ang(ang, arc=3.141592653589793): # ограничение угла в пределах +/-pi
    ang=ang%(2*arc)
    return ang + (2*arc if ang<-arc else -2*arc if ang>arc else 0)

def greedy_tsp(pts, ind): # жадное разомкнутое решение задачи коммивояжера (поиск в глубину)
    buf, res = [np.array(pts[i]) for i in range(len(pts)) if i!=ind], [np.array(pts[ind])]
    while len(buf): res+=[buf.pop(np.argmin([np.hypot(*(res[-1] - p)) for p in buf]))]
    return res

def full_searсh(pts, ind): # полный перебор возможных маршрутов
    min_len, min_path=np.inf, [] #NEW
    ii=[i for i in range(len(pts)) if i!=ind] 
    perms=itertools.permutations(ii)
    print(f"Num permutations: {math.factorial(len(ii))}")
    for step,perm in enumerate(perms):
        path=[pts[ind]] + [pts[i] for i in perm]
        L=calc_path_len(path)
        if L<min_len: min_len, min_path=L, path
        if step%1000==0: print(f"Step: {step + 1}")
    return min_path

def branch_and_bound_searсh(pts, ind): # применение метода ветвей и границ
    min_len, min_path=np.inf, greedy_tsp(pts, ind)
    L_upper=calc_path_len(min_path)

    ii=[i for i in range(len(pts)) if i!=ind]
    perms=itertools.permutations(ii)
    print(f"Num permutations: {math.factorial(len(ii))}")

    # проверка удовлетворительности решения (непревышения жадного пути или ранее найденного минимального пути)
    def check_upper_bound(perm, L_upper, pts): 
        s=dist(pts[ind], pts[perm[0]]) #NEW2
        for i in range(len(perm)-1):
            s+=dist(pts[perm[i]], pts[perm[i+1]]) #NEW2
            visited_pts=[pts[i] for i in perm[:i+1]] #NEW2
            L_lower=s + estimate_lower_bound(visited_pts, pts) #NEW perm[i+1:] вместо perm[:i+1]
            #print(L_lower, L_upper)
            #if L_lower>=L_upper: return False, perm[:i+2]
            if L_lower>L_upper: return False, perm[:i+1] #NEW2
        return True, None

    def estimate_lower_bound(visited_pts, pts): # уточняем нижнюю оценку оставшегося маршрута
        p_left=[p for p in pts if not p in visited_pts]
        buf=[visited_pts[-1], *p_left] # в буфере первых точек: последняя из пройденного маршрута и все непройденные
        res=0
        while len(buf):
            dd=[dist(buf[0], p) for p in p_left]
            dd[np.argmin(dd)]=np.inf # маскируем нулевое расстояние
            ind=np.argmin(dd)
            res+=dd[ind]
            buf.pop(0)
        return res

    bad_trunks=[] #плохие крупные ветви, на которых "отсекаем" мелкие

    def check_deletion(perm, bad_trunks): #проверка, не является ли ветвь удаленной
        for bt in bad_trunks:
            res=True
            for i in range(len(bt)): 
                if bt[i]!=perm[i]: res=False
            if res: return True
        return False

    #[132, 4561, 23, ...]
    for step,perm in enumerate(perms): #[2345]
        print(f"Step: {step + 1}")
        ok1 = not check_deletion(perm, bad_trunks)
        if not ok1:  #ветвь уже запрещена - уходим на след. итерацию
            print("skipping deleted branch")

            path=[pts[ind]] + [pts[i] for i in perm]
            L=calc_path_len(path)
            if L<763:
                print(ind, "+", perm) #4 + (0, 9, 1, 6, 8, 2, 7, 3, 5)
                print(path) #[(150, 150), (100, 100), (100, 200), (150, 200), (150, 300), (250, 300), (250, 200), (200, 150), (250, 100), (350, 100)]
                print(L) #762.1320343559643
                print(bad_trunks) #[(0,)]
                ok2, trunk = check_upper_bound(perm, L_upper, pts)
                print(ok2)
                #TODO: проверить check_upper_bound(perm, L_upper, pts) для вышеуказанных параметров
                #странно, что нижняя оценка для пути больше чем его реальная длина 2026-04-10

            assert L>763, "DELETED GOOD SOLUTION"

            continue
        ok2, trunk = check_upper_bound(perm, L_upper, pts) #NEW
        if not ok2:  #ветвь не запрещена, но верхняя граница не соблюдается - добавляем запрет и уходим на след. итерацию
            bad_trunks.append(trunk)
            #TODO: ДОБАВИТЬ УДАЛЕНИЕ БОЛЕЕ ЧАСТНЫХ ВЕТВЕЙ - например (0, 8, 2) после добавления (0, 8)
            print("added deleted branch")
            continue
        path=[pts[ind]] + [pts[i] for i in perm]
        L=calc_path_len(path)
        if L<min_len: 
            min_len, min_path, L_upper=L, path, L
            print("found better path")
    return min_path
    
sz = (800, 600)

def calc_path_len(path):
    res=0
    for i in range(len(path)-1): res+=dist(path[i], path[i+1])
    return res

if __name__=="__main__":
    screen, timer, fps =  pygame.display.set_mode(sz), pygame.time.Clock(), 20
    pygame.display.set_caption('Animation 2D')
    dt = 1 / fps

    pts=[(100, 100) , (150, 200) , (250, 200) ,
    (250, 100) , (150, 150) , (350, 100) , (150, 300) , 
    (200, 150) , (250, 300) , (100, 200)]

    START_IND = 4
    path=greedy_tsp(pts, START_IND)

    while True:
        for ev in pygame.event.get():
            if ev.type==pygame.QUIT: sys.exit(0)
            if ev.type == pygame.KEYDOWN:
                if ev.key == pygame.K_1:
                    path=full_searсh(pts, START_IND)
                    L=calc_path_len(path)
                if ev.key == pygame.K_2:
                    path=branch_and_bound_searсh(pts, START_IND)
                    L=calc_path_len(path)

        screen.fill((255, 255, 255))   
        for p in pts:
            pygame.draw.circle(screen, (0,0,0), p, 3, 0)  

        for i in range(len(path)-1):
            pygame.draw.line(screen, (255,0,0), path[i], path[i+1], 2)

        L=calc_path_len(path)
        draw_text(screen, f"L = {L}", 5, 5)
        pygame.display.flip(), timer.tick(fps)

#template file by S. Diane, RTU MIREA, 2024-2026
