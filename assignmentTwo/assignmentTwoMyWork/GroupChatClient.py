#Written by: Simion Cartis
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

#method for closing threads without causing race conditions. Not strictly necessary,
#as only the main thread can call this
def closeSockets():
    global closed #set lock so that two threads don't try to access func at once
    with closeLock:
        if closed: #if this function has already ran, don't try to run it again, simply return
            return
        closed = True
        
        clientSock.shutdown(SHUT_RDWR) #NECESSARY FOR CLEARNING BUFFERS, SUCH AS THE READING MAKEFILE
        sockFileWrite.close()
        sockFileRead.close()
        clientSock.close()

        
#function for writing to a server
def sendMessage(sockFileWrite):
    try:
        while not stopEvent.is_set():
            line = stdin.readline()
            sockFileWrite.write(line)
            sockFileWrite.flush()
            if not line: #receive an EOF, break the while loop, ending the thread and terminating stopEvent.wait()
                stopEvent.set()
                break
    except Exception:
        stopEvent.set()
        print('client closing connection')

#function for receiving from server
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

#threads for executing these functions asynchronously (I don't think select would work on windows here)
threadSend = Thread(target=sendMessage, args=(sockFileWrite,), daemon=True) #daemon thread because stdin.readline() is blocking, so kill thread when main thread exits
threadReceive = Thread(target=receiveMessage, args=(sockFileRead,))
threadSend.start()
threadReceive.start()

stopEvent.wait()
closeSockets()
threadReceive.join() #join the non-daemon if it hasn't already ended by now
print('closing')