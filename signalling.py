import socket  
from threading import Thread
import sqlite3
 
conn = sqlite3.connect('user.db',check_same_thread=False)
c = conn.cursor()
ADDRESS = ('127.0.1.1', 5535)  # addr for binding
g_socket_server = None  # listening socket
g_conn_pool = {}  # dict storing connections
encode_type = 'utf-8'
MSG_SIZE = 1024

def init():
    """
    server init
    """
    global g_socket_server
    table_init()                                                         # prepare database table
    g_socket_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # init socket obj
    g_socket_server.bind(ADDRESS)
    g_socket_server.listen(5)  # max wait number
    print("server is on air, listening for connections...")

def accept_client():
    """
    receive new connections
    """
    while True:
        client, _ = g_socket_server.accept()  # stop, wait for connection
        # add to link pool
        #print(_)
        # for each client, setup independent thread
        client_ip = _[0]+":"+str(_[1])
        thread = Thread(target=message_handle, args=(client,client_ip,))
        # set as Daemon
        thread.setDaemon(True)
        thread.start()
 
 
def message_handle(client,userIP):
    """
    handle message from client
    """ 
    while True:
        bytes = ''
        try:
            bytes = client.recv(MSG_SIZE)
        except Exception:                        # connection error, exit
            client.close()
            # delete client
            del g_conn_pool[userID]
            db_user_logout(userID)
            print(userID, 'went offline.')
            break
        
        if len(bytes) == 0:                      # another connection error, exit
            client.close()
            # delete client
            del g_conn_pool[userID]
            db_user_logout(userID)
            print(userID, 'went offline.')
            break
        else:
            userID,ops = bytes.decode(encoding=encode_type).split(' ',1) 
                                                            # we assume further msg to server will be ID cmd
            print(userID, ops)                              # A invite B 
            # deal with client request
            if ops[0] == 'l' and ops[1] == 'o':             # we assume first msg is userID login                           
                g_conn_pool[userID] = client
                print(userID,userIP)
                db_user_login(userID,userIP)
                client.sendall("login done! You are online.".encode(encoding=encode_type))
            if ops[0] == 'i':
                target = ops.split(' ')[1]
                result = fetch_ip_by_ID(target)
                #print(result)
                #print(is_account_online(target))
                if result != -1 and is_account_online(target):          # found and online
                    #print(result)
                    res_msg = 'found '+result[0]
                    print('sending', res_msg,'to', userID)
                    client.sendall(res_msg.encode(encoding=encode_type))
                    # notice target about this invitation
                    t_tar = g_conn_pool[target]
                    inv_msg = 'invite '+userID+' '+userIP
                    print('sending', inv_msg,'to', target)
                    t_tar.sendall(inv_msg.encode(encoding=encode_type))
                    continue
                elif result != -1:                                      # found but offline
                    print('user',target,'not online')
                    client.sendall("not online".encode(encoding=encode_type))
                    continue
                else:                                                    # not found at all
                    print('user',target,'not found')
                    client.sendall("not found".encode(encoding=encode_type))
                    continue
            elif ops[0] == 'l':
                result = get_online_user()
                userline = 'ls '
                for t in result:
                    for u in t:
                        userline += u
                        userline += ' '
                client.sendall(userline.encode(encoding=encode_type))
                continue


def table_init():
    c.execute('''CREATE TABLE IF NOT EXISTS user 
       (userID       TEXT    NOT NULL,
       userIP        TEXT    NOT NULL,
       Status        INT     NOT NULL);''')   # 0 for offline, 1 for online
    conn.commit()

def is_account_online(userID):
    if is_account_exist(userID):
        status = c.execute('SELECT Status FROM user WHERE userID = ?', (userID,)).fetchone()
        if status[0] == 1:
            return True
        else:
            return False
    else:
        return False

def is_account_exist(userID):
    if c.execute('SELECT userID FROM user WHERE userID = ?', (userID,)).fetchone() != None:
        return True
    else:
        return False

def db_user_login(userID,userIP):
    if is_account_exist(userID):
        c.execute('UPDATE user set Status = 1 WHERE userID = ?', (userID,))
        c.execute('UPDATE user set userIP = ? WHERE userID = ?', (userIP,userID,))
        conn.commit()
    else:
        c.execute('INSERT INTO user (userID, userIP, Status) VALUES (?, ?, 1)',(userID,userIP,))
        conn.commit()

def db_user_logout(userID):
    if is_account_exist(userID):
        c.execute('UPDATE user set Status = 0 WHERE userID = ?', (userID,))
        conn.commit()

def fetch_ip_by_ID(userID):
    if is_account_exist(userID):
        userIP = c.execute('SELECT userIP FROM user WHERE userID = ?', (userID,)).fetchone()
        return userIP
    return -1

def get_online_user():
    peer = c.execute('SELECT userID FROM user WHERE Status = 1').fetchall()
    return peer

if __name__ == '__main__':
    init()
    # setup thread for listening
    thread = Thread(target=accept_client)
    thread.setDaemon(True)
    thread.start()
    # main cycle
    while True:
        cmd = input("""------------------------------------
Input ls: Check online client number
Input q: Close Server
------------------------------------\n""")
        if cmd == 'ls':
            print("------------------------------------")
            userline = ''
            for t in get_online_user():
                for u in t:
                    userline += u
                    userline += ' '
            print("now online: ", userline)

        elif cmd == 'q':
            exit()
