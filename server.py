from tornado import websocket, web, ioloop
import json

class IndexHandler(web.RequestHandler):
	def get(self):
		self.render("index.html")

class SocketHandler(websocket.WebSocketHandler):
    def check_origin(self, origin):
        return True

    def open(self):
        self.write_message("hello friend")

    def on_close(self):
        print("conn closed");


app = web.Application([
	(r'/', IndexHandler),
	(r'/ws', SocketHandler)
])

if __name__ == '__main__':
	print("Now running at http://localhost:5000/")
	app.listen(5000)
	ioloop.IOLoop.instance().start()