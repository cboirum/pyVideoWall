'''
Author: Curtis Boirum
Date: 7/8/2013

Purpose: This script will create the tile dislpay server and wait for 
         clients to connect using a list of ports
         
         
Future Plans: Create a tiled view manager gui or text file that allows
                static definitions of screen client positions/sizes/scaling
                
'''

import tileMain_v2
import wx
import os
import subprocess
import thread
import time
import socket


#modelDataPath = r"C:\Users\Public\Pictures\galaxie.jpg"
modelDataPath = r"galaxie.jpg"
modType = 'ImageCtrl'
settingsFile = r"settingsFile.txt"
createClients = True
    
def getSettings():
    '''
    Returns the # of clients to spawn, the starting port 
    number, and the number of additional ports to leave
    open for connections.
    '''
    fle = open(settingsFile,'r')
    contents = []
    for line in fle.readlines():
        if line[0] != '#':
            if '\n' in line:
                contents.append(line[:-1])
            else:
                contents.append(line)
    numClients = int(contents[0])
    startPort = int(contents[1])
    numPorts = int(contents[2])
    fle.close
    print "Number of Clients:",numClients
    print "Starting Port    :",startPort
    print "Number of Ports  :",numPorts
        
    #numClients = 1
    #numPorts = 10

    
    
    if numPorts < numClients:
        numPorts = numClients
    
    return numClients,startPort,numPorts

def startClient(client,host):
    '''
    Starts another Python instance running the tileClientMain.py script
    using host and cPort.
    '''
    scriptPath = "python.exe tileClientMain.py"
    cmdString = '"' + scriptPath + ' ' + host + ', ' + str(client) + '"'
    cmdString = scriptPath + ' ' + host + ' ' + str(client)
    args = [host, str(client)]
    args = ', '.join(args)
    #python.exe tileClientMain.py localhost, 6000
    #print"cmdString:",cmdString
    #os.system(scriptPath)
    #subprocess.call(cmdString)
    #process = subprocess.Popen(scriptPath)
    print cmdString
    #process = subprocess.Popen(scriptPath, args)
    os.system(cmdString)
    
#def startRemoteServer(host,port,clients):
def getHost():
    '''
    returns the host defined in the text file in the same folder as this script
    (use the computer's name as identified on the Network - look in windows explorer)
    '''
    fle = open('ServerHost.txt','r')
    stuff = []
    for line in fle.readlines():
        if line[0] != '#':
            if '\n' in line:
                stuff.append(line[:-1])
            else:
                stuff.append(line)
    if stuff[0] == 'gethostname':
        host = socket.gethostname()
    else:
        host = stuff[0]
    fle.close
    #print "Connecting to:",host, 'on', port
    return host#,port

if __name__ == '__main__':
    app = wx.App(False)
    frame = tileMain_v2.MyFrame(None)
    frame.createModel(modType, frame.panel, modelDataPath)
    host = socket.gethostname()
    #host = socket.gethostbyname(host)
    #host = '192.168.1.120'
    host = getHost()
    numClients,port,numPorts = getSettings()
    #host = 'localhost'
    #port = 6000
    print "Starting connection host/port:",host,port
    frame.initializeConnections(host,port,leader=True, numClients = numPorts)
    frame.Show()
    clientList = range(port, port + numClients)
    print"ClientList:",clientList
    if createClients:
        for client in clientList:
            print"Starting Client:",client
            thread.start_new_thread(startClient,(client,host))
            time.sleep(1)
    app.MainLoop()