'''
Author: Curtis Boirum
Date: 7/9/2013

Purpose: This script will create a server on a remote machine that will spawn clients
            that will connect to the orriginal server on the host machine.
         
'''

import mainTileTest5
import wx
import os
import subprocess
import thread
import time
import sys

modelDataPath = r"C:\Users\Public\Pictures\galaxie.jpg"
modType = 'ImageCtrl'
numClients = 2
createClients = True

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
    
if __name__ == '__main__':
    if len(sys.argv) > 1:
        #print"System arg values:", sys.argv
        args = sys.argv
        host = args[1]
        if len(sys.argv) >2:
            port = args[2]
    else:
        #print"not enough system arg values:", sys.argv
        port = 6002
        host = 'localhost'
    app = wx.App(False)
    frame = mainTileTest5.MyFrame(None)
    frame.createModel(modType, frame.panel, modelDataPath)
    host = 'localhost'
    port = 6002
    #frame.initializeConnections(host,port,leader=True, numClients = numClients)
    #frame.Show()
    clientList = range(port, port + numClients)
    print"ClientList:",clientList
    if createClients:
        for client in clientList:
            print"Starting Client:",client
            thread.start_new_thread(startClient,(client,host))
            time.sleep(1)
    app.MainLoop()