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
import thread
import socket

from wx.lib.floatcanvas import NavCanvas, FloatCanvas, Resources

galaxiePicPath = r"C:\Users\boiruc\Pictures\galaxie.jpg"
modType = 'ImageCtrl'
hostList = ['localhost',
            ]
portList = [5000,
            5001,
            5002,
            5003,
            5004,
            ]
#modType = 'FloatCanvas'

#class MyPanel(wx.Panel):
#    def __init__(self, parent, iD):
#        wx.Panel.__init__(self, parent, iD)
#        
#    def onPaint(self, event):
#          ''' Called when the window is exposed. '''
#          # Create a buffered paint DC.  It will create the real
#          # wx.PaintDC and then blit the bitmap to it when dc is
#          # deleted.  Since we don't need to draw anything else
#          # here that's all there is to it.
#          #dc = wx.BufferedPaintDC(self, self.buffer)
class Leader(object):
    '''
    Listens on specified ports for client messages
    '''
    def __init__(self, parent, portList):
        print"Making the leader"
        self.parent = parent
        self.portList = portList
        self.port = portList.pop()
        self.conns = {}
        self.clients = []
        self.servers = []
        self.viewPorts = {}
        for port in portList:
            thread.start_new_thread(self.listenThread,(port,''))
            
    def listenThread(self,port,n):
        '''
        Listens on a port in it's own thread for new clients
        to connect
        '''
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        host = ''
        s.bind((host, port))
        self.servers.append(s)
        #print"Listening on Port: ",port
        print "listening"
        s.listen(1)
        conn, addr = s.accept()
        self.clients.append(addr)
        self.conns[addr] = conn
        #self.conn = conn
        while True:
            
            
            data = conn.recv(1024)
            #print "received: ",data, 'on port: ', port
            
            self.respond(conn,data)
            #self.conn.send("1::5000::Here is your stuff.")
    def ModelMoved(self, x, y):
        '''
        Send current model position to clients
        '''
        for client in self.clients:
            #print"updating client: ",str(client),"with: ", self.parent.MX,self.parent.MY
            msg = 'dx=='+str(self.parent.MX+self.parent.newX)+' dy=='+str(self.parent.MY+self.parent.newY)
            self.post(client,msg)
    
    def post(self, addr, msg):
        '''
        Post data to clients
        '''
        
        msg = '1::'+str(addr)+'::'+msg
        self.conns[addr].send(msg)
            
    def respond(self, conn, data):
        '''
        Parses incoming data into commands and acts on them
        '''
        print data
        code, addr, msg = data.split('::')
        if code == '3':
            '''
            3 is the code for highest priority messages such as
            registration and closing/errors
            '''
            if msg == 'register':
                self.viewPorts[addr] = {}
                print addr, "Registered"
                self.conns[addr] = conn
                conn.send("accepted")
        elif code == '2':
            '''
            2 is the code for requesting information
            '''
#            msg = 'dx=='+str(self.parent.Mx)+' dy=='+str(self.parent.My)
#            #print addr,"is requesting model information"
#            self.post(self.conn,msg)
            
        elif code == '1':
            '''
            1 is code for posting information
            '''
            #print addr,"is posting information:"
            #print msg    
                
class Follower(object):
    '''
    Talker object used by clients to communicate with the server
    '''
    def __init__(self, parent, host, port):
        print"Creating Follower"
        self.parent = parent
        self.port = port
        self.host = host
        self.clients = []
        self.servers = []
        
        self.makeConnection()
        
    def ModelMoved(self, n1, n2):
        '''
        dummy function that does nothing for follower
        '''
        pass
        
    def makeConnection(self):
        '''
        Make connection to the Leader server
        '''
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        print"Connecting to host/port:", self.host,self.port
        s.connect((self.host,self.port))
        self.connection = s
        self.register()
        
    def register(self):
        '''
        Registers this window with the server
        '''
        msg = "3::"+str(self.port)+'::register'
        self.connection.send(msg)
        data = self.connection.recv(1024)
        print "Leader says: ", data
        if data == "accepted":
            print "Server accepted registration"
            thread.start_new_thread(self.listenGud, (True,True))
        #self.testMessage(s)
    
    def listenGud(self, n, n1):
        '''
        Main listening loop waiting for updates from the leader,
        updates are stored into data for the display update thread
        to use.
        '''
        print"Asking Leader for directions"
        while True:
            #msg = "2::" + str(self.port) + "::gimmegimme"
            #self.connection.send(msg)
            #print"message sent"
            data = self.connection.recv(1024)
            try:
                self.respond(data)
            except:
                print"Communication Error"*4
    def respond(self, data):    
        '''
        parses incoming data into instructions and carries them out
        '''
        code, addr, msg = data.split("::")
        #print data
        if code == "1":
            #print "Leader is sending instructions"
            print msg
            parts = msg.split()
            data = {}
            for part in parts:
                key, value = part.split('==')
                if key not in data.keys():
                    data[key] = int(value)
            self.parent.MX = data['dx'] - self.parent.newX
            self.parent.MY = data['dy'] - self.parent.newY
            self.parent.adjust2Position()
            
                
        #self.parent.parent.MdX
        
    def testMessage(self, s):
        '''
        just for testing network
        '''
        msg = 'This is ' + str(self.port)
        print self.port,"Sending message"
        s.send(msg)
        
