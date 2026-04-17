#pip install pygame PyOpenGL

import pygame, numpy as np, math
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *

def draw_point(p):
    glColor3f(1,1,1), glPointSize(5.0), glBegin(GL_POINTS), glVertex3f(*p), glEnd()

def draw_segment(p0, p1):
    glColor3f(1,1,1), glBegin(GL_LINES), glVertex3fv(p0), glVertex3fv(p1), glEnd()

def draw_link(p0, a, b, alpha, theta, coordinate=0):
    s, c, al, th = math.sin, math.cos, alpha, theta+coordinate
    st,ct,sa,ca=s(th), c(th), s(al), c(al)
    mat=np.array([[ct, -st*ca, st*sa, a*ct],
    [st, ct*ca, -ct*sa, a*st],
    [0,sa,ca,b],[0,0,0,1]])
    p1=(mat@[*p0,1])[:3]
    draw_segment(p0, p1)
    return p1

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
    
    xIsUp=np.array([ #разворачиваем систему координат чтоб было похоже на X0Y0Z0
     0.0,  1.0,  0.0,  0.0, 
    -1.0,  0.0,  0.0,  0.0, 
     0.0,  0.0,  1.0,  0.0, 
     0.0,  0.0,  0.0,  1.0 ])

    glMultMatrixf(xIsUp)

    glTranslatef(-1.0, 0.0, -5) # Move the camera back

    fps=10
    dt, time=1/fps, 0

    q1,q2=0,0
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
        
        q1,q2=math.sin(time/10),math.cos(time/10)
        glRotatef(0.1, 1, 0, 0) # Rotate the cube
        glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)
        draw_axes()
        #draw_segment([0.5,0.5,0.5],[0.7,0.7,0.9])
        l1,l2=0.8, 0.5
        p0=[0,0,0]
        draw_point(p0)
        p1=draw_link(p0, l1,0,0,0, q1)
        draw_point(p1)
        p2=draw_link(p1, l2,0,0,0, q2)
        draw_point(p2)
        pygame.display.flip()
        pygame.time.wait(fps)
        time+=dt

main()