import sqlite3
 
conn = sqlite3.connect('user.db')
c = conn.cursor()

def register(ip_address, username, password):
    c.excute('INSERT INTO user (ip_address, username, password, isOnline) VALUES (?, ?, ?, 1)',
        (ip_address,username, password,)
    )
    c.commit()   

def is_account_online(username):
    if c.execute('SELECT isOnline FROM user WHERE username = ?', (username,)).fetchone() is 1:
        return True
    else:
        return False

def is_account_exist(username):
    if c.execute('SELECT username FROM user WHERE username = ?', (username,)).fetchone() is not None:
        return True
    else:
        return False

def user_login(username):
    c.excute('INSERT INTO user(isOnline) VALUES (1) WHERE username = ?', (username,))
    c.commit() 

def user_logout(username):
    c.excute('INSERT INTO user(isOnline) VALUES (0) WHERE username = ?', (username,))
    c.commit() 

def get_online_ip():
    peer = c.execute('SELECT ip_address FROM user WHERE isOnline = 1').fetchall()
    return peer

def get_password(username):
    password = c.execute('SELECT password FROM user WHERE username = ?', (username,)).fetchone()
    return password
    