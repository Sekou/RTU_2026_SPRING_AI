#pip install pygame PyOpenGL

import pygame, numpy as np, math
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *

# Define 8 vertices of a cube
vertices = ( (0, 0, 0), (1, 0, 0), (0, 0, 0),(0, 1, 0), (0, 0, 0),(0, 0, 1) )

def draw_segment(p0, p1):
    glColor3f(1,1,1), glBegin(GL_LINES), glVertex3fv(p0), glVertex3fv(p1), glEnd()

def draw_axes():
    ind_color=-1
    colors=[(1,0,0),(0,1,0),(0,0,1)]
    glBegin(GL_LINES) # Specify we are drawing lines
    for i,v in enumerate(vertices): 
        if i%2==0: 
            ind_color+=1
            glColor3f(*colors[ind_color])
        glVertex3fv(v)
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


    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
        
        glRotatef(1, 1, 0, 0) # Rotate the cube
        glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)
        draw_axes()
        draw_segment([0.5,0.5,0.5],[0.7,0.7,0.9])
        pygame.display.flip()
        pygame.time.wait(10)

main()