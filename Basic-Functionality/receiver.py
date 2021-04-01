import socket
import time
import random

PACKET_SIZE = 512
RECEIVER_ADDR = ('localhost', 8080)
SENDER_ADDR = ('localhost', 9090)
SLEEP_INTERVAL = 0.05
TIMEOUT_INTERVAL = 0.5

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(RECEIVER_ADDR)

expected_seq_num = 0
data = ""

file = open("output", "wb")

packets = dict()


def helper(recv_data, packet_length):
    global expected_seq_num
    expected_seq_num += packet_length
    while str(expected_seq_num) in packets.keys():
        next_packet_data, next_packet_length = packets[str(expected_seq_num)]
        recv_data += next_packet_data
        expected_seq_num += next_packet_length
    file.write(recv_data)


def send_ack(SYN_bit):
    global expected_seq_num
    ack_send = "SYN=" + str(SYN_bit) + ":ack=" + str(expected_seq_num)
    if random.randint(0, 10) > 0:
        #print(f'Packet Sent with ACK is {expected_seq_num} at {time.time()}')
        sock.sendto(ack_send.encode(), SENDER_ADDR)
    # else:
        # print(
        #     f'Packet with ACK {expected_seq_num} going to Lost at {time.time()}')


while True:
    message, _ = sock.recvfrom(2048)
    packet_length = len(message)
    temp = message.decode('latin-1').split(':')
    SYN_recv = int(temp[0][4])
    recv_seq_num = int(temp[1][4:])

    #print(f'Sequence Number Received is {recv_seq_num} at {time.time()}')

    if SYN_recv == 1 and expected_seq_num == recv_seq_num:
        expected_seq_num += packet_length
        send_ack(1)
    elif SYN_recv == 1:
        send_ack(1)
    else:
        recv_data = message[len(temp[0])+len(temp[1])+2+5:]
        if expected_seq_num == recv_seq_num:
            helper(recv_data, packet_length)
            send_ack(0)
        elif recv_seq_num > expected_seq_num:
            packets[str(recv_seq_num)] = (recv_data, packet_length)
            send_ack(0)
        else:
            send_ack(0)