#        for port in portList:
#            thread.start_new_thread(self.listenThread,(port))
            
#    def listenThread(self,port):
#        '''
#        Listens on a port in it's own thread for new clients
#        to connect
#        '''
#        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#        host = ''
#        s.bind((host, port))
#        self.servers.append(s)
#        while True:
#            s.listen(1)
#            conn, addr = s.accept()
#            data = conn.recv(1024)
#            print("received: ",data)    
        
        

class Model(object):
    '''
    This object defines the wrapper that allows synchronous
    data models to be displayed by multiple applications
    '''
    def __init__(self, parent, dataPath):
        self.parent = parent
        self.dx = 0
        self.dy = 0
        self.xOffset = 0
        self.yOffset = 0
        self.zOffset = 0
        self.rxOffset = 0
        self.ryOffset = 0
        self.rzOffset = 0
        self.LoadData(dataPath)
        self.SetDisplay()
        
    def LoadData(self,dataPath):
        '''
        If data is not an image, this must be subclassed
        '''
        self.data = wx.Image(dataPath, wx.BITMAP_TYPE_ANY)
        pass
    
#    def MoveXY(self,x,y):
#        '''
#        moves the model x and y pixels, requires subclassing
#        '''
    def MoveXY(self, x, y):
        '''
        Applies simple x y movement to the model in Window coordinates
        '''
        self.display.MoveXY(x, y)
    
    def SetDisplay(self):
        '''
        Must be subclassed with your specifid display initialization
        functions
        '''
        
    
class FCanvasModel(Model):
    '''
    Based on "FloatCanvas" example in the wxPython Demo
    Can be found under "More Windows/Controls"
    '''
    def __init__(self, parent, dataPath):
        self.NC = NavCanvas.NavCanvas(parent, Debug = 0, BackgroundColor = "DARK SLATE BLUE")
        self.display = self.NC.Canvas 
  #     NC.
#        self.display = FloatCanvas.FloatCanvas(parent, Debug = 0)#, BackgroundColor = "DARK SLATE BLUE")
        Model.__init__(self, parent, dataPath)
        #parent.Bind(FloatCanvas.EVT_MOTION, self.OnMove) 
        #parent.Bind(FloatCanvas.EVT_MOUSEWHEEL, self.OnWheel)
    def SetDisplay(self):
        Point = (0,0)
        self.NC.SetSize((1000,1000))
        self.display.SetSize((1000,1000))
        self.display.AddBitmap(self.data, Point, Position = "br" )
        self.display.Draw()
        pass
    
    def MoveXY(self, x, y):
        #wx.GetApp().Yield(True)
        x = -self.parent.GetParent().dx
        y = -self.parent.GetParent().dy
        #self.display.MoveXY(x, y)
        self.display.MoveImage((x,y), 'Pixel', True)
        print("Move X,Y: ",x,y)
  #      self.display.Draw()
         
class ImageCtrlModel(Model):
    def __init__(self, parent, dataPath):
        img = wx.EmptyImage(240,240)
        self.display = wx.StaticBitmap(parent, wx.ID_ANY, 
                                         wx.BitmapFromImage(img))
        Model.__init__(self, parent, dataPath)
        
        
    def MoveXY(self, x, y):
        self.display.MoveXY(x, y)
        
    def SetDisplay(self):
        self.bmp = wx.BitmapFromImage(self.data)
        self.display.SetBitmap(self.bmp)
        
        
    def yay(self,event):
        print"Yay"*10
        #self.bmp.Bind()
        
