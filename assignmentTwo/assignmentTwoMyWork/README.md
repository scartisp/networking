# Instruction for running my TCP group chat application written in Python

## Execute the server program by inputting the following command in your terminal
% python GroupChatServer.py 50000

## To create a client that connects to the server, open another terminal and input the following command
%  python GroupChatClient.py localhost 50000
% to kill a client, input ctrl+z (EOF) into the client's terminal. This will disconnect the client from the server

% to kill the server along with all clients connected, input ctrl+c into the server terminal