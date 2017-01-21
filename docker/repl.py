from traceback import print_exc

while(1):
	i = raw_input()
	i = i.replace("{*n*}", "\n")
	if i=='exit()':
		break
	else:
		try:
			exec(i)	
		except:
			print_exc()
		print "\\\\\\"
