import tileMain_v4 as tileMain
from PIL import Image

imagePath = 'galaxie.jpg'

#def cropImage():
#    area = image_object.crop(self.cropxy)
#    area.save(CROP_IMAGE, 'jpeg')
#    crop_image  = wx.Image(CROP_IMAGE, wx.BITMAP_TYPE_JPEG).ConvertToBitmap()
#    crop_bitmap = wx.StaticBitmap(self.crop_panel, bitmap=crop_image, name="Cropped Image")
#    crop_bitmap.CenterOnParent()
#    crop_bitmap.Refresh()

def defaultShow(imagePath=imagePath): 
    '''
    uses PIL (Python image library) to show the image
    ''' 
    img = Image.open(imagePath)
    img.show()
    
def wxShowStaticBitmap(imagePath=imagePath):
    '''
    uses wx to display the image
    '''
    import wx
    app = wx.App(False)
    title = 'Image Test StaticBitmap' 
    frame = wx.Frame(None,title=title)
    panel = wx.Panel(frame)
    img = wx.Image(imagePath, wx.BITMAP_TYPE_ANY)
    mainSizer = wx.BoxSizer(wx.VERTICAL)
    imageCtrl = wx.StaticBitmap(panel, wx.ID_ANY,
                                wx.BitmapFromImage(img))
    mainSizer.Add(imageCtrl, 0, wx.ALL, 5)
    panel.SetSizer(mainSizer)
    mainSizer.Fit(frame)
    panel.Layout
    frame.Show()
    app.MainLoop()
    
import wx

def pil_to_image(pil, alpha=True):
    """ Method will convert PIL Image to wx.Image """
    if alpha:
        image = apply( wx.EmptyImage, pil.size )
        image.SetData( pil.convert( "RGB").tostring() )
        image.SetAlphaData(pil.convert("RGBA").tostring()[3::4])
    else:
        image = wx.EmptyImage(pil.size[0], pil.size[1])
        new_image = pil.convert('RGB')
        data = new_image.tostring()
        image.SetData(data)
    return image


def image_to_pil(image):
    """ Method will convert wx.Image to PIL Image """
    pil = Image.new('RGB', (image.GetWidth(), image.GetHeight()))
    pil.fromstring(image.GetData())
    return pil
    
class dcExample(wx.Frame):
    def __init__(self, parent, title,imagePath):
        super(dcExample, self).__init__(parent, title=title, 
            size=(250, 150))
        self.img = wx.Image(imagePath, wx.BITMAP_TYPE_ANY)
        self.bmp = wx.BitmapFromImage(self.img)
        self.scale = 0
        self.SetDoubleBuffered(True)
        self.Bind(wx.EVT_PAINT, self.OnPaint)
        self.Bind(wx.EVT_MOUSE_EVENTS, self.Mousy)
        self.Centre()
        self.Show()

    def Mousy(self, event):
        if event.GetWheelRotation()!= 0:
            self.scale += event.GetWheelRotation()/120
            print "scale:",self.scale
        
        pil = image_to_pil(self.img)
        x = 300 + self.scale #* .01
        y = 300 + self.scale #* .01
        size = (x,y)
        print 'size',size
        pil.resize(size, Image.BILINEAR)
        img = pil_to_image(pil)
        self.bmp = wx.BitmapFromImage(img)
        
        self.Refresh()
            #self.Zoom(event.GetWheelRotation())

    def OnPaint(self, e):
        #dc = wx.BufferedPaintDC(self)#
        dc = wx.PaintDC(self)
        #dc = wx.B
        
        #dc.SetUserScale(x,y)
        dc.DrawBitmap(self.bmp,0,0)
        
        
    
def wxShowDC(imagePath=imagePath):
    
    app = wx.App(False)
    title = 'Image Test StaticBitmap' 
    #frame = dcExample(None,title=title)
    dcExample(None, title,imagePath)
    app.MainLoop()
    
def wxShowFC(imagePath=imagePath):
    app = wx.App(False)
    title = 'Image Test FloatCanvas' 
    frame = wx.Frame(None,title=title)
    canvas = tileMain.FCanvasModel(frame,dataPath = imagePath)
    #ScaledBitmap
    canvas.SetDisplay()
    frame.Show()
    app.MainLoop()
    
def pygletTest(imagePath=imagePath):
    '''
    test for pyglet module
    '''
    import pyglet

    window = pyglet.window.Window(resizable=True)
    gal = pyglet.image.load(imagePath)
    @window.event
    def on_draw():
        window.clear()
        gal.blit(0,0)
    
    pyglet.app.run()
    

    
class Camera(object):

    def __init__(self, win, x=0.0, y=0.0, rot=0.0, zoom=1.0):
        self.win = win
        self.x = x
        self.y = y
        self.rot = rot
        self.zoom = zoom

    def worldProjection(self):
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        widthRatio = self.win.width / self.win.height
        gluOrtho2D(
            -self.zoom * widthRatio,
            self.zoom * widthRatio,
            -self.zoom,
            self.zoom)

    def hudProjection(self):
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluOrtho2D(0, self.win.width, 0, self.win.height)
    
def pygletTest2(imagePath=imagePath):
    '''
    test for pyglet with 3D stuff
    '''
    
    #texture = gal.get_texture()
    #glBind
#    def MoveXY(self, x, y):
#        #wx.GetApp().Yield(True)
#        x = -self.parent.GetParent().dx
#        y = -self.parent.GetParent().dy
#        #self.display.MoveXY
#        self.display.MoveImage((x,y), 'Pixel', True)
#        print("Move X,Y: ",x,y)
#wxShowDC()

#wxShowFC()
pygletTest()
    
    
#def openGlut(imagePath=imagePath):
#    import glTest
#    glutInit()
#    test = AClass()
#    test.run()
    
#wxShowStaticBitmap()
