import socket
import time
import signal
import sqlite3
import threading
from threading import Thread, current_thread
import hashlib
import requests
from lxml import etree
import urllib

encode_type = 'utf-8'
MSG_SIZE = 1024
global is_exit,target_user,is_connected
is_connected = False
is_talking = False
user = ''
target_user = ''
target_ip = ''
target_port = 0
target_found = False
is_exit = False
conn = sqlite3.connect('temp.db')
c = conn.cursor()

# hardcode user ip 
client = ['127.0.0.2','127.0.0.3']
server_ip = '127.0.1.1'
server_port = 5535
client_port = 5500
port_to_server = 5501
temp_port = 5502

def get_outer_ip():
    url = 'http://tool.chinaz.com/'
    res = requests.get(url=url)
    html = etree.HTML(res.text)
    _ip = html.xpath('/html/body/div[2]/div/div[1]/a[2]')[0].text  # check element, copy Xpath
    #print(_ip)
    _ip = str(_ip).split(" ")[0]
    return _ip

def socket_listen(ts, MAX_CONNECTIONS=5):
    """
    receive new connections
    """
    global is_connected,target_port
    ts.listen(MAX_CONNECTIONS)
    
    print('waiting for', target_user, 'to accept...')
    client, _ = ts.accept()  # stop, wait for connection
    # add to link pool
    #print(_)
    if target_port > 0 :
        print('socket accepted from',_)
        is_connected = True
        show_msg_history(target_user)
        send_unsent_msg(client)
        # for each client, setup independent thread
        send_thread = Thread(target=socket_send_msg, args=(client, ))
        receive_thread = Thread(target=socket_receive_msg, args=(client,))
        # set as Daemon
        receive_thread.setDaemon(True)
        receive_thread.start()
        send_thread.start()
        send_thread.join()

def socket_connect(ts):
    global is_connected,target_user
    ADDR = (target_ip, client_port)
    try:
        is_connected = not ts.connect(ADDR) # on success, connect() return 0
    except Exception:
        print(target_user, 'is offline now, try next time.')
    if is_connected:
        print('connected to',target_user)
        show_msg_history(target_user)
        send_unsent_msg(ts)
        send_msg_thread = Thread(target=socket_send_msg, args=(ts, ))
        receive_msg_thread = Thread(target=socket_receive_msg, args=(ts, ))

        receive_msg_thread.setDaemon(True)
        send_msg_thread.start()
        receive_msg_thread.start()
        send_msg_thread.join()

def socket_send_msg(ts):       # send msg to peer
    msg = None
    global is_exit,user,target_user,is_talking
    
    while msg!='/exit' and not is_exit and is_talking:
        msg = input().strip()
        time_stamp = get_time_stamp()
        msg_assmbly = msg+' '+time_stamp
        try:
            ts.send(msg_assmbly.encode(encode_type))
        except Exception:
            print('msg cannot reach',target_user,'for now.')
            is_exit = True
        is_sent = int(not is_exit)
        write_msg_to_db(user, target_user, 1, time_stamp, is_sent, msg) # update msg sent or not sent to local db
    is_exit = True

def recieve_server_msg(s):             # receive msg from server, parse and get reply info
    global is_exit,user,target_ip,target_port,target_found,target_user

    while not is_exit:
        try:
            msg = s.recv(MSG_SIZE).decode(encoding=encode_type)
        except Exception:
            print('server goes offline.')
            is_exit = True
            break
        if len(msg) == 0:                      # connection error, exit
            s.close()
            print('server goes offline.')
            break
        msg_elements = msg.split(' ')
        if msg_elements[0] == 'ls':                                     # online list got
            print("now online: ", msg.split(' ',1)[1])
        elif msg_elements[0] == 'found':                                # target found and online
            target_ip = msg_elements[1].split(':',1)[0]
            target_port = int(msg_elements[1].split(':',1)[1])
            target_found = True
        elif msg_elements[0] == 'not' and msg_elements[1] == 'online':  # target not online
            target_port = -1
        elif msg_elements[0] == 'not' and msg_elements[1] == 'found':   # target not found in db
            target_port = -2
        elif msg_elements[0] == 'invite':                     # chat invite from target user with ip:port
            target_user = msg_elements[1]
            target_ip = msg_elements[2].split(':',1)[0]
            target_port = int(msg_elements[2].split(':',1)[1])
            print('receive invitation from',target_user,'accept?(y/n)')
        elif msg_elements[0] == 'refused':                     # chat invite from target user with ip:port
            target_port = -1
            temps = socket.socket(socket.AF_INET, socket.SOCK_STREAM)     # socket between peer
            temps.bind((myip,temp_port))
            
def socket_receive_msg(chat_socket):      # receive msg from peer in chat
    global target_user,is_exit
    while not is_exit and is_talking:
        msg = ''
        raw_msg = ''
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

def send_unsent_msg(ts):                                     # send unsent msg at the beginning of a chat
    unsent_msg = find_unsent_msg_about_target(target_user)   # better late than never
    for m in unsent_msg:
        msg = m[1]
        time_stamp = m[2]
        msg_assmbly = msg+' '+time_stamp
        ts.send(msg_assmbly.encode(encode_type))
    mark_msg_sent()

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
            

