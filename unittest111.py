import unittest

class Test(unittest.TestCase):

	#通过装饰类使setup和tesrdown方法只执行一次
	@classmethod
	def setUpClass(cls):
		print('start')

	@classmethod
	def tearDownClass(cls):
		print('end')

	def test1(self):
		print('test1')

	def test2(self):
		print('test2')

if __name__ == '__main__':
	unittest.main()