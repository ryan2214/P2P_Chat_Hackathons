import socket
import time
import sys

#get pc name
myname = socket.gethostname()
# get my ip
myPC_IP = socket.gethostbyname(myname)
print(myPC_IP)
COD = 'utf-8'
# inner ip
HOST = myPC_IP # server ip
# open from fire wall
PORT = 21566 # software port
BUFSIZ = 1024
ADDR = (HOST, PORT)
SIZE = 50 
tcpS = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # init socket obj
tcpS.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR,1) # add socket
tcpS.bind(ADDR) # bind ip
tcpS.listen(SIZE)  # set max link
while True:
    print("server start, listening")
    clientsocket, addr = tcpS.accept() 
    print("linked user", addr)
    while True:
        try:
            data = clientsocket.recv(BUFSIZ) # read msg
        except Exception:
            print("disconnected user", addr)
            break
        print("user said:",data.decode(COD))
        if not data:
            break
        msg = time.strftime("%Y-%m-%d %X") # get timestamp
        msg1 = '[%s]:%s' % (msg, data.decode(COD))
        clientsocket.send(msg1.encode(COD)) # send msg
    clientsocket.close() # close
tcpS.close()
