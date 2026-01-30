# Written by: Simion Cartis

#imports for socket
from socket import *
#imports for argv related methods
from sys import *

# error message if arguments are incorrect
if len(argv) != 3:
    print("usage:", argv[0], "<server name> <server port>")
    exit()

# Get server's whereabouts
serverName = argv[1]
serverPort = int(argv[2])

#creates a socket
clientSock = socket(AF_INET, SOCK_STREAM)

# Connect to the server
clientSock.connect((serverName, serverPort))
print(f"Connected to server at ('{serverName}', '{serverPort}')")

# Make a file stream out for client socket
serverSockFileIn = clientSock.makefile(mode="r")
# make file stream in for client socket THIS IS CURRENTLY NOT BEING USED
serverSockFileOut = clientSock.makefile(mode="w")

while True:
    # Send the line to server
    toServer = stdin.readline()
    serverSockFileOut.write(toServer)
    serverSockFileOut.flush()
    # if client sends nothing (inputted EOF char)==> client closed the connection
    if not toServer:
        print('Client closed connection')
        break
    # Read a message from the client
    message = serverSockFileIn.readline()
    # If no message ==> client closed the connection
    if not message:
        print('Server closed connection')
        break
    # Display the line
    print('Server:', message, end='')

# done
serverSockFileIn.close()
serverSockFileOut.close()
clientSock.close()
# print("Closing connection")