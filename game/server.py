import socket
import uuid
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

my_ids = []


def threaded_client(conn):
    global my_ids
    new_id = str(uuid.uuid4())
    conn.send(str.encode(new_id))
    my_ids.append(new_id)
    # while True:
    if len(my_ids) == 1:
        print("HELLO")
        conn.sendall(str.encode(str(my_ids)))

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