def get_time_stamp():           # get the time now
    now = int(time.time())
    timeArray = time.localtime(now)
    mytime = time.strftime("%Y/%m/%d-%H:%M:%S", timeArray)
    
    return mytime

def init_msg_table():           # init table if this is the first time, or db does not exist
    global c,conn
    c.execute("create table if not exists msg(fromID text not null,toID text not null,dir text not null,sendTime text not null,isShipped int not null,content text not null)")
    conn.commit()   

def del_msg_table():            # not used
    global c,conn
    c.execute("drop table msg")
    conn.commit() 

def insert_one_msg(fromID, toID, dir, sendTime, isShipped, content):
    global c,conn
    c.execute('INSERT INTO msg(fromID,toID,dir,sendTime,isShipped,content) VALUES (?, ?, ?, ?, ?, ?)',
        (fromID, toID, dir, sendTime, isShipped, content)
    )
    conn.commit()

def find_msg_about_target(target_username):        # return target related msg for showing chat history
    global c
    result = c.execute('select fromID,content,sendTime from msg where (fromID=? or toID = ?)',
         (target_username,target_username)).fetchall()
    return result

def find_unsent_msg_about_target(target_username):     # return target related unsent msg for sending them
    global c
    result = c.execute('select fromID,content,sendTime from msg where (toID=? and isShipped = ?)',
         (target_username,0)).fetchall()
    return result

def mark_msg_sent():                                # after sending unsent msg, mark them all as sent
    global c
    c.execute('UPDATE msg SET isShipped = ? WHERE isShipped = ?;',(1,0))

def debug():                                        # print some debug info
    print('is_connected=',is_connected)
    print('is_talking=',is_talking)
    print('user=',user)
    print('target_user=',target_user)
    print('target_ip=',target_ip)
    print('target_port=',target_port)
    print('target_found=',target_found)
    print('is_exit=',is_exit)

if __name__ == "__main__":
    signal.signal(signal.SIGINT, sig_handler)
    signal.signal(signal.SIGTERM, sig_handler)

    # fetch user IP for people without VPN, going to need this if not in the localhost test
    #external_ip = urllib.request.urlopen('https://ident.me').read().decode('utf8')
    #print('IP for user out of China:',external_ip)
    #print('IP for user in China:',get_outer_ip())
    #global target_user,user,is_connected,conn,c

    user = input('Enter your user name: ').strip()
    myip_index = input('Which ip to use(0 or 1)?')
    myip = client[int(myip_index)]
    ADDR = (myip,port_to_server)
    
    try:                                                       # s connecting server, login and build connection
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind(ADDR)
        s.connect((server_ip,server_port))
        login_msg = user+' login'
        s.sendall(login_msg.encode(encode_type))
        print(s.recv(1024).decode(encoding=encode_type))
    except Exception:
        print('cannot reach server now.')

    # db init (need username for index)
    user_name_hash = hashlib.md5(user.encode()).hexdigest()
    conn = sqlite3.connect(user_name_hash+'.db',check_same_thread=False)
    c = conn.cursor()
    init_msg_table()

    t=threading.Thread(target=recieve_server_msg,args=(s,))   # get ready for further server reply from socket s
    t.setDaemon(True)
    t.start()

    ts = socket.socket(socket.AF_INET, socket.SOCK_STREAM)     # socket between peer
    ts.bind((myip,client_port))

    while True and not is_talking:             # when talk starts, cycle ends to avoid input conflicts
        cmd = input("""------------------------------------
Input ls: list online users
Input t: Talk to someone
Input e: Exit
------------------------------------\n""")
        if cmd == 'ls':                                     # list online user (not accurate)
            l_msg = user+' list'
            s.send(l_msg.encode(encode_type))
        elif cmd == 't':                                   # want a talk
            print("------------------------------------")
            target_found = False
            target_port = 0
            target_user = input('Who would you talk to (user ID)? ').strip()   # choose chat target
            i_msg = user+' invite '+target_user
            s.send(i_msg.encode(encode_type))
            while not target_found:                         # waiting for server reply
                if target_port == -1:
                    print('user not found.')
                    break
                time.sleep(1)
            if target_port == -1:
                print('user not online now, try next time. leave some msg and quit by input /exit')
                continue               # go back to main menu
            if target_port == -2:
                print('user not found in registeration log.')
                continue               # go back to main menu
            # now the target ip and port found
            #print(target_user,target_ip,target_port)
            # finally, build connection between peers
            is_talking = True
            r_thread = Thread(target=socket_listen,args=(ts,))
            r_thread.start()
            r_thread.join()            # this is the end of program, maybe find a way to do some loop

        elif cmd == 'y':                # connection confirmed
                                        # start connecting to target
            if target_port > 0:         # check if ready for connection
                print('connecting')
                is_talking = True
                c_thread = Thread(target=socket_connect,args=(ts,))
                c_thread.start()
                c_thread.join()         # this is the end of program, maybe find a way to do some loop     
            else:
                print('not this time!')
        elif cmd == 'n':    
            if target_port >0:
                n_msg = user+' refuse '+target_user
                s.send(n_msg.encode(encode_type))
            else:
                print('do not input this!')
        elif cmd == 'd':
            debug()
        elif cmd == 'e':
            exit()
