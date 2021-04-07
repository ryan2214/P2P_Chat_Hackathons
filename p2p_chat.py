# coding:utf-8

from flask import Flask, render_template, request, redirect, url_for, make_response, jsonify, g, session
from flask_restful import reqparse, abort, Api, Resource
from pathlib import Path
import json
import logging
import os
import socket
import sys
import time
import sqlite3
import requests
import config

from datetime import timedelta

app = Flask(__name__)
api = Api(app)
app.config['SECRET_KEY'] = os.urandom(24)

# init a database
# store userID table for online/offline discovery
conn = sqlite3.connect('userIdDb.db')
s = requests.Session()
##
# Actually setup the Api resource routing here
##


@app.route('/', methods=['POST', 'GET'])
def index():
    if request.method == 'POST':
        f = request.form.get('username')
        session['username'] = f
        return redirect(url_for('chat'))
    return render_template('main.html')


@app.route('/chat', methods=['POST', 'GET'])  # add upload route
def chat():
    if 'username' in session:
        username = session['username']
        f = request.form.get('username')

        return render_template('chat.html', username=username)
    return render_template('main.html')


@app.route('/p2p', methods=['GET'])
def p2p():
    socket_server = socket.socket()
    server_host = socket.gethostname()
    ip = socket.gethostbyname(server_host)

    friend_ip = '172.18.131.90'
    chat_port = 8083
    socket_server.connect((friend_ip, chat_port))

    print('socket server', socket_server, 'host', server_host, 'ip', ip)

    return 'Your ip address is ' + ip


@app.route('/socket-chat', methods=['GET'])
def socket_chat():
    import time, socket, sys
 
    socket_server = socket.socket()
    server_host = socket.gethostname()
    ip = socket.gethostbyname(server_host)
    sport = 8080
    
    print('This is your IP address: ',ip)
    server_host = input('Enter friend\'s IP address:')
    name = input('Enter Friend\'s name: ')
    
    
    socket_server.connect((server_host, sport))
    
    socket_server.send(name.encode())
    server_name = socket_server.recv(1024)
    server_name = server_name.decode()
    
    print(server_name,' has joined...')
    while True:
        message = (socket_server.recv(1024)).decode()
        print(server_name, ":", message)
        message = input("Me : ")
        socket_server.send(message.encode())  


if __name__ == '__main__':
    # app.run(host='0.0.0.0', port=80, debug=True)
    app.run(debug=True)
