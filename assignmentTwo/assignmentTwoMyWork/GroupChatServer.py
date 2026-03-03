# Written by: Simion Cartis

#TODO refactor code

#imports
from sys import *
from select import *
from socket import *

if len(argv) != 2:
    print('usage:', argv[0], '<port>')
    exit()

serverPort = int(argv[1])
serverSock = socket(AF_INET, SOCK_STREAM)
serverSock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
serverSock.bind(('', serverPort))
serverSock.listen()
serverSock.setblocking(False)

#create a list for the sockets
clients = {}

def cleanClients(clients, toRemove: list[socket]):
    for c in toRemove:
        clients.pop(c)

def readMessage(clients):
    readable, writable, exceptReady= select(([serverSock]+list(clients.keys())), list(clients.keys()), [])
    readable: list[socket]
    writable: list[socket]
    toRemove = []
    for r in readable:
        if r is serverSock:
            clientSock, clientAddr = serverSock.accept()
            clientSock.setblocking(False)
            print('client at address ', clientAddr, ' connected')
            clients[clientSock] = clientAddr
        else:
            sockFileIn = r.makefile(mode='r')
            line = sockFileIn.readline()
            if not line:
                print('client at ', clients.get(r), ' disconnected')
                toRemove.append(r)
            else:
                line = 'client at ' + str(clients.get(r)) + ' sent: '+ line
                for w in writable:
                    if w in toRemove or w is r:
                        continue
                    sockFileOut = w.makefile(mode='w')
                    sockFileOut.write(line)
                    sockFileOut.flush()
                    sockFileOut.close()
                    sockFileIn.close()
    cleanClients(clients, toRemove)

print('waiting for clients to connect...')
try:
    while True:
        readMessage(clients)
except KeyboardInterrupt:
    serverSock.close()
    for c in list(clients.keys()):
        sockFileOut = c.makefile(mode='w')
        sockFileOut.write(chr(26))
        sockFileOut.close()
        c.close()