# server_minimal_fix.py
from socket import *
from sys import *
from select import *
import threading
from threading import Thread
from socket import SHUT_RDWR  # used when shutting down socket

if len(argv) != 2:
    print('usage:', argv[0], '<port>')
    exit()

serverPort = int(argv[1])

serverSock = socket(AF_INET, SOCK_STREAM)
serverSock.bind(('', serverPort))
serverSock.listen()

print('Waiting for a client ...')
clientSock, clientAddr = serverSock.accept()
print('Connected to a client at', clientAddr)

serverSock.close()

# file streams
clientSockFile = clientSock.makefile(mode='r')
clientSockFileOut = clientSock.makefile(mode="w")

# --- minimal addition: stop event so threads can coordinate shutdown ---
stop_event = threading.Event()

def send_message(clientSock, clientSockFile):
    try:
        while not stop_event.is_set():
            line = stdin.readline()
            # write even if empty line (EOF -> '')
            clientSockFileOut.write(line)
            clientSockFileOut.flush()

            if not line:  # EOF => server wants to close connection
                print('*** Server closing connection')
                # signal peer and local readers to wake
                try:
                    clientSock.shutdown(SHUT_RDWR)
                except Exception:
                    pass
                stop_event.set()
                break
    except Exception:
        stop_event.set()
        print('*** Server closing connection')
    finally:
        try:
            clientSockFileOut.close()
        except Exception:
            pass

def receive_message(clientSock, clientSockFile):
    try:
        while not stop_event.is_set():
            line = clientSockFile.readline()
            if not line:  # EOF from client
                print('*** Client closed connection')
                # ensure send side stops too
                stop_event.set()
                try:
                    clientSock.shutdown(SHUT_RDWR)
                except Exception:
                    pass
                break
            print('Client:', line, end='')
    except Exception:
        stop_event.set()
        print('*** Client closed connection')
    finally:
        try:
            clientSockFile.close()
        except Exception:
            pass

# start threads (no need to make them daemon since main waits on stop_event)
Thread(target=send_message, args=(clientSock, clientSockFile,),daemon=True).start()
Thread(target=receive_message, args=(clientSock, clientSockFile,),daemon=True).start()

# Wait until one of the threads sets the stop_event
stop_event.wait()

# final cleanup
try:
    clientSockFile.close()
except Exception:
    pass
try:
    clientSockFileOut.close()
except Exception:
    pass
try:
    clientSock.shutdown(SHUT_RDWR)
except Exception:
    pass
try:
    clientSock.close()
except Exception:
    pass

print('Server exiting')