#2026, S. Diane
#pip install pygame PyOpenGL

import pygame, numpy as np, math
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *

def draw_point(p, color=(1,1,1)):
    glColor3f(*color), glPointSize(5.0), glBegin(GL_POINTS), glVertex3f(*p), glEnd()

def draw_segment(p0, p1, color=(1,1,1)):
    glColor3f(*color), glBegin(GL_LINES), glVertex3fv(p0), glVertex3fv(p1), glEnd()

def get_pt(mat): return np.transpose(mat[:3,3])
def calc_link(M_prev, a, b, alpha, theta, coordinate=0):
    s, c, al, th = math.sin, math.cos, alpha, theta+coordinate
    st,ct,sa,ca=s(th), c(th), s(al), c(al)
    mat=np.array([[ct, -st*ca, st*sa, a*ct],
    [st, ct*ca, -ct*sa, a*st],
    [0,sa,ca,b],[0,0,0,1]])
    M_new=M_prev@mat #ВАЖНО! Матрицы перемножать именно в таком порядке
    return M_new

def draw_axes():
    glBegin(GL_LINES) # Specify we are drawing lines
    for v in [(1,0,0),(0,1,0),(0,0,1)]: 
        glColor3f(*v), glVertex3fv((0,0,0)), glVertex3fv(v)
    glEnd()

def get_mats_from_DH(DH, qq):
    mm=[]
    for i in range (len(DH)):
        m=calc_link(mm[i-1] if i>0 else np.eye(4), *DH[i], qq[i])
        mm.append(m)
    return mm

def search_IK(DH, qq, ind_q, step, p_goal): #решение ОЗК методом покоординатного спуска
    d_min, q_best=np.inf, qq[ind_q] #начальная гипотеза
    for q in np.arange(-math.pi, math.pi, step): #WARNING: указать правильные диапазоны
        qq[ind_q]=q
        mm=get_mats_from_DH(DH, qq)
        D=np.linalg.norm(np.subtract(p_goal, get_pt(mm[-1])))
        if D<d_min: d_min, q_best=D, q
        #TODO: оптимизировать перебор - как только начинает расти ошибка, останавливаться и искать в другую сторону
    return q_best

def main():
    pygame.init()
    display = (800, 600)
    pygame.display.set_mode(display, DOUBLEBUF|OPENGL)
    gluPerspective(45, (display[0]/display[1]), 0.1, 50.0)
      
    zIsUp=np.array([ #разворачиваем систему координат чтоб было похоже на X0Y0Z0
     -1.0,0.0,0.0,0.0,0.0,0.0,1.0,0.0,0.0,1.0,0.0,0.0,0.0,0.0,0.0,1.0])
    glMultMatrixf(zIsUp)

    glTranslatef(0, -5.0, -1) # Move the camera back

    fps=10
    dt, time=1/fps, 0

    a90=math.pi/2
    DH=[[0,0,-a90,a90],[0.432,0.149,0,0],[0.02,0,a90,a90],
    [0,0.432,-a90,0],[0,0,a90,0],[0,0.056,0,0]]  #почему th[0] +90, th[2] +90 ?
    qq=[0 for i in range(len(DH))]

    traj=[]
    traj2=[]
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(), quit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    for i in range(len(DH)):
                        qq[i]=search_IK(DH, qq, i, 0.1, p_goal)
        
        #p_goal=(0.5,0.5,0.5)
        p_goal=(0.5+math.sin(time/10)/2,0.5+math.sin(time/10+1)/2,0.5+math.sin(time/10+2)/2)

        for i in range(len(DH)):
            qq[i]=search_IK(DH, qq, i, 0.1, p_goal)

        #qq=[math.sin(time/10 + i) for i in range(6)]
      
        glRotatef(0.5, 0, 0, 1) # Rotate the cube
        glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)
        draw_axes()
        #draw_segment([0.5,0.5,0.5],[0.7,0.7,0.9])

        draw_point(p_goal, (1,0,1))

        p0=[0,0,0]
        draw_point(p0)

        mm=get_mats_from_DH(DH, qq)
        for i in range(len(mm)):
            draw_point(get_pt(mm[i]))
            if i>0: draw_segment(get_pt(mm[i]), get_pt(mm[i-1]))

        draw_segment(p_goal, get_pt(mm[-1]), (1,0,1))
        D=np.linalg.norm(np.subtract(p_goal, get_pt(mm[-1])))
        #print(D)

        traj.append( get_pt(mm[-1]) )
        traj2.append( [*p_goal] )

        for i in range(1, len(traj)): draw_segment(traj[i-1], traj[i], (1,1,0))
        for i in range(1, len(traj2)): draw_segment(traj2[i-1], traj2[i], (0,1,1))

        pygame.display.flip()
        pygame.time.wait(fps)
        time+=dt

main()
