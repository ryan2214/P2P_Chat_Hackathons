import socket
from time import ctime
# public ip
HOST = '192.168.56.1' # server ip
# cloud port need open this
PORT = 21566 #port
BUFSIZ = 1024
ADDR = (HOST, PORT)
tcpCliSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # establish socket obj
tcpCliSock.connect(ADDR) # link server
while True:
    data = input('>>').strip()
    if not data:
        break
    tcpCliSock.send(data.encode('utf-8')) # send
    data = tcpCliSock.recv(BUFSIZ) # read
    if not data:
        break
    print(data.decode('utf-8'))
tcpCliSock.close() # close