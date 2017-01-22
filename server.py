from tornado import websocket, web, ioloop
import tornado
from time import sleep
from threading import Thread, Event
import subprocess
import json
import urllib
import html
from pygments import highlight
from pygments.lexers import PythonLexer
from pygments.formatters import HtmlFormatter
import os.path


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

class ResolveHandler(BaseHandler):
    def post(self):
        #self.set_header("Access-Control-Allow-Origin", "*")
        #print(self.request.body)
        formatter = HtmlFormatter();
        lex = PythonLexer();
        formatter.noclasses = True;

        raw = self.get_body_argument("params")
        raw = raw.split("<")
        for i in range(len(raw)):
            if "wasCode" in raw[i]:
                end = raw[i].find('>')
                raw[i] = raw[i][:end] +highlight(raw[i][end:], lex, formatter)

        raw = "<".join(raw)

        #print(htmlStr)
        # decoded_string = html.unescape(htmlStr);
        # decoded_string = bytes(htmlStr, "utf-8").decode("unicode_escape")
        # print(decoded_string)
        raw = raw.replace('\\n', '')
        raw = raw.replace('\n', '<br>')
        raw = raw.replace('<textarea', '<textarea style="display:none"')
        raw = raw.replace('"', "")

        #css = open(os.path.join(os.path.dirname(__file__), "static/css/editor.css")).read()
        #raw = "<style>"+css+"</style>"+raw
        print(raw)
        self.write({'body': raw, 'raw':'true'})
        #body to html
        #convert raw... python to html formatted pretty.




class EditorHandler(web.RequestHandler):
    def get(self):
        d = self.get_argument("data", default="")
        if(len(d)):
            d = bytes(d, "utf-8").decode("unicode_escape")

        self.set_header("Access-Control-Allow-Origin", "*")
        print("rendering with: "+d)

        docCount = len(d.split('class="stdout"')) - 1

        self.render("editor.html", n=docCount, data=d[1:-1].replace('\n',''))

class HomeHandler(web.RequestHandler):
    def get(self):
        self.render("index.html")

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


class web_app(web.Application):
    def __init__(self):
        handlers = [
            (r'/', HomeHandler),
            (r'/editor', EditorHandler),
            (r'/ws', SocketHandler),
            (r'/resolve', ResolveHandler),
        ]

        settings = {
            "static_path": os.path.join(os.path.dirname(__file__), "static"),
            "template_path": os.path.join(os.path.dirname(__file__), "template")
        }
        web.Application.__init__(self, handlers, **settings)

# app = web.Application([
#         (r'/editor', EditorHandler),
#         (r'/ws', SocketHandler),

#         (r'/resolve', ResolverHandler)
# ])

if __name__ == '__main__':
    app = web_app()
    print("Now running at http://localhost:5000/editor")
    app.listen(5000)
    ioloop.IOLoop.instance().start()
