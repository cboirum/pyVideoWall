'''
Author: Curtis Boirum
Date: 7/8/2013

Purpose: This script will create the tile dislpay client and and attempt to
            connect to the tile display server. It will start with port 5000
            and keep incrementing the port number until it manages to connect
            or it reaches the port limit
         
Future Plans: Create a tiled view manager gui or text file that allows
                static definitions of screen client positions/sizes/scaling
                
'''

import tileMain_v2
import wx
import sys
import os

modelDataPath = r"galaxie.jpg"
modType = 'ImageCtrl'
portLimit = 5

def getHost():
    '''
    returns the host defined in the text file in the same folder as this script
    (use the computer's name as identified on the Network - look in windows explorer)
    '''
    fle = open('RemoteHost.txt','r')
    stuff = []
    for line in fle.readlines():
        if line[0] != '#':
            if '\n' in line:
                stuff.append(line[:-1])
            else:
                stuff.append(line)
    host = stuff[0]
    port = stuff[1]
    fle.close
    print "Connecting to:",host, 'on', port
    return host,port

if __name__ == '__main__':
    if len(sys.argv) > 1:
        #print"System arg values:", sys.argv
        args = sys.argv
        host = args[1]
        if len(sys.argv) >2:
            port = args[2]
            
    else:
        #print"not enough system arg values:", sys.argv
        #port = 6002
        host,port = getHost()
        #host = 'WN7X64-3HXZXN1'
        #host = '192.168.1.138'
        #port = 6002
        #host = 'localhost'
        #host = 'C001540206'
        #host = 'C001407742'
        #host = 'C001407742A'
        #curtCAT  = remoteComputer(port,'C001407742',0)
    #print "Connecting on host/port:",host,port
    app = wx.App(False)
    frame = tileMain_v2.MyFrame(None)
    frame.createModel(modType, frame.panel, modelDataPath)
    #host = 'localhost'
    #host = 'C001407742A'
    #frame.portLimit = 5
    
    frame.Show()
    port = int(port)
    print"Starting follower with host/port:",host,port
    frame.initializeConnections(host,port)
    app.MainLoop()