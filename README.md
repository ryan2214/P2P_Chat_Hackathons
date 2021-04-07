# P2P_Chat_Hackathons
Team 10
- Yuko Ishikawa
- Tianhe Lei
- Mella Liang

# Build instruction

go to the project folder, run "python p2p_chat.py" and visit 127.0.0.1:80 by your browser


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
