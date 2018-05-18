import socket
import sys
import random
import time

LOSS_PROB = 0
START_TIME = time.time()

def parse_args():
	global LOSS_PROB
	global RECV_BUFFER_SIZE

	LOSS_PROB = float(sys.argv[1])

def get_ip():
	s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	try:
		# Doesn't matter if its unreachable
		s.connect(('10.255.255.255', 1))
		IP = s.getsockname()[0]
	except:
		IP = '127.0.1.1'
	finally:
		s.close()
	return IP

def pack(seq_num, data = b''):
	seq_bytes = seq_num.to_bytes(4, byteorder = 'little', signed = True)
	return seq_bytes + data

def make_empty():
	return b''

def unpack(packet):
	seq_num = int.from_bytes(packet[0:4], byteorder = 'little', signed = True)
	return seq_num, packet[4:]

def get_file_name(sock):
	length, addr = sock.recvfrom(4)
	length = int.from_bytes(length, byteorder='big')
	name, addr = sock.recvfrom(length)
	return name.decode(), length

def receive(sock, file):
	try:
		with open(file, 'wb') as file:
			expected_seg = 0
			while True:
				pkt, addr = sock.recvfrom(1000000)
				if not pkt:
					break
				p = round(random.uniform(0.0, 1.0), 2)
				if  p > LOSS_PROB:
					seq_num, data = unpack(pkt)
					print(str(round(time.time() - START_TIME, 3)) + "   pkt: " + str(seq_num) + "  Receiver <- Sender")

					# Send back an ACK
					if seq_num == expected_seg:
						print(str(round(time.time() - START_TIME, 3)) + "   ack: " + str(expected_seg) + "  Receiver -> Sender")
						pkt = pack(expected_seg)
						sock.sendto(pkt, addr)
						expected_seg += 1
						file.write(data)
					else:
						if expected_seg - 1 == -1:
							expected_seg = 0
						print(str(round(time.time() - START_TIME, 3)) + "   ack: " + str(expected_seg) + "  Receiver -> Sender")
						pkt = pack(expected_seg)
						sock.sendto(pkt, addr)
				else:
					seq_num, _ = unpack(pkt)
					print(str(round(time.time() - START_TIME, 3)) + "   pkt: " + str(seq_num) + "   | Dropped")


	except IOError:
		print("Error opening " + file)

def main():
	receiverS = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	host = get_ip()
	port = 10080
	receiverS.bind((host, port))
	parse_args()
	print("Listening in address " + host + " port " + str(port))

	while True:
		try:
			file, recbuffer = get_file_name(receiverS)
			print("\n\nPacket loss probability " + str(LOSS_PROB))
			print("Socket buffer size: " + str(recbuffer))
			print("Socket buffer size updated: " + "1000000")
			print("\nThe receiver is ready to receive.")
			print("File name is received: " + file + "\n\n")
			receive(receiverS, file)
			print("\n\n" + file + " is successfully transferred")
		except KeyboardInterrupt:
			if receiverS:
				receiverS.close()
			break
if __name__ == "__main__":
    main()