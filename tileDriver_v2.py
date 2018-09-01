import tileMain_v5 as tileMain
import tileClient_v4 as tileClient
import tileServer_v4 as tileServer
import sys
import socket

modelOptions = ['ImageCtrl','3D']

def makeClient(argv,modType = 'ImageCtrl'):
    runType = 'Client'
    port = int(argv[1])
    if len(argv)>2:
        host = argv[2]
    else:
        host = 'localhost'
    tileClient.CreateClient(host,port,modType = modType)
    
def makeServer(modelType = 'ImageCtrl'):
    runType = 'Server'
    tileServer.CreateServer(modType = modelType)

if __name__ == '__main__':
    #sys.argv.append('6000')
    if len(sys.argv)>1:
        makeClient(sys.argv)
    else:
        makeServer()