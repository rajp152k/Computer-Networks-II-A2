import socket
import time
import random

RECEIVER_ADDR = ('10.0.10.2', 8080)
SENDER_ADDR = ('10.0.10.1', 9090)

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(RECEIVER_ADDR)

expected_seq_num = 0

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


def send_ack():
    global expected_seq_num
    ack_send = "ack=" + str(expected_seq_num)
    # if random.randint(0, 10) > 0:
    #print(f'Packet Sent with ACK is {expected_seq_num} at {time.time()}')
    sock.sendto(ack_send.encode(), SENDER_ADDR)
    # else:
    #     print(
    #         f'Packet with ACK {expected_seq_num} going to Lost at {time.time()}')


while True:
    message, _ = sock.recvfrom(2048)
    packet_length = len(message)
    temp = message.decode('latin-1').split(':')
    recv_seq_num = int(temp[0][4:])
    recv_data = message[len(temp[0])+6:]
    # print(f'Sequence Number Received is {recv_seq_num} at {time.time()}')
    # print(f'Data Recevied is {message[1][5:]}')
    if expected_seq_num == recv_seq_num:
        helper(recv_data, packet_length)
        send_ack()
    elif recv_seq_num > expected_seq_num:
        packets[str(recv_seq_num)] = (recv_data, packet_length)
        send_ack()
    else:
        send_ack()
