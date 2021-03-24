# plan

## Basics: 

 - Connectionless
 - Connection oriented : 3-way handshake

## Sender
 - initiate connection
 - Main sender thread
 - Ack thread
    - with timer : curr time - last ack recv.
        - upon expiry, communicate to sender thread for retransmission
        - if ack recv : communicate to sender to send next packets
        - upon last ack : terminate client and sender thread.

## Recvr
 - connection establishment
 - process recvd packet(ack and seq no.)
 - decide to buffer/deliver
    - send cumulative ack

### MISC
 - TCP  : fast retransmit upon 3 duplicate acks
 - latter priority : flow control : account for recvr buffer
 - congenstion control : slow starts and cuts when drop/loss
 - dynamic timer : RTT and deviation using past stats
