from tornado import websocket, web, ioloop
from time import sleep
from threading import Thread, Event
import subprocess
import json
import os

class EditorHandler(web.RequestHandler):
	def get(self):
		self.render("editor.html")

class SocketHandler(websocket.WebSocketHandler):
    def check_origin(self, origin):
        return True

    @web.asynchronous
    def open(self):
        #self.write_message("hello friend")

        cmd = "docker run -i docker-python python -u repl.py"
        self.proc = subprocess.Popen(cmd.split(' '), stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

        #self.proc.kill()

        #self.stdin = self.proc.stdin
        #self.stdout= sout
        #self.stderr= serr
        self.stop = Event()
        self.wthread = Thread(target=writer, args=(self, self.proc.stdout, self.stop))
        self.wthread.start()
        
    def on_close(self):
        self.proc.kill()
        print("conn closed");

    def on_message(self, message):
        if(message=="{*reset*}"):
            print("RESET")

            self.proc.kill()
            self.proc.stdout.close()
            print("waiting")
            self.wthread.join()
            print("error!")

            cmd = "docker run -i docker-python python -u repl.py"
            self.proc = subprocess.Popen(cmd.split(' '), stdin=subprocess.PIPE, stdout=subprocess.PIPE)

            print("spawned new proc")

            self.wthread = Thread(target=writer, args=(self, self.proc.stdout, self.stop))
            self.wthread.start()

            self.write_message("done")
        else:
            print("got message: ", message)
            print("encoded: ", str.encode(message+"\n"))
            self.proc.stdin.write(str.encode(message+"\n"))
            self.proc.stdin.flush()

def writer(conn, fd, stop):
    while(not stop.is_set()):
        try:
            r = fd.read(1).decode('utf-8')
            if(len(r)):
                print("R: ",r)
                conn.write_message(r)
        except:
            print("read failed!")
            break

app = web.Application([
	(r'/editor', EditorHandler),
	(r'/ws', SocketHandler),
    (r'/files/(.*)', web.StaticFileHandler, {'path':'static/'})
])
if __name__ == '__main__':
	print("Now running at http://localhost:5000/")
	app.listen(5000)
	ioloop.IOLoop.instance().start()