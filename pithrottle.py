#!/usr/bin/python

import socket
import re
from pprint import pprint

TCP_IP = '127.0.0.1'
TCP_PORT = 12090
BUFFER_SIZE = 1024
#BUFFER_SIZE = 4
MESSAGE = "Hello, World!"


class PiThrottle:
	def __init__(self, *args):
		pass
      
	def roster(self, input):
		print "Roster list"
		self.rosterlist = []
        	parse=re.search('RL([0-9]+)\\]\\\\\[(.*)',input)
		if parse.group(1) > 0:
			for entry in parse.group(2).split(']\['):
				self.rosterlist.append(entry.split('}|{'))
		print '\n'.join(map(str,self.rosterlist))

	def turnoutstate(self, input):
		print "Turnout status"
		self.turnoutstates = {}
		for entry in input[6:].split(']\['):
			entrylist = entry.split('}|{')
			if entrylist[1] != 'Turnout':
				self.turnoutstates[entrylist[1]] = entrylist[0]
		pprint(self.turnoutstates)

	def turnout(self, input):
		print "Turnout list"
		self.turnouts = {}
		for entry in input[6:].split(']\['):
			entrylist = entry.split('}|{')
			if entrylist[1]:
				self.turnouts[entrylist[1]] = { 'sysname': entrylist[0], 'state': entrylist[2] }
			else:
				self.turnouts[entrylist[0]] = { 'sysname': entrylist[0], 'state': entrylist[2] }
		pprint(self.turnouts)

	def setturnout(self, input):
		parse=re.search('PTA([0-9])(.*)',input)
		if parse:
			print "Turnout: "+parse.group(2)+" set to "+self.turnoutstates[parse.group(1)]
	
	def route(self, input):
		print "Route list"
		routelist = []
		routes = {}
		for entry in input[6:].split(']\['):
			entrylist = entry.split('}|{')
			routelist.append(entrylist)
			if entrylist[1]:
				routes[entrylist[1]] = entrylist[0]
			else:
				routes[entrylist[0]] = entrylist[0]

		print '\n'.join(map(str,routelist))
		pprint(routes)


# Main code line
if __name__ == '__main__':
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	s.connect((TCP_IP, TCP_PORT))
	s.settimeout(0.05)


	throttle = PiThrottle()

# s.send(MESSAGE)
	data =""

	while True:
		try:
			data = data + s.recv(BUFFER_SIZE)
			bits=data.rsplit('\n',1)
			if len(bits)>1:
				data = bits[1]
				lines = bits[0].split('\n')
				for line in lines:
					if line:
						print line
						if re.match("RL(.*)",line):
							throttle.roster(line)
						if re.match("PPA(.*)",line):
							print "Power"
						if re.match("PTT(.*)",line):
							throttle.turnoutstate(line)
						if re.match("PTL(.*)",line):
							throttle.turnout(line)
						if re.match("PRL(.*)",line):
							throttle.route(line)
						if re.match("PTA(.*)",line):
							throttle.setturnout(line)
					

#			print '\n'.join(map(str,throttle.rosterlist))
#			pprint(turnoutstates)
#			pprint(turnouts)
#			pprint(routes)


		except (socket.timeout):
			pass

		except Exception, e:
			print "Exception: "+str(e)
			break

	s.close()
