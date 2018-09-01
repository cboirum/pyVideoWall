'''
Tile Display Test by Curtis Boirum
7/2/13

Goal of the test is to create a serverless mesh network
of independent application windows that synchronize 
their view of a model with eachother.

The first model will be nothing the goal is to eventually
render a complex 3D scene from multiple persepectives
and/or a single tiled perspective. The single tiled 
perspective is the ultimate goal. The model data would
ideally be loaded on a usage requirement basis per window
tile.

Tasks:

Create window
    live display of
        mouse position
        window position and boundaries
        
    network stream broadcast
        mouse position
        window position
        
    network stream receive
        mouse pos.
        window pos.
        
Detect other windows that are open and number
windows sequentially

Create window manager that can spawn process windows
with a target model, and target window location/boundaries.

Arbitrarily change window displays' viewport location 
(similarly to changing multiple display monitor orientations
with the OS desktop resolution settings).

'''
import wx
import subprocess
import sys

galaxiePicPath = r"C:\Users\boiruc\Pictures\galaxie.jpg"

class MyPanel(wx.Panel):
    def __init__(self, parent, iD):
        wx.Panel.__init__(self, parent, iD)
        
    def onPaint(self, event):
          ''' Called when the window is exposed. '''
          # Create a buffered paint DC.  It will create the real
          # wx.PaintDC and then blit the bitmap to it when dc is
          # deleted.  Since we don't need to draw anything else
          # here that's all there is to it.
          #dc = wx.BufferedPaintDC(self, self.buffer)

