# client_minimal_fix.py
from socket import *
from sys import *
from select import *
import threading
from threading import Thread
from socket import SHUT_RDWR

if len(argv) != 3:
    print("usage:", argv[0], "<server name> <server port>")
    exit()

serverName = argv[1]
serverPort = int(argv[2])

sock = socket(AF_INET, SOCK_STREAM)
sock.connect((serverName, serverPort))
print(f"Connected to server at ('{serverName}', '{serverPort}')")

sockFile = sock.makefile(mode='r')
serverSockFileOut = sock.makefile(mode="w")

stop_event = threading.Event()

def send_message(sock, sockFile):
    try:
        while not stop_event.is_set():
            line = stdin.readline()
            serverSockFileOut.write(line)
            serverSockFileOut.flush()

            if not line:  # EOF => client wants to close connection
                print('*** Client closing connection')
                try:
                    sock.shutdown(SHUT_RDWR)
                except Exception:
                    pass
                stop_event.set()
                break
    except Exception:
        stop_event.set()
        print('*** Client closing connection')
    finally:
        try:
            serverSockFileOut.close()
        except Exception:
            pass

def receive_message(sock, sockFile):
    try:
        while not stop_event.is_set():
            line = sockFile.readline()
            if not line:  # EOF => server closed connection
                print('*** Server closed connection')
                stop_event.set()
                try:
                    sock.shutdown(SHUT_RDWR)
                except Exception:
                    pass
                break
            print('Server:', line, end='')
    except Exception:
        stop_event.set()
        print('*** Server closed connection')
    finally:
        try:
            sockFile.close()
        except Exception:
            pass

Thread(target=send_message, args=(sock, sockFile,),daemon=True).start()
Thread(target=receive_message, args=(sock, sockFile,),daemon=True).start()

# wait until stop_event set by either thread
stop_event.wait()

# final cleanup
try:
    sockFile.close()
except Exception:
    pass
try:
    serverSockFileOut.close()
except Exception:
    pass
try:
    sock.shutdown(SHUT_RDWR)
except Exception:
    pass
try:
    sock.close()
except Exception:
    pass

print('Client exiting')