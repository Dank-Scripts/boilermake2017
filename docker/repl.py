while(1):
	i = raw_input()
        i = i.replace("{*n*}", "\n")
	if i=='exit()':
		break
	else:
		exec(i)	
		print "\\\\\\"
