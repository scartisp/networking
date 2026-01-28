# These instructions are for running OneWayMesg application written in c for Windows 11 with Visual Studio Developer Command Prompt

Install Visual Studio 2022, and make sure Developer option with C++ is enabled.

Open two Developer Command Prompt for VS 2022

# Compile the server and client programs
% cl OneWayMesgServer_Win.c
% cl OneWayMesgClient_Win.c

# First, run the server with a port number (say 50000) in one command prompt
% OneWayMesgServer_Win.exe 50000

# Then, run the client with the server's whereabouts in another command prompt
% OneWayMesgClient_Win.exe localhost 50000

# Type messages at the client and see them displayed at the server

# To end the client, type Ctrl-D (on Windows Ctrl-Z followed by return)
# This is referred to as EOF (end of file), meaning end of input
# Then, the server will also quit saying client closed the connection
