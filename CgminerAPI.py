import socket
import json

#http://thomassileo.com/blog/2013/09/17/playing-with-python-and-cgminer-rpc-api/
#Copyright (2013) Thomas Sileo

class CgminerAPI(object):
	""" Cgminer RPC API wrapper. """
	def __init__(self, host='localhost', port=4028):
		self.data = {}
		self.host = host
		self.port = port

	def command(self, command, arg=None):
		""" Initialize a socket connection,
		send a command (a json encoded dict) and
		receive the response (and decode it).
		"""
		sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

		try:
			sock.connect((self.host, self.port))
			payload = {"command": command}
			if arg is not None:
				# Parameter must be converted to basestring (no int)
				payload.update({'parameter': unicode(arg)})

			sock.send(json.dumps(payload))
			received = self._receive(sock)
		finally:
			sock.shutdown(socket.SHUT_RDWR)
			sock.close()
		
		return json.loads(received[:-1])

	def _receive(self, sock, size=4096):
		msg = ''
		while 1:
			chunk = sock.recv(size)
			if chunk:
				msg += chunk
			else:
				break
		return msg

	def __getattr__(self, attr):
		def out(arg=None):
			return self.command(attr, arg)
		return out