#1. Create window
class MyFrame(wx.Frame):
    def __init__(self, parent, iD=-1, pos=wx.DefaultPosition, size=(800, 600),
                 style=wx.DEFAULT_FRAME_STYLE):
        '''
        Coordinate Naming Conventions:
        
        Wall - Global coordinates of the virtual "wall" that is created by
        all combined displays. Typically uses the leader as the top left 
        corner but can vary
        
        Machine - Coordinate system of the display output for the current
        physical display device which could include multiple monitors 
        connected to the same computer. WRT Wall coordinates.
        
        Screen - Coordinate system of each individual screen attached to 
        the same physical display device. If there is only 1 screen then 
        this is the same as Machine coordinates. WRT Machine coordinates
        
        Window - Coordinate system of the current application window wrt
            the Screen coordinates.
        
        +x is to the right
        +y is downward
        
        WallRt = coordinate point of the wall (0,0) that is universal center
        MachineRt = coordinate point of the Display wrt to Wall
        ScreenRt = Relative position of the current system screen wrt 
            MachineRt
        WindowRt = Relative position of current application window wrt 
            MachineRt
        '''
        title = self.getTitle()
        wx.Frame.__init__(self, parent, iD, title, pos, size, style)
        #self.SetCursor(wx.StockCursor(wx.CURSOR_PENCIL))
        self.timer = wx.Timer(self)
        #self.Bind(wx.EVT_TIMER, self.update, self.timer)
        self.modelRootX = -1080
        self.modelRootY = 0
        self.dx = 0
        self.dy = 0
        self.Mdx = 0
        self.Mdy = 0
        self.Mx = 0
        self.My = 0
        self.panel = wx.Panel(self, iD)
        self.panel.SetDoubleBuffered(True)
        self.createModel(modType, self.panel, galaxiePicPath)
        self.Model.display.Bind(wx.EVT_MOUSE_EVENTS,self.updateModel)
        self.panel.Bind(wx.EVT_MOUSE_EVENTS,self.updateModel)
        self.panel.Bind(wx.EVT_MOUSEWHEEL,self.updateModel)
        #self.Model.display.Bind(wx.EVT_MOTION,self.updateModel)
        self.initializeDisplay()
        self.runType = None
        self.initializeConnections()
        #self.model = None
        
        #self.timer.Start(milliseconds = 0)
        self.Bind(wx.EVT_MOVE,self.update)
        #self.Bind(wx.EVT_LEFT_DOWN,self.update)
        #self.panel.Bind(wx.EVT_LEFT_DOWN,self.update)
        #self.Bind(wx.EVT_LEFT_DOWN,self.update)
        #self.Bind(wx.EVT_MOUSE_EVENTS,self.update)
        #self.Bind(wx.EVT_PAINT, self.onPaint)
        
    def createModel(self,modType,parent,dataPath):
        '''
        returns the model to be used 
        '''
        if modType == 'FloatCanvas':
            model = FCanvasModel(parent,dataPath)
        elif modType == 'ImageCtrl':
            model = ImageCtrlModel(parent,dataPath)
        self.Model = model
        #self.Model.display.Bind(wx.EVT_MOTION,self.updateModel)
        
    def onPaint(self,event):
        self.update(event)
        
    def initializeConnections(self):
        '''
        Checks to see if there are any other processes, if not
        then it will become the Leader process and load the
        model.
        '''
        others = self.getOtherApps()
        port = portList[others]
        host = 'localhost'
        if others >0:
            self.setFollower()
            self.Com = Follower(self, host, port)
        else:
            self.setLeader()
            self.Com = Leader(self, portList)
    
    def setFollower(self):
        '''
        Sets this process to be a listening Follower
        '''
        self.runType = 'Follower'
        
        pass
    
    def setLeader(self):
        '''
        Sets this process to be the controlling Leader
        '''
        self.runType = 'Leader'
    
    def initializeDisplay(self):
        '''
        Creates initial GUI elements.
        '''
        panel = self.panel
        self.mousePosText = wx.StaticText(panel,-1,'',(45,5))
        self.windowPosText = wx.StaticText(panel,-1,'',(45,25))
        self.windowSizeText = wx.StaticText(panel,-1,'',(45,45))
        self.modelPosText = wx.StaticText(panel,-1,'',(45,65))
        self.modelAbsPosText = wx.StaticText(panel,-1,'',(45,85))
        self.MX = 0
        self.MY = 0
        self.newMx = 0
        self.newMy = 0
        
        self.windowPos = self.GetPositionTuple()
        self.newX = self.windowPos[0]
        self.newY = self.windowPos[1]
        self.MX = x = self.modelRootX - self.newX
        self.MY = y = self.modelRootY - self.newY
        self.Model.MoveXY(x, y)
        
    def updateModel(self,event):
        '''
        Applies event actions to the model
        '''
        #print dir(event)
        
            #left click and drag event
        self.getMouseInfo()
        #print event.GetWheelRotation()
        #print dir(event)
        #print event.WheelRotation
        if event == wx.EVT_MOUSEWHEEL:
            print"Mousewheel"
            
        
        if event.LeftIsDown():
            self.adjustGlobalDisplay()
        
    def update(self,event):
        '''
        Updates window info & display
        '''
        self.updateMyInfo()
        self.getMyInfo()
        #print(event.GetWheelRotation())
