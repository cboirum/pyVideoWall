#import pyglet
#
#window = pyglet.window.Window()
#image = pyglet.image.Texture.create(256,128)
#img1 = pyglet.image.load('galaxie.jpg')#('img1.png')
#img2 = pyglet.image.load('galaxie.jpg')#('img2.png')
#image.blit_into(img1,0,0,0)
#image.blit_into(img2,128,0,0)
#@window.event
#def on_draw():
#    window.clear()
#    image.blit(0,0)
#
#pyglet.app.run()

from pyglet.gl import *
from pyglet import image

# Direct OpenGL commands to this window.
window = pyglet.window.Window()
#glEnable(GL_TEXTURE_2D)
pic = image.load('galaxie.jpg')

#data = pyglet.image.load('galaxie.jpg').get_data()
pic.blit(0,0,0)
texture = pic.get_texture()
#texture_id = glGenTextures(1)

@window.event
def on_draw():
    glClear(GL_COLOR_BUFFER_BIT)
    glLoadIdentity()
    glBegin(GL_TRIANGLES)
    glVertex2f(0, 0)
    glVertex2f(window.width, 0)
    glVertex2f(window.width, window.height)
    glEnd()

pyglet.app.run()