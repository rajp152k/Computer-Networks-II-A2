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

packets = dict()


def helper(recv_data, packet_length):
    global expected_seq_num
    expected_seq_num += packet_length
    while str(expected_seq_num) in packets.keys():
        next_packet_data, next_packet_length = packets[str(expected_seq_num)]
        recv_data += next_packet_data
        expected_seq_num += next_packet_length
    file.write(recv_data)


while True:
    message, _ = sock.recvfrom(1024)
    message = message.decode()
    packet_length = len(message)
    message = message.split(':')
    recv_seq_num = int(message[0][4:])
    recv_data = message[1][5:]
    # print(f'Sequence Number Received is {recv_seq_num} at {time.time()}')
    # print(f'Data Recevied is {message[1][5:]}')
    if expected_seq_num == recv_seq_num:
        helper(recv_data, packet_length)
        ack_send = "ack=" + str(expected_seq_num)
        #print(f'Send Ack {ack_send} at {time.time()}')
        sock.sendto(ack_send.encode(), SENDER_ADDR)
    else:
        packets[str(recv_seq_num)] = (recv_data, packet_length)