#1. Create window
class MyFrame(wx.Frame):
    def __init__(self, parent, iD=-1, pos=wx.DefaultPosition, size=(800, 600),
                 style=wx.DEFAULT_FRAME_STYLE):
        title = self.getTitle()
        wx.Frame.__init__(self, parent, iD, title, pos, size, style)
        self.SetCursor(wx.StockCursor(wx.CURSOR_PENCIL))
        self.timer = wx.Timer(self)
        #self.Bind(wx.EVT_TIMER, self.update, self.timer)
        self.modelRootX = 0
        self.modelRootY = 0
        
        self.initializeDisplay()
        self.runType = None
        self.initializeConnections()
        self.model = None
        
        
        #self.timer.Start(milliseconds = 0)
        #self.Bind(wx.EVT_MOVE,self.update)
        #self.Bind(wx.EVT_PAINT, self.onPaint)
        
    def onPaint(self,event):
        self.update(event)
        
    def initializeConnections(self):
        '''
        Checks to see if there are any other processes, if not
        then it will become the master process and load the
        model. If their 
        '''
        others = self.getOtherApps()
        if others >0:
            self.setSlave()
        else:
            self.setMaster()
    
    def setSlave(self):
        '''
        Sets this process to be a listening slave
        '''
        self.runType = 'Slave'
        pass
    
    def setMaster(self):
        '''
        Sets this process to be the controlling master
        '''
        self.runType = 'Master'
        pass
    
    def initializeDisplay(self):
        '''
        Creates initial GUI elements.
        '''
        self.panel = panel = MyPanel(self,-1)
        self.panel.SetDoubleBuffered(True)
        self.mousePosText = wx.StaticText(panel,-1,'',(45,25))
        self.windowPosText = wx.StaticText(panel,-1,'',(45,45))
        self.windowSizeText = wx.StaticText(panel,-1,'',(45,65))
        self.modelPosText = wx.StaticText(panel,-1,'',(45,85))
        img = wx.EmptyImage(240,240)
        self.MX = 0
        self.MY = 0
        self.imageCtrl = wx.StaticBitmap(self.panel, wx.ID_ANY, 
                                         wx.BitmapFromImage(img))
        self.loadImage(galaxiePicPath)
        
        self.windowPos = self.GetPositionTuple()
        self.newX = self.windowPos[0]
        self.newY = self.windowPos[1]
        self.MX = x = self.modelRootX - self.newX
        self.MY = y = self.modelRootY - self.newY
        self.imageCtrl.MoveXY(x, y)
        
    def loadImage(self, filepath):
        '''
        Loads an image and returns wx.image of it
        '''
        imgFile = wx.Image(filepath, wx.BITMAP_TYPE_ANY)
        self.imageCtrl.SetBitmap(wx.BitmapFromImage(imgFile))
        self.panel.Refresh()
        #self.info = {self.title+ ' Mouse Absolute Position: ':}
        
    def update(self,event):
        '''
        Updates window info & display
        '''
        self.updateMyInfo()
        self.getMyInfo()
        self.adjustDisplayXY()
        #self.broadCastMyInfo()
        #self.receiveTheirInfo()
        self.displayMyInfo()
        
    def broadCastMyInfo(self):
        '''
        Sends data to all other discovered applications
        '''
        pass
    
    def receiveTheirInfo(self):
        '''
        Checks for newly received data from other 
        applications
        '''
        pass
    
    
    
    def getTitle(self):
        '''
        Attempts to determine how many windows of this same
        application are already running, and make the title 
        of this application the count + 1
        '''
        others = self.getOtherApps()
        self.num = others + 1
        self.title = 'Window ' + str(self.num)
        return self.title
        
    def getOtherApps(self):
        '''
        Gets number of applications the same as this one
        '''
        myScriptName = __file__
        print myScriptName
        cmd = cmd = 'WMIC PROCESS get Caption,Commandline,Processid'
        proc = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
        count = 0
        for line in proc.stdout:
            parts = line.split()
            if 'python.exe' in line:
                if myScriptName in line:
                    print parts
                    count += 1
        #sys.exit()
        return count-1
        
    def updateMyInfo(self):
        '''
        Updates all mouse and window position information
        '''
        self.info = []
        if self.runType == 'Master':
            self.getMouseInfo()
        elif self.runType == 'Slave':
            self.getSlaveInfo()
        
    
    def getMyInfo(self):
        '''
        gets important information about this window
        including its size and position
        '''
        self.windowSize = self.GetClientSizeTuple()
        self.windowPos = self.GetPositionTuple()
        self.info.append([self.windowPosText,  self.title+ ' Window Position        : ', self.windowPos])
        self.info.append([self.windowSizeText, self.title+ ' Window Size            : ', self.windowSize])
        self.oldX = X1 = self.newX
        self.oldY = Y1 = self.newY
        self.newX = X2 = self.windowPos[0]
        self.newY = Y2 = self.windowPos[1]
        self.dX = X1-X2
        self.dY = Y1-Y2
        self.info.append([self.modelPosText, self.title+ ' Model Position         : ', [self.MX, self.MY]])
            
    def getMouseInfo(self):
            
        self.mouseScrnPos = wx.GetMousePosition()
        #self.mousePanelPos = self.ScreenToClientXY(self.mouseScrnPos)
        self.mousePanelPos = (0,0)
        
        title = self.title
        
        
        self.info.append([self.mousePosText,   title+ ' Mouse Absolute Position: ', self.mouseScrnPos])
        self.info.append([None,                title+ ' Mouse Relative Position: ', self.mousePanelPos])
        
    def getSlaveInfo(self):
        '''
        Will gather information pertinant to a slave window
        '''
        pass
    def displayMyInfo_Old(self):
        '''
        Displays all infor in self.info
        '''
        for data in self.info:
            print data[0],str(data[1])
    
    def displayMyInfo(self):
        '''
        Displays all infor in self.info
        '''
        
        for data in self.info:
            if isinstance(data[0], wx.StaticText):
                #data[0].
                text = data[1]+str(data[2])
                data[0].SetLabel(text)
            #if isinstance(#data[0] 
            #print data[0],str(data[1])
    
    def adjustDisplayXY(self):
        '''
        Calculates the change in position of the window and
        applies that to keep the model view stationary
        '''
        self.dX
        self.dY
        if self.dX != 0 or self.dY != 0:
            self.MX += self.dX
            self.MY += self.dY
            self.imageCtrl.MoveXY(self.MX,self.MY)


if __name__ == '__main__':
    app = wx.App(False)
    frame = MyFrame(None)
    frame.Show()
    app.MainLoop()