#        absPos = wx.GetMousePosition()
#        print"absPos:",absPos
#        
#        point = self.ScreenToClient(absPos)
#        print"relPos:",point
#        HitTest = self.panel.HitTest(point)
#        print"Hit test result: ",HitTest

        self.adjustLocalDisplayXY()
        #if self.panel.HitTest(point) == 1:
        #self.adjustLocalDisplayXY()
        
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
        cmd = 'WMIC PROCESS get Caption,Commandline,Processid'
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
        if self.runType == 'Leader':
            self.getMouseInfo()
        elif self.runType == 'Follower':
            self.getFollowerInfo()
    
    def getMyInfo(self):
        '''
        gets important information about this window
        including its size and position
        '''
        self.windowSize = self.GetClientSizeTuple()
        self.windowPos = self.GetPositionTuple()
        self.mousePos = self.getMouseInfo
        self.info.append([self.windowPosText,  self.title+ ' Window 2 Wall Position : ', self.windowPos])
        self.info.append([self.windowSizeText, self.title+ ' Window Size            : ', self.windowSize])
        self.oldx = X1 = self.newX
        self.oldy = Y1 = self.newY
        self.newX = X2 = self.windowPos[0]
        self.newY = Y2 = self.windowPos[1]
        self.dx = X1-X2
        self.dy = Y1-Y2
        self.MabsX = X2 + self.MX
        self.MabsY = Y2 + self.MY
        self.info.append([self.modelPosText, self.title+ ' Model Position         : ', [self.MX, self.MY]])
        self.info.append([self.modelAbsPosText, self.title + 'Model 2 Wall Position:', [self.MabsX, self.MabsY]])
            
    def getMouseInfo(self):
        self.mouseScrnPos = wx.GetMousePosition()
        self.oldMx = X1 = self.newMx
        self.oldMy = Y1 = self.newMy
        self.newMx = X2 = self.mouseScrnPos[0]
        self.newMy = Y2 = self.mouseScrnPos[1]
        self.Mdx = X1-X2
        self.Mdy = Y1-Y2
        #self.Mdw = W1-W2
        #print"Mouse dx,dy:",self.Mdx,self.Mdy

        
        #self.mousePanelPos = self.ScreenToClientXY(self.mouseScrnPos)
        #self.mousePanelPos = (0,0)
        
        #title = self.title
        
        #self.info.append([self.mousePosText,   title+ ' Mouse Absolute Position: ', self.mouseScrnPos])
        #self.info.append([None,                title+ ' Mouse Relative Position: ', self.mousePanelPos])
        
    def getFollowerInfo(self):
        '''
        Will gather information pertinant to a Follower window
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
    
    def adjustLocalDisplayXY(self):
        '''
        Calculates the change in position of the window and
        applies that to keep the model view stationary
        '''
        self.dx
        self.dy
        if self.dx != 0 or self.dy != 0:
            self.MX += self.dx
            self.MY += self.dy
            self.Model.MoveXY(self.MX,self.MY)
            
    def adjustGlobalDisplay(self):
        '''
        Applies changes to the model's position globably.
        '''
        #self.Mdx
        #self.Mdy
        #if self.Mdx != 0 or self.Mdy != 0:
        self.MX -= self.Mdx
        self.MY -= self.Mdy
        #self.MabsX = self.MX + self.newX
        #self.MabsY = self.MY + self.newY
        print"Model X,Y", self.MX, self.MY
        self.Model.MoveXY(self.MX, self.MY)
        self.Com.ModelMoved(self.MX, self.MY)
        
    def adjust2Position(self):
        '''
        Move the model to a specified position
        '''
        print"Model X,Y", self.MX, self.MY
        self.Model.MoveXY(self.MX, self.MY)
        self.Com.ModelMoved(self.MX, self.MY)
        


if __name__ == '__main__':
    app = wx.App(False)
    frame = MyFrame(None)
    frame.Show()
    app.MainLoop()