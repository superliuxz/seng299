import socket
import json
import sys
import select


class CommunicationHandler:
	def __init__(self):
		self.sock = socket.socket()
		self.sel_list = [self.sock]

	def get_self_sock(self):
		return self.sock

	def send(self, dictionary):
		data = bytes(json.dumps(dictionary), "utf-8")
		self.sock.send(data)

	def receive(self):
		data = self.sock.recv(4096)

		return "" if not data else json.loads(data, encoding="utf-8")

	def close(self):
		self.sock.close()

	def get_response(self):
		return select.select(self.sel_list, [], [])


class ServerCommunicationHandler(CommunicationHandler):
	def __init__(self, host, port):
		super().__init__()

		self.sock.setblocking(False)
		## https://stackoverflow.com/questions/29217502/socket-error-address-already-in-use
		self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		self.sock.bind((host, port))
		self.sock.listen(5)

	@staticmethod
	def send(dictionary, s):
		'''
		overrides the method in base class

		:param dictionary:
		:param s:
		:return:
		'''
		data = bytes(json.dumps(dictionary), "utf-8")

		try:
			for sock in s:
				sock.send(data)

		except TypeError:
			s.send(data)

	@staticmethod
	def receive(s):
		data = s.recv(4096)

		return "" if not data else json.loads(data, encoding="utf-8")

	@staticmethod
	def close(s):
		s.close()

	def close_all(self):
		for sock in self.sel_list:
			sock.close()

	def add_sock(self, sock):
		self.sel_list.append(sock)

	def remove_sock(self, sock):
		self.sel_list.remove(sock)

	def accept_new_conn(self):
		sock, addr = self.sock.accept()

		self.add_sock(sock)

		return sock.getpeername()



class ClientCommunicationHandler(CommunicationHandler):
	def __init__(self, host, port):
		super().__init__()

		self.sel_list.append(sys.stdin)

		try:
			self.sock.connect((host, port))
		except ConnectionRefusedError or socket.gaierror:
			print('Unable to connect {}@{}'.format(host, port))
			sys.exit(1)


## some tests
if __name__ == "__main__":
	c1 = ServerCommunicationHandler("localhost", 8888)
	c2 = ClientCommunicationHandler("localhost", 8888)

	print(c1.sel_list)
	print(c2.sel_list)