# P2P_Chat_Hackathons
Team 10
- Yuko Ishikawa
- Tianhe Lei
- Mella Liang


# Suggested Roles:

## User:

Socket: send msg by IP to other peers,

Flask Web Application: Interface for chat, (multiple user), show recent chat, access to chat history.

Web SQL: Store chat content locally, impl by js.

          message table: fromID, toID, direction, isShipped, timeStamp,  content
          
          peer table: peerID, peerAddr

## Server:

Socket: Receive online(/offline) status sent by users, notify interesting users on receive online "hello". (update offline by onunload?)

SQL Lite: Keep track of all the users status (online/offline).
   
          peer table: peerID, peerAddr, isOnline, (interestPeerList)*
          
          *(interestPeerList means all the peers called this peer during offline, store their peerID in this list. Could SQL store list as parameter?)
