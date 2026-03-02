# Written by: Simion Cartis
#TODO: make it so that you can actually kill the execution of this program (maybe just keyboard interrupt is ok?)

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
clients = [serverSock] #TODO, since clients doesn't just hold clients, maybe change its name to sockets?

# def acceptClients():
#     clientSock, clientAddr = serverSock.accept()
#     clientSock.setblocking(False)
#     print('client at address ', clientAddr, ' connected')
#     clients.append(clientSock)

def readMessage(clients: list[socket]):
    readable, writable, exceptReady= select(clients, clients, clients) #TODO, do I need the third arg?
    readable: list[socket]
    writable: list[socket]
    toRemove = []
    for r in readable:
        if r is serverSock:
            clientSock, clientAddr = serverSock.accept()
            clientSock.setblocking(False)
            print('client at address ', clientAddr, ' connected')
            clients.append(clientSock)
        else:
            sockFileIn = r.makefile(mode='r')
            line = sockFileIn.readline()
            if not line:
                print('client with socket disconnected') #TODO how can I pass the clientAddr to this print? make clients a dictionary?
                toRemove.append(r)
            else:
                for w in writable:
                    if w in toRemove or w is r or w is serverSock:
                        continue
                    sockFileOut = w.makefile(mode='w')
                    sockFileOut.write(line) #TODO add client address that sent message (def need to make it a dictionary)
                    sockFileOut.flush()
                    sockFileOut.close()
                    sockFileIn.close()
    cleanClients(clients, toRemove)

def cleanClients(clients: list[socket], toRemove: list[socket]):
    for c in toRemove:
        clients.remove(c)

print('waiting for clients to connect...')
try:
    while True:
        # acceptClients()
        readMessage(clients)
except KeyboardInterrupt:
    for c in clients:
        c.close()