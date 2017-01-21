from tornado import websocket, web, ioloop
from time import sleep
from threading import Thread, Event
import subprocess
import json
import urllib
from pygments import highlight
from pygments.lexers import PythonLexer
from pygments.formatters import HtmlFormatter


class BaseHandler(web.RequestHandler):

    def set_default_headers(self):
        print("setting headers!!!")
        self.set_header("Access-Control-Allow-Origin", "https://compose.mixmax.com")
        self.set_header("Access-Control-Allow-Headers", "x-requested-with")
        self.set_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')
        self.set_header('Access-Control-Allow-Credentials', 'true')


    def post(self):
        self.write('some post')

    def get(self):
        self.write('some get')

    def options(self):
        # no body
        self.set_status(204)
        self.finish()

class ResolverHandler(BaseHandler):
    def post(self):
        #self.set_header("Access-Control-Allow-Origin", "*")
        #print(self.request.body)
        def toHtml(prettyLines):
            return "".join(prettyLines)

        def prettyEachLine(raw):
                lines = raw.split("\n")
                formatter = HtmlFormatter()
                lex = PythonLexer()
                formatter.noclasses = True
                prettyLines = []
                for line in lines:
                        pretty = highlight(line, lex, formatter)
                        prettyLines.append(pretty)
                return prettyLines
        raw = self.get_body_argument("params")
        html = toHtml(prettyEachLine(raw))
        print(urllib.parse.unquote(html))
        self.write({'body': urllib.parse.unquote(html), 'raw': 'true'})
        #body to html
        #convert raw... python to html formatted pretty.




class EditorHandler(web.RequestHandler):
    def get(self):
        self.set_header("Access-Control-Allow-Origin", "*")
        self.render("editor.html")

class SocketHandler(websocket.WebSocketHandler):
    def check_dorigin(self, origin):
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
       # (r'/files/(.*)', web.StaticFileHandler, {'path':'static/'})
        (r'/resolve', ResolverHandler)
])

if __name__ == '__main__':
	print("Now running at http://localhost:5000/")
	app.listen(5000)
	ioloop.IOLoop.instance().start()
