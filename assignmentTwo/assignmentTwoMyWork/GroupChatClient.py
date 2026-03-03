#Written by: Simion Cartis
#TODO: make the double "client disconnected message" not be double, optimize code

#TODO find out how to properly end threads
#imports
from sys import *
from socket import *
import threading
from threading import *

if len(argv) != 3:
    print("usage:", argv[0], "<server name> <server port>")
    exit()

#connect to the server
serverName = argv[1]
serverPort = int(argv[2])
clientSock = socket(AF_INET, SOCK_STREAM)
clientSock.connect((serverName, serverPort))
print(f"Connected to server at ('{serverName}', '{serverPort}')")

sockFileWrite = clientSock.makefile(mode='w')
sockFileRead = clientSock.makefile(mode='r')

stopEvent = threading.Event()
closeLock = threading.Lock()
closed = False

def closeThreads():
    global closed
    with closeLock:
        if closed:
            return
        closed = True
        
        clientSock.shutdown(SHUT_RDWR)
        sockFileWrite.close()
        sockFileRead.close()
        clientSock.close()

        

def sendMessage(sockFileWrite):
    try:
        while not stopEvent.is_set():
            line = stdin.readline()
            sockFileWrite.write(line)
            sockFileWrite.flush()
            if not line:
                stopEvent.set()
                break
    except Exception:
        stopEvent.set()
        print('client closing connection')

def receiveMessage(sockFileRead):
    try:
        while not stopEvent.is_set():
            line = sockFileRead.readline()
            if not line:
                stopEvent.set()
                break
            print(line, end='')
    except Exception:
        stopEvent.set()
        print('client closing connection')

threadSend = Thread(target=sendMessage, args=(sockFileWrite,), daemon=True)
threadReceive = Thread(target=receiveMessage, args=(sockFileRead,))
threadSend.start()
threadReceive.start()

stopEvent.wait()
closeThreads()
threadReceive.join()
print('closing')