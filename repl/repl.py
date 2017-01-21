from sys import stdout
while(1):
	i = raw_input()
	if i=='exit()':
		break
	else:
		exec(i)	
		exec('print "***"')
		stdout.flush()