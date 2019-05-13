import struct
import os
import socket
import argparse

ETH_P_ALL = 0x0003
ETH_SIZE = 14

def make_ethernet_header(raw_data):
	ether_data = raw_data[:ETH_SIZE]
	ether = struct.unpack('!6B6BH', ether_data)
	print('Ethernet Header')
	print('[dst] %02x:%02x:%02x:%02x:%02x:%02x' % ether[:6])
	print('[src] %02x:%02x:%02x:%02x:%02x:%02x' % ether[6:12])
	print('[Ether_type]',ether[12])
	if ether[12] == 2048:
		make_IP_header(raw_data)

def binary_change(input):
	dec = int(input,16)
	if dec < 2:
		flag_bin = bin(dec)
		flag = '0b' + '000' + flag_bin[2:]
	elif 2 <= dec and dec < 4:
		flag_bin = bin(dec)
		flag = '0b' + '00' + flag_bin[2:]
	elif 4 <= dec and dec < 8:
		flag_bin = bin(dec)
		flag = '0b' + '0' + flag_bin[2:]
	else:
		flag = bin(dec)
	return flag

def dumpcode(buf):
	print('Raw Data')
	print("%7s"% "offset ", end='')
	for i in range(0, 16):
		print("%02x " % i, end='')
		if not (i%16-7):
			print("- ", end='')
	print("")
	for i in range(0, len(buf)):
		if not i%16:
			print("0x%04x" % i, end= ' ')
		print("%02x" % buf[i], end= ' ')
		if not (i % 16 - 7):
			print("- ", end='')
		if not (i % 16 - 15):
			print(" ")
	print("")
def make_IP_header(raw_data):
	print('IP HEADER')
	print('[version] %01x' % (raw_data[14]//16))
	print('[header_length]', raw_data[14] % 16)
	print('[tos] %d' % raw_data[15])
	print('[total_length]', raw_data[16]*256+raw_data[17])
	print('[id]', raw_data[18]*256+raw_data[19])
	print('[flag]', int(raw_data[20]/32))
	print('[offset]', (raw_data[20]%32)+raw_data[21])
	print('[TTL] %02x' % raw_data[22])
	print('[protocol] %02x' % raw_data[23])
	print('[checksum]', raw_data[24]*256+raw_data[25])
	print('[dst] %d.%d.%d.%d' % (raw_data[26],raw_data[27],raw_data[28],raw_data[29]))
	print('[src] %d.%d.%d.%d' % (raw_data[30],raw_data[31],raw_data[32],raw_data[33]))
	dumpcode(raw_data)

def sniffing(nic):
	if os.name == 'nt':
		address_familiy = socket.AF_INET
		protocol_type = socket.IPPROTO_IP
	else:
		address_familiy = socket.AF_PACKET
		protocol_type = socket.ntohs(ETH_P_ALL)

	with socket.socket(address_familiy, socket.SOCK_RAW, protocol_type) as sniffe_sock:
		sniffe_sock.bind((nic, 0))

		if os.name == 'nt':
			sniffe_sock.setsockopt(socket.IPPROTO_IP,socket.IP_HDRINCL,1)
			sniffe_sock.ioctl(socket.SIO_RCVALL,socket.RCVALL_ON)

		data, _ = sniffe_sock.recvfrom(65535)
		make_ethernet_header(data)


		if os.name == 'nt':
			sniffe_sock.ioctl(socket.SIO_RCVALL,socket.RCVALL_OFF)

if __name__ == '__main__':
	parser = argparse.ArgumentParser(description='This is a simpe packet sniffer')
	parser.add_argument('-i', type=str, required=True, metavar='NIC name', help='NIC name')
	args = parser.parse_args()

	sniffing(args.i)