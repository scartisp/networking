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

def sendMessage(clientSock: socket, sockFileWrite):
    try:
        while not stopEvent.is_set():
            line = stdin.readline()
            sockFileWrite.write(line)
            sockFileWrite.flush()

            if not line:
              #  print('client closing conneciton')
                try:
                    clientSock.shutdown(SHUT_RDWR)
                except Exception:
                    pass
                stopEvent.set()
                break
    except Exception:
        stopEvent.set()
        print('client closing connection')
    finally:
        sockFileWrite.close()

def receiveMessage(clientSock: socket, sockFileRead):
    try:
        while not stopEvent.is_set():
            line = sockFileRead.readline()
            print(line, end='')
            
            if not line:
                #print('server closed conneciton')
                try:
                    clientSock.shutdown(SHUT_RDWR)
                except Exception:
                    pass
                stopEvent.set()
                break
    except Exception:
        stopEvent.set()
        print('client closing connection')
    finally:
        sockFileRead.close()

Thread(target=sendMessage, args=(clientSock, sockFileWrite), daemon=True).start()
Thread(target=receiveMessage, args=(clientSock, sockFileRead), daemon=True).start()

stopEvent.wait()

print('closing')
sockFileWrite.close()
sockFileRead.close()
clientSock.close()