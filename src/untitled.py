import subprocess
from threading import Thread

stop = False

def writer(fd):
    while(not stop):
        print(fd.read(1).decode('utf-8'), end='')

cmd = "docker run -i docker-python python -u repl.py"
proc = subprocess.Popen(cmd.split(' '), stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

proc.stdin.write(b'print 5\n')
proc.stdin.flush()

t = Thread(target=writer, args=(proc.stdout,))
t.start()

e = Thread(target=writer, args=(proc.stderr,))
e.start()

proc.stdin.close()
proc.wait()
stop = True

#proc.kill()