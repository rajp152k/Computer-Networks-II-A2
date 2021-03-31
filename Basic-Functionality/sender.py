import socket
import random
import time
import _thread

PACKET_SIZE = 512
RECEIVER_ADDR = ('localhost', 8080)
SENDER_ADDR = ('localhost', 9090)
SLEEP_INTERVAL = 0.05
TIMEOUT_INTERVAL = 4

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(SENDER_ADDR)

N = 30

next_seq_num = 0
expected_ack_number = 0
rwnd = N
start_time = -1

packets = dict()

lock = _thread.allocate_lock()


def get_packet(seq_num):
    if str(seq_num) in packets.keys():
        return packets[str(seq_num)]
    else:
        data_length = random.randint(1, 5)
        single_number = random.randint(0, 9)
        data = [str(single_number) for x in range(data_length)]
        data = "".join(data)
        data = "seq=" + str(next_seq_num) + ":data=" + data
        packets[str(next_seq_num)] = data
        return data


def send(next_packet, seq_num):
    global next_seq_num
    if random.randint(0, 2) > 0:
        print(
            f'Packet Sent with Sequence number is {seq_num} at {time.time()}')
        sock.sendto(next_packet.encode(), RECEIVER_ADDR)
    else:
        print(
            f'Packet with Sequence Number {seq_num} going to Lost at {time.time()}')


def send_packet(seq_num, is_retransmission):
    lock.acquire()
    global start_time
    if not is_retransmission:
        global next_seq_num
        next_packet = get_packet(next_seq_num)
        while (next_seq_num - expected_ack_number + len(next_packet)) <= rwnd:
            send(next_packet, next_seq_num)
            next_seq_num += len(next_packet)
            next_packet = get_packet(next_seq_num)
    else:
        packet_resent = get_packet(seq_num)
        send(packet_resent, seq_num)
        start_time = time.time()
    if start_time == -1:
        start_time = time.time()
    lock.release()


def timer_thread():
    while True:
        if start_time != -1 and time.time() - start_time > TIMEOUT_INTERVAL:
            print('Resending')
            send_packet(expected_ack_number, True)


def main_thread():
    send_packet(None, False)
    _thread.start_new_thread(timer_thread, ())

    while True:
        global start_time, expected_ack_number
        message, _ = sock.recvfrom(1024)
        message = message.decode()
        message = message.split(':')
        recv_ack = int(message[0][4:])
        print(f'Received Ack {recv_ack} at {time.time()}')
        if recv_ack > expected_ack_number:
            expected_ack_number = recv_ack
            if expected_ack_number == next_seq_num:
                start_time = -1
            else:
                start_time = time.time()
            if next_seq_num <= 50:
                send_packet(None, False)
            elif next_seq_num == expected_ack_number:
                return


main_thread()
