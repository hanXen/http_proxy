#!/usr/bin/python3

import socket
import sys
import threading

list_lock = threading.Lock()
clients_list = []

def receive_client(client_socket, send_socket):
	while True:
		try:
			response = send_socket.recv(65538)
			if not response:
				break
			client_socket.send(response)	
		except:
			break

def lis_client(client_socket):
	while True:
		try:
			request = client_socket.recv(4096).decode()
			if not request:
				break
			host_idx = request[request.index("Host"):]
			send_host = host_idx[len("Host: "):host_idx.index("\r\n")]
			send_port = 80
			send_addr = (send_host, send_port)
			send_socket =  socket.socket(socket.AF_INET , socket.SOCK_STREAM)
			send_socket.connect(send_addr)
			send_socket.send(request.encode())
			th = threading.Thread(target = receive_client, args = (client_socket,send_socket))
			th.daemon = True
			th.start()
		except:
			break
	try:
		send_socket.close()
	except:
		pass
	list_lock.acquire()
	clients_list.remove(client_socket)
	list_lock.release()
	client_socket.close()

def start_proxy(server_socket):
	try:
		while True:
			(client_socket,addr) = server_socket.accept()
			list_lock.acquire()
			clients_list.append(client_socket)
			list_lock.release()
			t = threading.Thread(target = lis_client, args = (client_socket,))
			t.daemon = True
			t.start()
	except KeyboardInterrupt:
		print("\n--- Server Closed ---")
		list_lock.acquire()
		for client in clients_list:
			client.close()
		list_lock.release()
		server_socket.close()
		sys.exit(1)

def main():
	if len(sys.argv) != 2:
		print("*** Syntax Error ***")
		print("Syntax: http_proxy <port>")
		print("Sample: http_oroxy 8080")
		sys.exit(1)

	port = int(sys.argv[1])
    
	server_socket = socket.socket(socket.AF_INET , socket.SOCK_STREAM)
	server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
	server_socket.bind(('127.0.0.1',port))
	server_socket.listen(10)
	
	start_proxy(server_socket)

if __name__ == '__main__':
	main()