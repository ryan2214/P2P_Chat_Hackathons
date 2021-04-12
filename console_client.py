import socket
import time
import sys
import os
import signal
import threading
from threading import Thread, current_thread

encode_type = 'utf-8'
MSG_SIZE = 1024
global is_exit,target_user,is_connected

is_connected = False
target_user = ''
is_exit = False

# hardcode user info 
# TODO: replaced by sqlite3 ops
client = {"A":'127.0.0.2',"B":'127.0.0.3'}

# one lock per chat per user
# chat_lock = threading.Lock()


# turn into class later
def initialize_socket():
    # HOST = '127.0.1.1'
    HOST = client[input('Enter your user name(A/B): ').strip()]
    PORT = 21566
    ADDR = (HOST, PORT)
    MAX_CONNECTIONS = 50
    global target_user
    global is_connected
    tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tcp_socket.bind(ADDR)

    target_user = input('Who would you talk to (A/B)? ').strip()

    listen_thread = Thread(target=socket_listen, args=(tcp_socket, ))
    connect_thread = Thread(target=socket_connect, args=(tcp_socket, PORT, ))

    connect_thread.start()
    connect_thread.join()
    
    if not is_connected:
        listen_thread.start()
        listen_thread.join()

        


def socket_listen(listen_socket, MAX_CONNECTIONS=50):
    listen_socket.listen(MAX_CONNECTIONS)
    print('Listening...')

    while True:
        chat_socket, friend_addr = listen_socket.accept()
        print('Connected to host', friend_addr)

        send_msg_thread = Thread(target=socket_send_msg, args=(chat_socket, ))
        receive_msg_thread = Thread(
            target=socket_receive_msg, args=(chat_socket, ))

        receive_msg_thread.daemon = True

        send_msg_thread.start()
        receive_msg_thread.start()

        send_msg_thread.join()



def socket_connect(chat_socket, PORT):
        global is_connected,target_user
        friend_ip = client[target_user]
        ADDR = (friend_ip, PORT)

        try:
            is_connected = not chat_socket.connect(ADDR) # on success, connect() return 0
        except Exception:
            print(target_user, 'is offline now, prepare to listen.')
        if is_connected:
            print('connected to ',target_user)
        
        while is_connected and not is_exit:
            send_msg_thread = Thread(target=socket_send_msg, args=(chat_socket, ))
            receive_msg_thread = Thread(
                target=socket_receive_msg, args=(chat_socket, ))

            receive_msg_thread.setDaemon(True)

            send_msg_thread.start()
            receive_msg_thread.start()

            send_msg_thread.join()

def socket_send_msg(chat_socket):
    msg = None

    while msg != '/exit':
        msg = input().strip()
        chat_socket.send(msg.encode(encode_type))

    sys.exit()


# figure out how to end
def socket_receive_msg(chat_socket):
    while not is_exit:
        msg = chat_socket.recv(MSG_SIZE)
        if msg:
            print('>', msg.decode(encode_type))

def sig_handler(signum, frame):
    global is_exit
    is_exit = True

if __name__ == "__main__":
    signal.signal(signal.SIGINT, sig_handler)
    signal.signal(signal.SIGTERM, sig_handler)
    initialize_socket()

