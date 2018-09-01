'''
Tile Display Test by Curtis Boirum
7/2/13

update 7/16/13: Communication will now send pickled command objects
                and move broadcasting will only send to clients that
                are ready.
                
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
#import wx
#import subprocess
import sys
import thread
import socket
import subprocess
import time
import pickle

#wx_StaticText
import wx
from wx import StaticText as wx_StaticText
from wx import App as wxDotApp
from wx import Image as wxDotImage
from wx import BITMAP_TYPE_ANY as wxDotBITMAP_TYPE_ANY
from wx.lib.floatcanvas import NavCanvas, FloatCanvas, Resources

#galaxiePicPath = r"C:\Users\boiruc\Pictures\galaxie.jpg"
galaxiePicPath = r"galaxie.jpg"
screenSetupPath = r'ScreenSetup.txt'
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
def getScreenSetup():
    '''
    returns a dictionary of screen settings for various 
    client port connections
    '''
    fle = open(screenSetupPath,'r')
    lines = fle.readlines()
    info = []
    sInfo = {}
    curPort = '0'
    for line in lines:
        if line[0] != '#':
            if '\n' in line:
                line = line[:-1]
            parts = line.split()
            if len(parts) ==1:
                curPort = parts[0]
                sInfo[curPort] = {}
            if len(parts)>1:
                param = parts[0]
                value = parts[2]
                #values.remove('=')
                sInfo[curPort][param] = value
                
        #screenInfo[port][param] = value
    return sInfo
    

class Leader(object):
    '''
    Listens on specified ports for client messages
    '''
    def __init__(self, parent, host, portList):#, portList):
        print"Making the leader"
        self.parent = parent
        self.portList = portList
        self.port = portList[0]
        self.conns = {}
        self.clients = []
        self.registeredClients = []
        self.servers = []
        self.isReady = {}
        self.viewPorts = {}
        for port in portList:
            thread.start_new_thread(self.listenThread,(host,port))
    
    def setScreenPositions(self,event):
        '''
        Changes the coordinate offsets for all clients attached
        according to screenSetup document
        '''
        screenSetup = getScreenSetup()
        #print"updating client settings"
        for client in self.registeredClients:
            if client in screenSetup.keys():
                data = screenSetup[client]
                orders = []
                data['dx'] = str(self.parent.M2sX)
                data['dy'] = str(self.parent.M2sY)
                for param in data.keys():
                    value = data[param]
                    if param not in ['dx','dy']:
                        param = 's'+param
                    orders.append(param+'=='+value)
                msg = ' '.join(orders)
                print msg
                self.post(client,msg,forceDelivery=True)
            else:
                print"No screen setup info for: ",client
        #thread.start_new_thread(self.threadManager, ('',''))
        
    def threadManager(self, n1, n2):
        '''
        restarts threads if they need to be terminated
        '''
        pass
            
    def listenThread(self,host,port):
        '''
        Listens on a port in it's own thread for new clients
        to connect
        '''
        #notConnected = False
        while True:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.host = host
            self.port = port
            s.bind((host, port))
            self.clients.append(port)
            print "listening on: ",port,host
            s.listen(1)
            conn, addr = s.accept()
            while True:
                try:
                    data = conn.recv(1024)
                    self.respond(conn,data)
                except:
                    #time.sleep(.1)
                    break
                    #s.close()
                    #break
        #self.listenThread(host,port)
        
    def ModelMoved(self, x, y):
        '''
        Send current model position to clients
        '''
        #for client in self.clients:
#        x = self.parent.MX+self.parent.newX
#        y = self.parent.MY+self.parent.newY
        #msg = 'dx=='+str(self.parent.MX+self.parent.newX)+' dy=='+str(self.parent.MY+self.parent.newY)
        #print msg
        for client in self.registeredClients:
            #print"updating client: ",str(client),"with: ", self.parent.MX,self.parent.MY
            #msg = pickle.dumps(commands,2)
            msg = 'dx=='+str(self.parent.MX+self.parent.newX)+' dy=='+str(self.parent.MY+self.parent.newY)
            self.post(client,msg)
            
    def comThread(self):
        '''
        sends messages from the que
        '''
        while True:
            msg = self.msgs.pop()
            
        #time.sleep(.2)
    
    def post(self, addr, msg, forceDelivery=False):
        '''
        Post data to clients
        '''
        messageNotSent = True
        while messageNotSent:
            #print"posting"
            if self.isReady[addr]:
                msg = '1::'+str(addr)+'::'+msg
            #print "msg:",msg
            #print("Connections:")
            #print self.conns.keys()
                try:
                    self.conns[str(addr)].send(msg)
                    self.isReady[addr] = False
                    messageNotSent = False
                except:
                    self.isReady[addr] = False
                    s = self.conns.pop(str(addr))
            if not forceDelivery:
                messageNotSent = False
                
                    #print addr, "closed"
                    #self.listenThread(self.host, int(addr))
            
    def respond(self, conn, data):
        '''
        Parses incoming data into commands and acts on them
        '''
        #print data
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
                self.registeredClients.append(addr)
                self.isReady[addr] = True
                conn.send("accepted")
                
        elif code == '2':
            '''
            2 is the code for requesting information
            '''
            self.isReady[addr] = True
            
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
    def __init__(self, parent):
        
        self.parent = parent
        self.portLimit = self.parent.portLimit
        self.port = int(parent.port)
        self.host = parent.host
        self.clients = []
        self.servers = []
        self.needUpdate = True 
        self.watchDogTime = 0.5 #seconds to allow no response before resending ready signal
        self.watchDogUpdate = 0.2 #time between watchdog checks
        self.lastCom = time.time()
        self.attemptsLimit = 10
        print"Creating Follower on Port:",self.port
        thread.start_new_thread(self.watchDog,('',''))
        self.makeConnection()
    
    def watchDog(self, n1, n2):
        '''
        keeps track of elapsed time since last message and
        sets the flag to resend "ready" signal if the watchDogTime
        in seconds is reached
        '''
        while 1:
            time.sleep(self.watchDogUpdate)
            now = time.time()
            delta = now - self.lastCom
            if delta>= self.watchDogTime:
                self.needUpdate = True
        
    def ModelMoved(self, n1, n2):
        '''
        dummy function that does nothing for follower
        '''
        pass
    def makeConnection(self, attempts = 0):
        '''
        Make connection to the Leader server
        '''
        #s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        #s.settimeout(.25)
        #print"Trying to connect, host/port:",self.host,self.port
        connected = False
        while not connected:
            print"Trying to connect, host::port:",self.host,"::",self.port
            #socket.socket.settimeout(3)
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(3)
            try:
                s.connect((self.host,self.port))
                connected = True
            except:
                connected = False
            #self.conn = socket.create_connection((self.host,self.port)) 
            
            s.settimeout(None)
            if connected:
                self.connection = s
                print"Attempting to register"
                self.register()
            else:
                #print"Could not connect to server"
                #self.port += 1
                #attempts += 1
                if attempts < self.attemptsLimit:
                    #print"Trying another port:", self.port
                    time.sleep(2)
                    
                    #self.makeConnection(attempts = attempts)
                else:
                    print"I Give Up."
                    time.sleep(10)
                    sys.exit()
                    
    def makeConnection_OLD3(self, attempts = 0):
        '''
        Make connection to the Leader server
        '''
        #s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        #s.settimeout(.25)
        #print"Trying to connect, host/port:",self.host,self.port
        connected = False
        
        print"Trying to connect, host::port:",self.host,"::",self.port
        #socket.socket.settimeout(3)
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(3)
        try:
            s.connect((self.host,self.port))
            connected = True
        except:
            connected = False
        #self.conn = socket.create_connection((self.host,self.port)) 
        
        s.settimeout(None)
        if connected:
            self.connection = s
            self.register()
        else:
            print"Could not connect to server"
            self.port += 1
            attempts += 1
            if attempts < self.attemptsLimit:
                print"Trying another port:", self.port
                time.sleep(1)
                
                self.makeConnection(attempts = attempts)
            else:
                print"I Give Up."
                time.sleep(10)
                sys.exit()
            
    def makeConnection_OLD(self):
        '''
        Make connection to the Leader server
        '''
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        #s.settimeout(.25)
        #print"Trying to connect, host/port:",self.host,self.port
        connected = False
        try:
            print"Trying to connect, host/port:",self.host,self.port
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((self.host,self.port))
            connected = True
        except:
            from traceback import print_exc as tracebackDotPrint_exc
            tracebackDotPrint_exc(file=sys.stdout)
            print"could not connect on port:",self.port
        if connected:
            self.connection = s
            self.register()
        else:
            print"Could not connect to server"
            sys.exit()
                        
    def makeConnection_OLD2(self):
        '''
        Make connection to the Leader server
        '''
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(.25)
        print"Trying to connect, host/port:",self.host,self.port
        portNum = 0
        connected = False
        while portNum <= self.portLimit and not connected:
            try:
                print"Trying to connect, host/port:",self.host,self.port
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.connect((self.host,self.port))
                connected = True
            except:
                from traceback import print_exc as tracebackDotPrint_exc
                tracebackDotPrint_exc(file=sys.stdout)
                print"could not connect on port:",self.port

        if connected:
            self.connection = s
            self.register()
        else:
            print"Could not connect to server"
            sys.exit()
        
    def register(self, newThread = True):
        '''
        Registers this window with the server
        '''
        msg = "3::"+str(self.port)+'::register'
        self.connection.send(msg)
        data = self.connection.recv(1024)
        print "Leader says: ", data
        if data == "accepted":
            print "Server accepted registration"
            if newThread:
                thread.start_new_thread(self.listenGud, (True,True))
            else:
                self.listenGud(True,True)
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
            try:
                data = self.connection.recv(1024)
                try:
                    self.respond(data)
                except:
                    print data
                    print"Communication Error"*4
                if self.watchDogTime:
                    self.watchDogTime = False
                    print"Wait time exceeded"
                    self.sendReady()
            except:
                self.reconnect()
    def reconnect(self):
        '''
        Attempts the reconnect to host without starting a new
        connection thread
        '''
        self.makeConnection()
        self.register(newThread=False)
                
    def respond(self, data):    
        '''
        parses incoming data into instructions and carries them out
        '''
        code, addr, msg = data.split("::")
        #print data
        if code == "1":
            #print "Leader is sending instructions"
#            print msg
            parts = msg.split()
#            data = pickle.load(msg)
            data = {}
            for part in parts:
                key, value = part.split('==')
                if key not in data.keys():
                    data[key] = int(value)
            self.setParams(data)
            self.sendReady()
    
    def setParams(self,data):
        '''
        loops through data object and applies values
        '''
        print data
        if 'sx' in data.keys():
            self.parent.sx = data['sx']
        if 'sy' in data.keys():
            self.parent.sy = data['sy']
        if 'MabsX' in data.keys():
            self.parent.MabsX = data['dx']#data['MabsX']
        if 'MabsY' in data.keys():
            self.parent.MabsY = data['dy']#data['MabsY']
        if 'dx' in data.keys():
            self.parent.MX = data['dx'] - self.parent.newX - self.parent.sx #converting from wall coordinates to window
        if 'dy' in data.keys():
            self.parent.MY = data['dy'] - self.parent.newY - self.parent.sy
        self.parent.adjust2Position()
            
    def sendReady(self):
        '''
        Notifies Server that we are ready to receive new
        model positioning data
        '''
        msg = '2::'+ str(self.port) + '::ready'
        self.connection.send(msg)
            
                
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
        self.sx = 0 #X offset of this system's physical screen
        self.sy = 0 #Y offset of this system's physical screen
#        self.xOffset = 0
#        self.yOffset = 0
#        self.zOffset = 0
#        self.rxOffset = 0
#        self.ryOffset = 0
#        self.rzOffset = 0
        self.LoadData(dataPath)
        self.SetDisplay()
        
    def LoadData(self,dataPath):
        '''
        If data is not an image, this must be subclassed
        '''
        self.data = wxDotImage(dataPath, wxDotBITMAP_TYPE_ANY)
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
        #self.display.MoveXY
        self.display.MoveImage((x,y), 'Pixel', True)
        print("Move X,Y: ",x,y)
  #      self.display.Draw()
         
class ImageCtrlModel(Model):
    def __init__(self, parent, dataPath):
        img = wx.EmptyImage(240,240)
#        self.display = wx.StaticBitmap(parent, wx.ID_ANY, 
#                                         wx.BitmapFromImage(img))
        print"trying to load image from:", dataPath
        self.display = wx.StaticBitmap(parent, wx.ID_ANY, wx.BitmapFromImage(wxDotImage(dataPath, wxDotBITMAP_TYPE_ANY)))
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
        self.modelRootX = 0#-1080
        self.modelRootY = 0
        
        self.dx = 0
        self.dy = 0
        self.Mdx = 0
        self.Mdy = 0
        
        self.Mx = 0   #Model X coordinate
        self.My = 0   #Model Y coordinate
        self.M2wX = 0 #Model 2 window
        self.M2wY = 0 #Model 2 window
        self.M2sX = 0 #Model 2 screen
        self.M2sY = 0 #Model 2 screen
        self.sx = 0   #Screen 2 wall
        self.sy = 0   #Screen 2 wall
        self.portLimit = 10
        
        self.panel = wx.Panel(self, iD)
        self.panel.SetDoubleBuffered(True)
        
        
#        self.Model.display.Bind(wx.EVT_MOUSE_EVENTS,self.updateModel)
#        self.panel.Bind(wx.EVT_MOUSE_EVENTS,self.updateModel)
#        self.panel.Bind(wx.EVT_MOUSEWHEEL,self.updateModel)
#        #self.Model.display.Bind(wx.EVT_MOTION,self.updateModel)
#        self.initializeDisplay()
#        self.runType = None
#        self.initializeConnections()
#        #self.model = None
#        
#        #self.timer.Start(milliseconds = 0)
#        self.Bind(wx.EVT_MOVE,self.update)
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
        
        self.Model.display.Bind(wx.EVT_MOUSE_EVENTS,self.updateModel)
        self.panel.Bind(wx.EVT_MOUSE_EVENTS,self.updateModel)
        self.panel.Bind(wx.EVT_MOUSEWHEEL,self.updateModel)
        #self.panel.Bind(wx.EVT_RIGHT_UP,self.Com.setScreenPositions)
        #self.Model.display.Bind(wx.EVT_MOTION,self.updateModel)
        self.initializeDisplay()
        self.runType = None
        
        #self.model = None
        
        #self.timer.Start(milliseconds = 0)
        self.Bind(wx.EVT_MOVE,self.update)
        #self.Model.display.Bind(wx.EVT_MOTION,self.updateModel)
        
    def onPaint(self,event):
        self.update(event)
        
    def initializeConnections(self, host, port,leader = False, numClients = False):
        '''
        Checks to see if there are any other processes, if not
        then it will become the Leader process and load the
        model.
        '''
        if leader:
            self.SetTitle('Server')
        else:
            self.SetTitle('Client: '+str(port)) 
        self.host = host
        self.port = port
        if leader and numClients:
            portList = range(port,port + numClients)
            print"Creating leader with portList:",portList
            self.setLeader(host, portList)
        else:
            self.setFollower()
    
    def setFollower(self):
        '''
        Sets this process to be a listening Follower
        '''
        self.runType = 'Follower'
        self.Com = Follower(self)
        pass
    
    def setLeader(self, host, portList):
        '''
        Sets this process to be the controlling Leader
        '''
        self.runType = 'Leader'
        self.Com = Leader(self, host, portList)#, portList)
        self.panel.Bind(wx.EVT_RIGHT_UP,self.Com.setScreenPositions)
        self.Model.display.Bind(wx.EVT_RIGHT_UP,self.Com.setScreenPositions)
        self.Model.display.Bind(wx.EVT_MOUSEWHEEL,self.Com.setScreenPositions)
    
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
            self.update(True)
            #self.updateMyInfo()
        
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
        #print"Getting my info"
        self.windowSize = self.GetClientSizeTuple()
        
        self.windowPos = self.GetPositionTuple()
        self.mousePos = self.getMouseInfo
        #self.info.append([self.windowPosText,  'Window 2 Screen Position : ', self.windowPos])
        
        self.oldx = X1 = self.newX
        self.oldy = Y1 = self.newY
        self.newX = X2 = self.windowPos[0]
        self.newY = Y2 = self.windowPos[1]
        self.dx = X1-X2
        self.dy = Y1-Y2
        self.M2sX = X2 + self.MX
        self.M2sY = Y2 + self.MY
        
        self.info.append([self.Screen2WallText, 'Screen 2 Wall   : ', [self.sx, self.sy]])
        self.info.append([self.windowPosText,   'Window 2 Screen : ', self.windowPos])
        self.info.append([self.windowSizeText,  'Window Size     : ', self.windowSize])
        self.info.append([self.modelPosText,    'Model 2 Window  : ', [self.MX, self.MY]])
        self.info.append([self.modelAbsPosText, 'Model 2 Screen  : ', [self.M2sX, self.M2sY]])
    
    def initializeDisplay(self):
        '''
        Creates initial GUI elements.
        '''
        panel = self.panel
        #self.mousePosText = wx_StaticText(panel,-1,'',(45,5))
        self.Screen2WallText = wx_StaticText(panel,-1,'',(45,5))
        self.windowPosText = wx_StaticText(panel,-1,'',(45,25))
        self.modelPosText = wx_StaticText(panel,-1,'',(45,45))
        self.modelAbsPosText = wx_StaticText(panel,-1,'',(45,65))
        self.windowSizeText = wx_StaticText(panel,-1,'',(45,85))

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
        #print"Displaying my info"
        for data in self.info:
            if isinstance(data[0], wx_StaticText):
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
        #self.dx
        #self.dy
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
        #self.M2sX = self.MX + self.newX
        #self.MabsY = self.MY + self.newY
        #print"Model X,Y", self.MX, self.MY
        #print "MX",self.MX,"MY",self.MY
        #print "M2sX",self.M2sX,"MabsY",self.MabsY
        #print"GLOBAL"
        self.Model.MoveXY(self.MX, self.MY)
        self.Com.ModelMoved(self.MX, self.MY)
        self.displayMyInfo()
        
    def adjust2Position(self):
        '''
        Move the model to a specified position
        '''
        #print"Model X,Y", self.MX, self.MY
        #print"adjust2position"
        self.Model.MoveXY(self.MX, self.MY)
        self.Com.ModelMoved(self.MX, self.MY)
        self.displayMyInfo()
        


if __name__ == '__main__':
    if False:
        app = wxDotApp(False)
        frame = MyFrame(None)
        frame.createModel(modType, frame.panel, galaxiePicPath)
        host = 'localhost'
        port = 5000
        frame.initializeConnections(host,port,leader=True)
        frame.Show()
        app.MainLoop()
    else:
        getScreenSetup()
    