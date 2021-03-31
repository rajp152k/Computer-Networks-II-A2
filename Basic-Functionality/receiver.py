import socket
import time

PACKET_SIZE = 512
RECEIVER_ADDR = ('localhost', 8080)
SENDER_ADDR = ('localhost', 9090)
SLEEP_INTERVAL = 0.05
TIMEOUT_INTERVAL = 0.5

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(RECEIVER_ADDR)

expected_seq_num = 0
data = ""

file = open("output.txt", "w")

while True:
    message, _ = sock.recvfrom(1024)
    message = message.decode()
    packet_length = len(message)
    message = message.split(':')
    recv_seq_num = int(message[0][4:])
    #print(f'Sequence Number Received is {recv_seq_num} at {time.time()}')
    # print(f'Data Recevied is {message[1][5:]}')
    if expected_seq_num == recv_seq_num:
        ack_send = "ack=" + str(expected_seq_num + packet_length)
        #print(f'Send Ack {ack_send} at {time.time()}')
        sock.sendto(ack_send.encode(), SENDER_ADDR)
        expected_seq_num += packet_length
        file.write(message[1][5:])
