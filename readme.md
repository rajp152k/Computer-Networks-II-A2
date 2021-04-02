# RDT for FTP over UDP

*Reliable Data Transfer for transferring files using UDP*

---

# Instructions for use

## Sender 

The sender takes in the following arguments

- recvr_addr : the address of the receiver (default : 10.0.10.2)
- recvr_port : port number of the receiver (default : 8080)
- sendr_addr : the address of the sender   (default : 10.0.10.1)
- sendr_port : port number of the sender   (default : 9090)
- input      : name of the file to be sent over the connection

Sample Usage 

```
python3 sender.py --recvr_addr 10.0.0.254 --sendr_addr 10.0.0.253 --input 'test-1MB'
```

## Receiver 

The receiver takes in only one argument 

- output : name of the file in which the received contents are stored

Sample Usage

```
python3 receiver.py --output 'outfile'
```

### NOTE : receiver should be up and running before the sender code is executed
