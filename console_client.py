import socket
import time
import signal
import sqlite3
import threading
from threading import Thread, current_thread
import hashlib

encode_type = 'utf-8'
MSG_SIZE = 1024
global is_exit,user,target_user,is_connected,conn,c,raw_msg
is_server_connected = False
is_connected = False
user = ''
target_user = ''
raw_msg = ''
is_exit = False

conn = sqlite3.connect('temp.db')
c = conn.cursor()

# hardcode user info 
# TODO: replaced by sqlite3 ops
client = {"A":'127.0.0.2',"B":'127.0.0.3'}
server_ip = '127.0.1.1'
server_port = 5535
# one lock per chat per user
# chat_lock = threading.Lock()


# turn into class later
def initialize_socket():
    global target_user,user,is_connected,conn,c
    # HOST = '127.0.1.1'
    user = input('Enter your user name(A/B): ').strip()
    HOST = client[user]
    PORT = 21566
    ADDR = (HOST, PORT)

    # db init
    user_name_hash = hashlib.md5(user.encode()).hexdigest()
    conn = sqlite3.connect(user_name_hash+'.db',check_same_thread=False)
    c = conn.cursor()
    init_msg_table()

    tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tcp_socket.bind(ADDR)
    connect_to_server(tcp_socket, PORT)
    tcp_socket.close()
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
    global is_exit,target_user
    listen_socket.listen(MAX_CONNECTIONS)
    print('Listening...')

    while not is_exit:
        chat_socket, friend_addr = listen_socket.accept()
        print('Connected to host', friend_addr)
        show_msg_history(target_user)
        send_msg_thread = Thread(target=socket_send_msg, args=(chat_socket, ))
        receive_msg_thread = Thread(
            target=socket_receive_msg, args=(chat_socket, ))

        receive_msg_thread.setDaemon(True)

        send_msg_thread.start()
        receive_msg_thread.start()

        send_msg_thread.join()


def connect_to_server(chat_socket, PORT):
        global is_server_connected,is_exit
        ADDR = (server_ip, server_port)
        #chat_socket.connect(ADDR)
        try:
            is_server_connected = not chat_socket.connect(ADDR) # on success, connect() return 0
        except Exception:
            print('server is offline now.')
        if is_server_connected:
            print('connected to server')

        if is_server_connected and not is_exit:
            # tell the server the user is online, by userID
            # TODO: ask if target of local unsent msg is online
            send_msg_thread = Thread(target=socket_send_login, args=(chat_socket, ))

            send_msg_thread.start()
            send_msg_thread.join()

def socket_connect(chat_socket, PORT):
        global is_connected,target_user,is_exit
        friend_ip = client[target_user]
        ADDR = (friend_ip, PORT)

        try:
            is_connected = not chat_socket.connect(ADDR) # on success, connect() return 0
        except Exception:
            print(target_user, 'is offline now, prepare to listen.')
        if is_connected:
            print('connected to',target_user)
            show_msg_history(target_user)
        while is_connected and not is_exit:
            send_msg_thread = Thread(target=socket_send_msg, args=(chat_socket, ))
            receive_msg_thread = Thread(
                target=socket_receive_msg, args=(chat_socket, ))

            receive_msg_thread.setDaemon(True)

            send_msg_thread.start()
            receive_msg_thread.start()

            send_msg_thread.join()

def socket_send_login(chat_socket):
    global user
    is_sent = False
    msg = 'login '+user+' '+get_time_stamp()
    print(msg)
    try:
        chat_socket.send(msg.encode(encode_type))
        is_sent = True
    except Exception:
        print('msg cannot reach',target_user,'for now.')
        is_sent = False
    if is_sent:
        print('login success')

def socket_send_msg(chat_socket):
    msg = None
    global is_exit,user,target_user
    
    while msg!='/exit' and not is_exit:
        msg = input().strip()
        time_stamp = get_time_stamp()
        msg_assmbly = msg+' '+time_stamp
        try:
            chat_socket.send(msg_assmbly.encode(encode_type))
        except Exception:
            print('msg cannot reach',target_user,'for now.')
            is_exit = True
        is_sent = int(not is_exit)
        write_msg_to_db(user, target_user, 1, time_stamp, is_sent, msg) # update msg sent or not sent to local db
    is_exit = True


# figure out how to end
def socket_receive_msg(chat_socket):
    global target_user,is_exit,raw_msg
    while not is_exit:
        msg = ''
        try:
            msg = chat_socket.recv(MSG_SIZE)
        except Exception:
            print(target_user,'goes offline.')
            is_exit = True
        if msg:
            raw_msg = msg.decode(encode_type)
        if msg and raw_msg.rsplit(' ',1)[0]!='/exit' and not is_exit :
            print(target_user,'>', raw_msg)
            time_stamp = raw_msg.rsplit(' ',1)[1]

            write_msg_to_db(target_user, user, 0, time_stamp, 1, raw_msg.rsplit(' ',1)[0])

def sig_handler(signum, frame):
    global is_exit
    is_exit = True

def write_msg_to_db(fromID, toID, dir, sendTime, isShipped, content):
    if content[0]!='/':
        insert_one_msg(fromID, toID, dir, sendTime, isShipped, content)

def show_msg_history(target):
    chat = find_msg_about_target(target)
    for m in chat:
        if m:
            #print(m[1])
            if m[0] == user:
                print(m[1],'\t',m[2])
            else:
                content = m[0] + ' >'
                print(content,m[1],'\t',m[2])
    
    print('-------------history-------------')


            

def get_time_stamp():
    now = int(time.time())
    timeArray = time.localtime(now)
    mytime = time.strftime("%Y/%m/%d-%H:%M:%S", timeArray)
    
    return mytime

def init_msg_table():
    global c,conn
    c.execute("create table if not exists msg(fromID text not null,toID text not null,dir text not null,sendTime text not null,isShipped int not null,content text not null)")
    conn.commit()   

def del_msg_table():
    global c,conn
    c.execute("drop table msg")
    conn.commit() 

def insert_one_msg(fromID, toID, dir, sendTime, isShipped, content):
    global c,conn
    c.execute('INSERT INTO msg(fromID,toID,dir,sendTime,isShipped,content) VALUES (?, ?, ?, ?, ?, ?)',
        (fromID, toID, dir, sendTime, isShipped, content)
    )
    conn.commit()

def find_msg_about_target(target_username):
    global c
    result = c.execute('select fromID,content,sendTime from msg where (fromID=? or toID = ?)',
         (target_username,target_username)).fetchall()
    return result

if __name__ == "__main__":
    signal.signal(signal.SIGINT, sig_handler)
    signal.signal(signal.SIGTERM, sig_handler)
    
    initialize_socket()
