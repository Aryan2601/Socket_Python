import socket
import select

header = 64
ip = socket.gethostbyname(socket.gethostname()) #get ip address 
port = 11337
format = 'utf-8'
server_socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM) #ipv4 , tcp data packets 
server_socket.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1) # gives us way to reconnect
server_socket.bind((ip,port))
server_socket.listen()

sockets_list = [server_socket] #to store clients in this list

clients = {}

def receive_message(client_socket):
    try:
        message_header = client_socket.recv(header)
        if not len(header):
            return False
        message_length = int(message_header.decode("utf-8").strip())
        return{"header":message_header,"data":client_socket.recv(message_length)}
    except:
        return False
    
while True:
    read_sockets, _ , exception_sockets = select.select(sockets_list,[],sockets_list) #socket that we read , socket that we write, sockets that we might air on
    
    for notified_socket in read_sockets:
        if notified_socket == server_socket:
            client_socket, client_address = server_socket.accept() #To bring in connection
            user = receive_message(client_socket)
            if user is False: #if someone disconnected
                continue 
            sockets_list.append(client_socket)
            clients[client_socket] = user
            print(f"Accepted new connection from {client_address[0]}:{client_address[1]} username:{user['data'].decode(format)}")
            
        else:
            message = receive_message(notified_socket)
            if message is False:
                print(f"Close connection from {clients[notified_socket]['data'].decode(format)}")
                sockets_list.remove(notified_socket)
                del clients[notified_socket]
                continue
            user = clients[notified_socket]
            print(f"Received message from: {user['data'].decode(format)} : {message['data'].decode(format)}")
            for client_socket in clients:
                # But don't sent it to sender
                if client_socket != notified_socket:
                    # Send user and message (both with their headers)
                    # We are reusing here message header sent by sender, and saved username header send by user when he connected
                    client_socket.send(user['header'] + user['data'] + message['header'] + message['data'])
    for notified_socket in exception_sockets:
        sockets_list.remove(notified_socket)
        del clients[notified_socket]
    

