# Written by: Simion Cartis

#imports for socket
from socket import *
#imports for argv related methods
from sys import *

# message if arguments are incorrect
if len(argv) != 2:
    print('usage:', argv[0], '<port>')
    exit()

# Get the port on which server should listen */
serverPort = int(argv[1])

# Create the server socket
serverSock = socket(AF_INET, SOCK_STREAM)

# Bind the socket to the given port
serverSock.bind(('', serverPort))

# Set the server for listening
serverSock.listen()

# Wait to receive a connection request
print('Waiting for a client ...')
clientSock, clientAddr = serverSock.accept()
print('Connected to a client at', clientAddr)

# No other clients, close the server socket
serverSock.close()

# Make a file stream out for client socket
clientSockFileIn = clientSock.makefile(mode="r")
# make file stream in for client socket
clientSockFileOut = clientSock.makefile(mode="w")

while True:
    # Read a message from the client
    message = clientSockFileIn.readline()
    # If no message ==> client closed the connection
    if not message:
        print('Client closed connection')
        clientSockFileIn.close()
        clientSockFileOut.close()
        clientSock.close()
        break
    # Display the line
    print('Client:', message, end='')
    
    toClient = stdin.readline()
    clientSockFileOut.write(toClient)
    clientSockFileOut.flush()

    if not toClient:
        print('Server closed connection')
        clientSockFileIn.close()
        clientSockFileOut.close()
        clientSock.close()
        break