# P2P_Chat_Hackathons
Team 10
- Yuko Ishikawa
- Tianhe Lei
- Mella Liang

# Initial Setup 
```
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```
### To save imports
- After you install something, update list of imports:
```
pip freeze > requirements.txt
```
# Build instruction
Make sure you are in the project folder
```
source venv/bin/activate
python3 p2p_chat.py
```
Then visit 127.0.0.1:80 in your browser

# Website
https://p2p-chat-ec500.herokuapp.com/
- To push to heroku:
- (create a Heroku account, tell me the email you used to register, and I'll add you as a collaborator so you could update the website)
```
git add .
git commit -m "[details of commit]"
git push origin [current branch]
git push heroku [current branch]:main
```

![preview_0](https://github.com/ryan2214/P2P_Chat_Hackathons/blob/main/pics/preview_0.png?raw=true)


# Suggested Roles:

## User: console_client.py

Socket: send and receive msg by IP to server and other peers.

Python Console Application: Interface for chat, show online user, access to chat history in connection setup, send messaage.

SQLite3: Store chat content locally, impl by sqlite3.

          msg table: fromID text, toID text,dir text(0:in,1:out), sendTime text,isShipped int(0:not,1:yes),content text


## Server: signalling.py

Socket: Receive online status sent by users, turn the user offline when connection to the user ends, notify invited users on receive invitation from user.

SQL Lite: Keep track of all the users status (online/offline).
   
          user table: userID TEXT, userIP TEXT, Status INT(1:online,0:offline)

