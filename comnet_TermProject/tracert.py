import os
import argparse
import struct
import socket
import timeit
from functools import reduce

class PARSING:
	ETHER = None
	Reply_IP = None
	Reply_ICMP = None
	Reply_IP_Header_len = 0
	Reply_msg = ''
	Reply_UDP = None	
	Send_IP = None

	def __init__(self,raw_data,msg_len): # msg_len = send_data_length
		self.Only_IP_HEADER(raw_data[0:]) # IP_HEADER
		self.Only_ICMP_HEADER(raw_data[self.Reply_IP_Header_len:],msg_len) # ICMP_HEADER + DATA

	def Only_Ethernet_HEADER(self,raw_data):
		self.ETHER = struct.unpack('!6B6BH',raw_data)

	def Only_IP_HEADER(self,raw_data):
		self.Reply_IP_Header_len = (raw_data[0] & 0x0F) * 4 # version + (Header_len)
		IP_data = raw_data[0:self.Reply_IP_Header_len]
		IP_Option_len = self.Reply_IP_Header_len - 20
		if IP_Option_len == 0:
			unpackType = '!2B3H2B1H4B4B'
		else:
			unpackType = '!2B3H2B1H4B4B' + str(IP_Option_len) + 'B'
		self.Reply_IP = struct.unpack(unpackType,IP_data)
	
	def Only_ICMP_HEADER(self,raw_data,msg_len):
		self.Reply_ICMP = struct.unpack('!BBHHH',raw_data[0:8]) # total 8 byte
		# Total = Protocol_Type(1) + Code(1) + Checksum(2) + identifier(2) + sequence(2)
		if self.Reply_ICMP[0] == 0 and self.Reply_ICMP[1] == 0: # Arrive Destination ICMP
			if msg_len > 64:
				msg_len = 64
			self.Reply_msg = str(struct.unpack('!'+str(msg_len)+'s',raw_data[8:msg_len+8]))
			self.Reply_msg = str(self.Reply_msg[3:msg_len+3])
			# recv_data Max_size = 64 why..?????
		elif self.Reply_ICMP[0] == 3 and self.Reply_ICMP[1] == 3: # Arrive Destination UDP
			self.Send_IP = struct.unpack('!BBHHHBBH4B4B',raw_data[8:28])
			self.UDP_Header = (raw_data[28:])
		else:
			self.Send_IP = struct.unpack('!BBHHHBBH4B4B',raw_data[8:28])
	
	def Only_UDP_HEADER(self, raw_data):
		self.Reply_UDP = struct.unpack('!4H',raw_data)

class IP_Header:
	version = 4      	# 4bit
	header_len = 5		# 4bit  ver+header_len = 1byte   
	tos = 0		 	# 1byte
	total_length = 0	# 2byte
	identifier = 25252	# 2byte			
	flag = 0		# 3bit
	offset = 0		# 13bit flag+offset = 2byte
	ttl = 1			# 1byte
	protocol = 0		# 1byte
	checksum = 0		# 2byte
	src = socket.inet_aton('0.0.0.0') 	# 4byte
	dst = None				# 4byte
	IP_HEADER = None 			# TOTAL = 20 byte
	def __init__(self,Destination,DATA_LENGTH,TTL,PORT):
		self.dst = socket.inet_aton(Destination)
		self.ttl = TTL
		self.protocol = PORT
		self.total_length = 20 + 8 + DATA_LENGTH  # IP (20 byte)+ ICMP(8 byte)+DATA_LENGTH 
		self.IP_HEADER = self.MAKE_IP_HEADER() 
	def MAKE_IP_HEADER(self):
		ver_and_header_len = (self.version << 4) + self.header_len # 4 bit + 4 bit = 1 byte
		flag_and_offset = (self.flag << 13) + self.offset # 3 bit + 13 bit = 2 byte
		result = struct.pack('!BBHHHBBH4s4s',ver_and_header_len,self.tos,
					self.total_length,self.identifier,flag_and_offset,
					self.ttl,self.protocol,self.checksum,
					self.src,self.dst)
		# MAKE IP HEADER TOTAL 20 byte
		return result
