# Written by: Simion Cartis

#imports
from sys import *
from select import *
from socket import *

if len(argv) != 2:
    print('usage:', argv[0], '<port>')
    exit()

serverPort = int(argv[1])
serverSock = socket(AF_INET, SOCK_STREAM)
serverSock.bind(('', serverPort))
serverSock.listen()
serverSock.setblocking(False)

#create a list for the sockets
clients = {}

def serveClients(clients): #blocks for one second, if nothing is readable or writeable, unblocks
    readable, writable, _= select(([serverSock]+list(clients.keys())), list(clients.keys()), [], 1)
    readable: list[socket]
    writable: list[socket]
    toRemove = []
    for r in readable:
        if r is serverSock: # if the serverSock is readable, that means a client is trying to connect
            clientSock, clientAddr = serverSock.accept()
            rSock = clientSock.makefile(mode='r')
            wSock = clientSock.makefile(mode='w')
            clientSock.setblocking(False)
            print('client at address ', clientAddr, ' connected')
            clients[clientSock] = {'addr': clientAddr, 'rSock': rSock, 'wSock': wSock}
        else:
            rInfo = clients.get(r) #unpack everything from the inner dict
            rSock = rInfo['rSock']
            line = rSock.readline()
            if not line: # if receive EOF, close all sockets and obj related to client, remove from client dict
                print('client at ', rInfo['addr'], ' disconnected')
                rSock.close()
                rInfo['wSock'].close()
                r.close()
                clients.pop(r)
            else:
                line = 'client at ' + str(rInfo['addr']) + ' sent: '+ line
                for w in writable:
                    if w is r: #client shouldn't write to themself 
                        continue
                    wInfo = clients.get(w)
                    wSock = wInfo['wSock']
                    wSock.write(line) #write client input to all othe clients
                    wSock.flush()

print('waiting for clients to connect...')
try:
    while True: #continously run the serveClient function, except for on keyboard interrupt (ctrl+c)
        serveClients(clients)
except KeyboardInterrupt:
    serverSock.close() # on interrupt, kill all socket and socket related objects
    for c in list(clients.keys()):
        sockFileOut = c.makefile(mode='w')
        sockFileOut.write(chr(26))
        sockFileOut.close()
        clients.get(c)['rSock'].close()
        clients.get(c)['wSock'].close()
        c.close()