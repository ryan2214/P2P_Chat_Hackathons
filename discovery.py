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

    def register():
        username = self.tcpClientSocket.recv(MSG_SIZE).decode()
        if db.is_account_exist(username):
            response = "exist"
            self.tcpClientSocket.send(response.encode())
                    
        else:
            password = self.tcpClientSocket.recv(MSG_SIZE).decode()
            ip_address = self.tcpClientSocket.recv(MSG_SIZE).decode()
            db.register(username, password, ip_address)
            response = "success"
            self.tcpClientSocket.send(response.encode())

    def login():
        username = self.tcpClientSocket.recv(MSG_SIZE).decode()
        password = self.tcpClientSocket.recv(MSG_SIZE).decode()
        if not db.is_account_exist(username):
            response = "not_exist"
            self.tcpClientSocket.send(response.encode())
        elif db.get_password(username) != password:
            response = "invalid_password"
            self.tcpClientSocket.send(response.encode())
        else:
            db.user_login(message[1], self.ip, message[3])
            response = "success"
            self.tcpClientSocket.send(response.encode())
    
    def search():
        username = self.tcpClientSocket.recv(MSG_SIZE).decode()
        if db.is_account_exist(username):
            if db.is_account_online(username):
                ip_address = db.get_peer_ip_port(username)
                response = "success"
                self.tcpClientSocket.send(response.encode())
                self.tcpClientSocket.send(ip_address.encode())
            else:
                response = "offline"
                self.tcpClientSocket.send(response.encode())
        else:
            response = "not_found"
            self.tcpClientSocket.send(response.encode())

    def list_peers():
        response = db.get_online_ip()
        self.tcpClientSocket.send(response.encode())

    def logout():
        username = self.tcpClientSocket.recv(MSG_SIZE).decode()
        db.user_logout(message[1])
        self.tcpClientSocket.close()

    def run(self):
        self.lock = threading.Lock()
        while True:
            request = self.tcpClientSocket.recv(MSG_SIZE).decode()
            if request == "register":
               register()
            elif request == "login":
                login()
            elif request == "search":
                search()
            elif request == "list":
                list_peers()
            elif request == "logout":
                logout()
                break

port = 5535 ## temporary
host = "127.0.1.1" ## temporary
print("Centeralized Sever started")
print("Cantralized Server IP address: " + host)
print("Cantralized Server port number: " + port)

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