class Trace_ICMP:
	PROTOCOL_TYPE = 8 # 1byte type = IPv4
	CODE = 0	  # 1byte
	CHECK_SUM= 0	  # 2byte
	IDENTYFIER = 0	  # 2byte
	SEQUENCE = 0 	  # 2byte
	send_data = ''    # send from MY_PC to domain   / ICMP header  total = 8 byte 

	timeout = 0
	TOTAL_LENGTH = 0 # ICMP PACKET LENGTH
	PROTO_PORT = 0   # DEFAULT = 8888
	MAX_HOPS = 0 	 # DEFAULT = 30
	ICMP_HEADER = None
	IP_HEADER = None
	def __init__(self,domain,packet_size,recv_tout,max_hops,port):
		self.timeout = recv_tout 	# args.t default = 1
		self.PROTO_PORT = port		# args.p default = 8888
		self.MAX_HOPS = max_hops	# args.c default = 30
		self.send_data = 'L' * (packet_size-28) # packetsize = IP_Header (20) + ICMP_Header (8) + data
		self.CHECK_SUM = self.checksum()
		self.ICMP_HEADER = self.MAKE_ICMP_PACKET()
		self.SEND_PACKET(domain)
		
	def checksum(self):
		PROTO_TYPE_AND_CODE = (self.PROTOCOL_TYPE << 8) + self.CODE
		SUM_HEADER = PROTO_TYPE_AND_CODE + self.CHECK_SUM + self.IDENTYFIER + self.SEQUENCE
		byte_data = self.send_data.encode()		
		self.TOTAL_LENGTH = len(byte_data) + 8 # send_data length + ICMP header 8 byte
		size = len(byte_data) # Make Checksum
		if size % 2 == 1: 		# if size % 2 == 1  -> make size % 2 == 0
			byte_data += b'\x00'
			size+=1
		size = size // 2
		byte_data = struct.unpack('!'+str(size)+'H',byte_data) # packing Big Endian
		SUM_HEADER += reduce(lambda x,y : x+y,byte_data) # ICMP HEADER + SEND_DATA
		result = (SUM_HEADER >> 16) + (SUM_HEADER & 0xFFFF) # sum 2 byte in once
		result += result >> 16
		result = (result ^ 0xFFFF) # Complemnet-1
		return result

	def MAKE_ICMP_PACKET(self):
		return struct.pack('!BBHHH',self.PROTOCOL_TYPE,self.CODE,self.CHECK_SUM,self.IDENTYFIER,self.SEQUENCE)

	def SEND_PACKET(self,Destination):
		with socket.socket(socket.AF_INET,socket.SOCK_RAW,socket.IPPROTO_RAW) as sock:
			get_out_of_TTL = False
			for TTL in range(1,self.MAX_HOPS+1):
				self.IP_HEADER = IP_Header(Destination,len(self.send_data),TTL,self.PROTO_PORT)
				Send_PACKET = self.IP_HEADER.IP_HEADER + self.ICMP_HEADER + self.send_data.encode()
				MY_IP_HEADER = struct.unpack('!BBHHHBBH4B4B',self.IP_HEADER.IP_HEADER)
				print("%02d" % TTL,end = "     ")
				for route in range(0,3): # Routing 3 times in TTL
					ROUTE_START = timeit.default_timer() # Timer Start point
					sock.sendto(Send_PACKET,(Domain_Address,8888))
					self.RECV_PACKET()
					ROUTE_END = timeit.default_timer() # Timer End point
					if self.Reply is None: #RECV_PACKET == NULL
						print("  *  ",end = "  ")
					else:
						packet = PARSING(self.Reply, len(self.send_data)) # RECV_PACKET != NULL
						packet_addr = {'Reply' : '%d.%d.%d.%d' % packet.Reply_IP[8:12]}
						if packet.Reply_ICMP[0] == 11 and packet.Reply_ICMP[1] == 0:
							if self.COMPARE_SEND_AND_MY_IP(packet,MY_IP_HEADER):
								print('%.2f ms' % ((ROUTE_END-ROUTE_START)*1000),end = "  ")
								if route == 2:
									try:
										name = socket.gethostbyaddr(packet_addr['Reply'])[0]
										P_addr = str(socket.gethostbyaddr(packet_addr['Reply'])[2])
										print('[',name,end = ',  ')
										print(P_addr.strip('[]'), ']',end = " ")
									except:
										print('[',packet_addr['Reply'].strip('[]'),']',end = " ")
						elif packet.Reply_ICMP[0] == 0 and packet.Reply_ICMP[1] == 0:
							if packet.Reply_ICMP[3] == 0 and packet.Reply_msg == self.send_data:
								print('%.2f ms' % ((ROUTE_END-ROUTE_START)*1000),end = "  ")
								if route == 2:
									try:
										name = socket.gethostbyaddr(packet_addr['Reply'])[0]
										P_addr = str(socket.gethostbyaddr(packet_addr['Reply'])[2])
										print('[',name,end = ", ")
										print(P_addr.strip('[]'), ']')
										print('Destination Arrive')
									except:
										print('[', packet_addr['Reply'].strip('[]'),']')
										print('Destination Arrive')
									get_out_of_TTL = True
									print("Send_data : %s " % packet.Reply_msg, end= "")
									break
				print("")						
				if get_out_of_TTL:
					break
				

	def RECV_PACKET(self):
		with socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_ICMP) as recv_sock:
			recv_sock.settimeout(self.timeout)
			try:
				self.Reply, _ = recv_sock.recvfrom(65535)
			except:
				self.Reply = None

	def COMPARE_SEND_AND_MY_IP(self,packet,MY_IP_HEADER):
		if (packet.Send_IP[0] == MY_IP_HEADER[0]
			and (packet.Send_IP[1] == MY_IP_HEADER[1] or packet.Send_IP[1] == 128)
			and packet.Send_IP[2] == MY_IP_HEADER[2]
			and packet.Send_IP[3] == MY_IP_HEADER[3]
			and packet.Send_IP[4] == MY_IP_HEADER[4]
			and packet.Send_IP[5] == 1
			and packet.Send_IP[6] == MY_IP_HEADER[6]
			and packet.Send_IP[12:] == MY_IP_HEADER[12:]):
			return True			
			
