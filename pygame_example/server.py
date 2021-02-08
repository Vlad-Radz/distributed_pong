import socket
#  low-level primitives for working with multiple threads
from _thread import start_new_thread

# socket: A socket is one endpoint of a two-way communication link between two programs running on the network.
# socket: is bound to a port number so that the TCP layer can identify the app that data is destined to be sent to.
# socket: software structure
# ####
# AF_INET & AF_INET6: address (and protocol) families
# SOCK_STREAM means that it is a TCP socket.
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

server = '192.168.178.43'
# server = "localhost"
port = 5555

# Translate a host name to IPv4 address format
# Is here to allow localhost
server_ip = socket.gethostbyname(server)

try:
    # Bind the socket to address
    s.bind((server, port))
except socket.error as e:
    print(str(e))

# Enable a server to accept connections
# number of unaccepted connections that the system will allow before refusing new connections
s.listen(2)
print("Waiting for a connection")

currentId = "0"
pos = ["0:50,50", "1:100,100"]


def threaded_client(conn):
    global currentId, pos
    # What happens with currentId here? -->
    conn.send(str.encode(currentId))
    currentId = "1"  # --> это сервер присваивает ID игрокам. Сначала посылает 0, потом 1
    while True:
        try:
            # Receive data from the socket
            # The maximum amount of data to be received at once is specified by bufsize. Why this bufsize?
            data = conn.recv(2048)
            reply = data.decode('utf-8')
            if not data:
                conn.send(str.encode("Goodbye"))
                break
            else:
                # If there is reply, we get ID from one "run" and save position in the shared data structure.
                # And send to the socket position of different player.
                print("Recieved: " + reply)
                arr = reply.split(":")
                id = int(arr[0])
                pos[id] = reply  # is it thread-safe?

                if id == 0: nid = 1
                if id == 1: nid = 0

                reply = pos[nid][:]  # a copy of the whole array --> send position
                print("Sending: " + reply)

            conn.sendall(str.encode(reply))
        except:
            break

    print("Connection Closed")
    conn.close()


while True:
    # `conn` is a new socket object usable to send and receive data on the connection
    # `address` is the address bound to the socket on the other end of the connection.
    conn, addr = s.accept()
    print("Connected to: ", addr)

    # Start a new thread and return its identifier.
    # The thread executes the function function with the argument list args (which must be a tuple).
    start_new_thread(threaded_client, (conn,))
