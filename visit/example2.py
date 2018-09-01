import sys
__system_bytecode_setting = sys.dont_write_bytecode
sys.dont_write_bytecode = True

#import sys
#sys.path.append(r"C:\Users\boiruc\AppData\Local\Programs\LLNL\VisIt 2.6.1\lib\site-packages")

from visit import *
Launch()


#import visitproxy
#
#host = "localhost"
#port = 9002
#password = "bob"
#BUFSIZE = 4096
#
##create a VisIt Proxy
#vp = visitproxy.ViewerProxy()
#
#gmap = sys.modules["__main__"].__dict__
#gmap["vp"] = vp
#
##connect to existing host & password
#vp.connect(host,port,password)