class UDP :
	s_port = 52131 # 2byte
	d_port = 33434 # 2byte
	length = 0 # 2byte
	checksum = 0 # 2byte
	msg = ''
	tout = 0
	max_hop = 0
	header = None
	ip = None
	next_proto = 0

	def __init__(self, destination,packet_size ,timeout, hops, proto) :
		self.msg = 'L' * (packet_size-28)
		self.d_port = 8888
		self.length = 8 + len(self.msg)
		self.tout = timeout
		self.max_hop = hops
		self.assemble()
		self.next_proto = proto
		self.udp_request(destination)

	def assemble(self) :
		self.header = struct.pack('!4H', self.s_port, self.d_port, self.length, self.checksum)
	
	def udp_request (self, dest) :
		with socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_RAW) as sock :
			arrive_flag = False 
			for i in range(1, self.max_hop+1) :
				self.ip = IP_Header(dest, self.length, i, self.next_proto)
				total_packet = self.ip.IP_HEADER + self.header + self.msg.encode()
				my_ip_header = struct.unpack('!BBHHHBBH4B4B', self.ip.IP_HEADER)
				print('%02d' %i, end = "  ")
				for j in range(0, 3) :
					start = timeit.default_timer()
					sock.sendto(total_packet, (args.d, 0))
					self.udp_recv()
					end = timeit.default_timer()
					if self.reply is None :
						print(' * ', end = "  ")
					else :
						packet = PARSING(self.reply, len(self.msg))
						addr = {'reply' : '%d.%d.%d.%d' %packet.Reply_IP[8:12]}
						if packet.Reply_ICMP[0] == 11 and packet.Reply_ICMP[1] == 0 :
							if (packet.Send_IP[0] == my_ip_header[0] 
								and (packet.Send_IP[1] == my_ip_header[1] or packet.send_ip[1] == 128) 
								and packet.Send_IP[2] == my_ip_header[2]
								and packet.Send_IP[3] == my_ip_header[3]
								and packet.Send_IP[4] == my_ip_header[4]
								and packet.Send_IP[5] == 1
								and packet.Send_IO[6] == my_ip_header[6]
								and packet.Send_IP[12:] == my_ip_header[12:]) :
								print('%.2f ms' %((end-start)*1000), end = "  ")
								if j == 2 :
									try :
										name = socket.gethostbyaddr(addr['reply'])[0]
										p_addr = str(socket.gethostbyaddr(addr['reply'])[2])
										print('[', name, end = ", ")
										print(p_addr.strip('[]'), ']', end = " ")
									except :
										print('[', addr['reply'].strip('[]'), ']', end = " ")
						if packet.Reply_ICMP[0] == 3 and packet.Reply_ICMP[1] == 3 :
							if (packet.Send_IP[3] == my_ip_header[3]
								and packet.Reply_UDP[1] == self.d_port) :
								print('%.2f ms' %((end-start)*1000), end = "  ")
								if j == 2 :
									try :
										name = socket.gethostbyaddr(addr['reply'])[0]
										p_addr = str(socket.gethostbyaddr(addr['reply'])[2])
										print('[', name, end = ", ")
										print(p_addr.strip('[]'), ']')
										print('Destination arrive', end = "")	
									except :
										print('[', addr['reply'].strip('[]'), ']')
										print('Destination arrive', end = "")	
									arrive_flag = True			
				print("")
				self.d_port += 1
				self.assemble()
				if(arrive_flag == True) :
					break

	def udp_recv (self) :
		with socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_ICMP) as recv_sock :
			recv_sock.settimeout(self.tout)
			try :
				self.reply, _ = recv_sock.recvfrom(65535)
			except :
				self.reply = None

if __name__ == '__main__':
	parser = argparse.ArgumentParser(description = "domain / PACKET_SIZE / RECV_TIMEOUT / UDP_PORT")
	proto_parser = parser.add_mutually_exclusive_group()
	
	parser.add_argument('d',help="Domain Address  ex) google.com")
	parser.add_argument('s',type=int,help="Packet Size ex) 50")
	parser.add_argument('-t',type=int,help="RECV_TIMEOUT Default=1",default=1,required=False)
	parser.add_argument('-c',type=int,help="max_hops Default=30",default=30,required=False)
	parser.add_argument('-p',type=int,help="PORT Default=8888",default=8888,required=False)

	proto_parser.add_argument('-I',action='store_true')
	proto_parser.add_argument('-U',action='store_true')
	args = parser.parse_args()
	
	
	Domain_Address = socket.gethostbyname(args.d)
	print("tracert to ",args.d,"(",Domain_Address,")",args.c,"hops max", "PACKET SIZE : ",args.s)
	if args.I:
		print('PROTOCOL : ICMP')
		RUN_ICMP = Trace_ICMP(Domain_Address,args.s,args.t,args.c,1)
	elif args.U:
		print('PROTOCOL : UDP')
		RUN_UDP = UDP(Domain_Address,args.s,args.t,args.c,17)
	
	