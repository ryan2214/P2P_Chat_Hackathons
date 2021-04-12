# coding:utf-8
 
from flask import Flask, render_template, request, redirect, url_for, make_response,jsonify,g,session
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

## init a database
## store userID table for online/offline discovery
#conn = sqlite3.connect('userIdDb.db')
s = requests.Session()
##
## Actually setup the Api resource routing here
##

@app.route('/', methods=['POST', 'GET'])
def index():
    if request.method == 'POST':
        f = request.form.get('username')
        session['username']=f
        return redirect(url_for('chat'))
    return render_template('main.html')

@app.route('/chat', methods=['POST', 'GET'])  # add upload route
def chat():
    if 'username' in session:
        username = session['username']
        f = request.form.get('username')

        return render_template('chat.html', username = username)
    return render_template('main.html')

    
if __name__ == '__main__':
    # app.debug = True
    app.run(host='0.0.0.0', port=80, debug=True)
