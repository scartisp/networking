# Written by: Simion Cartis

#TODO REFACTOR THIS CODE, AND COMMENT IT. FOR THE LOOOOOVE OF GOD (AHHHHHHHHHHHHHHHH)

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
    readable, writable, _= select(([serverSock]+list(clients.keys())), list(clients.keys()), [], 1)
    readable: list[socket]
    writable: list[socket]
    toRemove = []
    for r in readable:
        if r is serverSock:
            clientSock, clientAddr = serverSock.accept()
            rSock = clientSock.makefile(mode='r')
            wSock = clientSock.makefile(mode='w')
            clientSock.setblocking(False)
            print('client at address ', clientAddr, ' connected')
            clients[clientSock] = {'addr': clientAddr, 'rSock': rSock, 'wSock': wSock}
        else:
            #sockFileIn = r.makefile(mode='r')
            rInfo = clients.get(r)
            rSock = rInfo['rSock']
            line = rSock.readline()
            if not line:
                print('client at ', rInfo['addr'], ' disconnected')
                rSock.close()
                rInfo['wSock'].close()
                r.close()
                toRemove.append(r)
            else:
                line = 'client at ' + str(rInfo['addr']) + ' sent: '+ line
                for w in writable:
                    if w in toRemove or w is r:
                        continue
                    wInfo = clients.get(w)
                    wSock = wInfo['wSock']
                    #sockFileOut = w.makefile(mode='w')
                    wSock.write(line)
                    wSock.flush()
                 #   wSock.close()
                #rSock.close()
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
        clients.get(c)['rSock'].close()
        clients.get(c)['wSock'].close()
        c.close()