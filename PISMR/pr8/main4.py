#pip install pygame PyOpenGL

import pygame, numpy as np, math
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *

def draw_point(p):
    glColor3f(1,1,1), glPointSize(5.0), glBegin(GL_POINTS), glVertex3f(*p), glEnd()

def draw_segment(p0, p1):
    glColor3f(1,1,1), glBegin(GL_LINES), glVertex3fv(p0), glVertex3fv(p1), glEnd()

def get_pt(mat): return np.transpose(mat[:3,3])
def draw_link(M_prev, a, b, alpha, theta, coordinate=0):
    s, c, al, th = math.sin, math.cos, alpha, theta+coordinate
    st,ct,sa,ca=s(th), c(th), s(al), c(al)
    mat=np.array([[ct, -st*ca, st*sa, a*ct],
    [st, ct*ca, -ct*sa, a*st],
    [0,sa,ca,b],[0,0,0,1]])
    M_new=M_prev@mat #ВАЖНО! Матрицы перемножать именно в таком порядке
    p0,p1=get_pt(M_prev), get_pt(M_new)
    d=np.linalg.norm(np.subtract(p1, p0))
    #assert abs(d-a)<0.001, f"Error - wrong link length: {d} / {a}"
    draw_segment(p0,p1)
    return M_new

def draw_axes():
    glBegin(GL_LINES) # Specify we are drawing lines
    for v in [(1,0,0),(0,1,0),(0,0,1)]: 
        glColor3f(*v), glVertex3fv((0,0,0)), glVertex3fv(v)
    glEnd()

def main():
    pygame.init()
    display = (800, 600)
    pygame.display.set_mode(display, DOUBLEBUF|OPENGL)
    gluPerspective(45, (display[0]/display[1]), 0.1, 50.0)
    
    #xIsUp=np.array([ #разворачиваем систему координат чтоб было похоже на X0Y0Z0
    # 0.0,  1.0,  0.0,  0.0, 
    #-1.0,  0.0,  0.0,  0.0, 
    # 0.0,  0.0,  1.0,  0.0, 
    # 0.0,  0.0,  0.0,  1.0 ])
      
    zIsUp=np.array([ #разворачиваем систему координат чтоб было похоже на X0Y0Z0
     -1.0,  0.0,  0.0,  0.0, 
     0.0,  0.0,  1.0,  0.0, 
     0.0,  1.0,  0.0,  0.0, 
     0.0,  0.0,  0.0,  1.0 ])

    #glMultMatrixf(xIsUp)
    glMultMatrixf(zIsUp)

    glTranslatef(0, -5.0, -1) # Move the camera back

    fps=10
    dt, time=1/fps, 0

    q1,q2=0,0
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
        
        #qq=[math.sin(time/10 + i) for i in range(6)]
        qq=[0]*6
        qq[1]=1#math.sin(time/10)
        glRotatef(0.1, 0, 0, 1) # Rotate the cube
        glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)
        draw_axes()
        #draw_segment([0.5,0.5,0.5],[0.7,0.7,0.9])

        p0=[0,0,0]
        a90=math.pi/2
        draw_point(p0)
        M1=draw_link(np.eye(4), 0,0,-a90,0, qq[0]);draw_point(get_pt(M1))
        M2=draw_link(M1, 0.432,0.149,0,0, qq[1]); draw_point(get_pt(M2))
        M3=draw_link(M2, 0.02,0,a90,0, qq[2]); draw_point(get_pt(M3))
        M4=draw_link(M3, 0,0.432,-a90,0, qq[3]); draw_point(get_pt(M4))
        M5=draw_link(M4, 0,0,a90,0, qq[4]); draw_point(get_pt(M5))
        M6=draw_link(M5, 0,.056,0,0, qq[5]); draw_point(get_pt(M6))
        pygame.display.flip()
        pygame.time.wait(fps)
        time+=dt

main()