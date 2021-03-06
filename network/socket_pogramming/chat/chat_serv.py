import socket
import selectors
import sys

sel=selectors.DefaultSelector()
data_sock_list=[]
clnt_addr_list=[]

def serv_accept(sock):
    data_sock, clnt_addr=sock.accept()
    data_sock_list.append(data_sock)
    clnt_addr_list.append(clnt_addr)
    print('connection from {}'.format(clnt_addr[1]))
    data_sock.setblocking(False)
    sel.register(data_sock, selectors.EVENT_READ, read)

def read(data_sock, mask):
    if mask & selectors.EVENT_READ:
        received=data_sock.recv(1024)
        if received:
            if received.decode().split('$$')[1]=='0':
                print('connection from {} closing'.format(
                    clnt_addr_list[data_sock_list.index(data_sock)][1]))
                clnt_addr_list.pop(data_sock_list.index(data_sock))
                data_sock_list.remove(data_sock)
                sel.unregister(data_sock)
                data_sock.close()
            for sock in data_sock_list:
                sock.sendall(received)

if len(sys.argv) < 3:
    print('usage : <host> <port>')
    exit()

serv_sock=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
serv_sock.bind((sys.argv[1], int(sys.argv[2])))
serv_sock.listen()
serv_sock.setblocking(False)
sel.register(serv_sock, selectors.EVENT_READ, serv_accept)

while True:
    events=sel.select()
    for key, mask in events:
        if key.fileobj is serv_sock:
            callback=key.data
            callback(key.fileobj)
        else:
            callback=key.data
            callback(key.fileobj, mask)
