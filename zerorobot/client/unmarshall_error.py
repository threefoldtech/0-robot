class UnmarshallError(Exception):
	def __init__(self, resp, msg=''):
		self.response = resp
		self.msg = msg
