from socket import *
import threading
import select
import db

encode_type = 'utf-8'
MSG_SIZE = 1024

class ClientThread(threading.Thread):
    def __init__(self, ip, port, tcpClientSocket):
        threading.Thread.__init__(self)
        self.tcpClientSocket = tcpClientSocket
    
    def run(self):
        self.lock = threading.Lock()
        
        while True:
            message = self.tcpClientSocket.recv(MSG_SIZE).decode().split()

            if message[0] == "register":
                if db.is_account_exist(message[2]):
                    response = "exist"
                else:
                    db.register(message[1], message[2], message[3])
                    response = "success"
                self.tcpClientSocket.send(response.encode())
            
            elif response[0] == "login":
                if not db.is_account_exist(message[1]):
                    response = "not_exist"
                elif db.get_password(message[1]) != message[2]:
                    response = "invalid_password"
                else:
                    db.user_login(message[1])
                    response = "success"
                self.tcpClientSocket.send(response.encode())

            elif response[0] == "search":
                if db.is_account_exist(message[1]):
                    if db.is_account_online(message[1]):
                        ip_address = db.get_peer_ip_port(message[1])
                        response = "success" + ' ' + ip_address
                    else:
                        response = "offline"
                else:
                    response = "not_found"
                self.tcpClientSocket.send(response.encode())
            
            elif response[0] == "list":
                response = db.get_online_ip()
                self.tcpClientSocket.send(response.encode())
            
            elif response[0] == "logout":
                db.user_logout(message[1])
                self.tcpClientSocket.close()
                break

if __name__ == "__main__":
    port = 5535        ## temporary
    host = "127.0.1.1" ## temporary

    print("Signaling Sever started!")
    print("Signaling Server IP address: " + host)
    print("Signaling Server port number: " + str(port))

    tcpSocket = socket(AF_INET, SOCK_STREAM)
    tcpSocket.bind((host,port))
    tcpSocket.listen(10)
    input = [tcpSocket]

    while input:
        print("Listening...")
        readable, writable, exceptional = select.select(input, [], [])
        for s in readable:
            if s == tcpSocket:
                tcpClientSocket, addr = tcpSocket.accept()
                newThread = ClientThread(addr[0], addr[1], tcpClientSocket)
                newThread.start()
    tcpSocket.close()