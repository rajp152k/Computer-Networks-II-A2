import socket
import random
import time
import _thread
import os

RECEIVER_ADDR = ('10.0.10.2', 8080)
SENDER_ADDR = ('10.0.10.1', 9090)
TIMEOUT_INTERVAL = 2
BUFFER_SIZE = 1024

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(SENDER_ADDR)

N = 50 * BUFFER_SIZE

next_seq_num = 0
expected_ack_number = 0
rwnd = N
start_time = -1

packets = dict()

lock = _thread.allocate_lock()

completed = False

# the name of file we want to send, make sure it exists
filename = "test-1MB"
# get the file size
filesize = os.path.getsize(filename)
file = open(filename, "rb")


def get_packet(seq_num):
    if str(seq_num) in packets.keys():
        return packets[str(seq_num)]
    else:
        data = file.read(BUFFER_SIZE)
        if not data:
            return None
        data = ("seq=" + str(next_seq_num) + ":data=").encode() + data
        packets[str(next_seq_num)] = data
        return data


def send(next_packet, seq_num):
    # if random.randint(0, 10) > 0:
    # print(
    #     f'Packet Sent with Sequence number is {seq_num,len(next_packet)} at {time.time()}')
    sock.sendto(next_packet, RECEIVER_ADDR)
    # else:
    # print(
    #     f'Packet with Sequence Number {seq_num} going to Lost at {time.time()}')


def send_packet(seq_num, is_retransmission):
    lock.acquire()
    global start_time
    if not is_retransmission:
        global next_seq_num
        next_packet = get_packet(next_seq_num)
        if next_packet == None:
            lock.release()
            return False
        while (next_seq_num - expected_ack_number + len(next_packet)) <= rwnd:
            send(next_packet, next_seq_num)
            next_seq_num += len(next_packet)
            next_packet = get_packet(next_seq_num)
            if next_packet == None:
                lock.release()
                return False
    else:
        packet_resent = get_packet(seq_num)
        send(packet_resent, seq_num)
        start_time = time.time()
    if start_time == -1:
        start_time = time.time()
    lock.release()
    return True


def timer_thread():
    global completed
    while not completed:
        if start_time != -1 and time.time() - start_time > TIMEOUT_INTERVAL:
            #print(f'Resending {expected_ack_number} at {time.time()}')
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
        #print(f'Received Ack {recv_ack} at {time.time()}')
        if recv_ack > expected_ack_number:
            expected_ack_number = recv_ack
            if expected_ack_number == next_seq_num:
                start_time = -1
            else:
                start_time = time.time()

            success = send_packet(None, False)
            if success == False and next_seq_num == expected_ack_number:
                completed = True  # pylint: disable=unused-variable

                return


main_thread()