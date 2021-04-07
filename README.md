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
git push heroku [current branch]:main
```

![preview_0](https://github.com/ryan2214/P2P_Chat_Hackathons/blob/main/pics/preview_0.png?raw=true)


# Suggested Roles:

## User:

Socket: send msg by IP to other peers,

Flask Web Application: Interface for chat, (multiple user), show recent chat, access to chat history.

Web SQL: Store chat content locally, impl by js.

          message table: fromID, toID, direction, isShipped, timeStamp,  content
          
          peer table: peerID, peerAddr

![preview_1](https://github.com/ryan2214/P2P_Chat_Hackathons/blob/main/pics/preview_1.png?raw=true)

## Server:

Socket: Receive online(/offline) status sent by users, notify interesting users on receive online "hello". (update offline by onunload?)

SQL Lite: Keep track of all the users status (online/offline).
   
          peer table: peerID, peerAddr, isOnline, (interestPeerList)*
          
          *(interestPeerList means all the peers called this peer during offline, store their peerID in this list. Could SQL store list as parameter?)
