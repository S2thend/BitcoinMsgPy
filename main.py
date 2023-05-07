SEED_DNS = [
    'bitcoin.seed.memo.cash', 
    'seed.bitcoinstats.com'
]

# Magic bytes, as usual
MAGIC = b'\xf9\xbe\xb4\xd9'
VERACK = b'\xf9\xbe\xb4\xd9\x76\x65\x72\x61\x63\x6b\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x5d\xf6\xe0\xe2'

import socket
import time
import urllib.request
import hashlib

def get_myip():
    myip_str = urllib.request.urlopen('https://api.ipify.org').read().decode()
    myip = socket.inet_aton(myip_str)
    return myip

def version_message(nodeip, myip=get_myip()):
    # Version number (PROTOCOL_VERSION in core)
    version = int(70015).to_bytes(4, 'little')

    # Random services, we don't care
    services = int(1).to_bytes(8, 'little')

    timestamp = int(time.time()).to_bytes(8, 'little')

    addr_recv = services + b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xff\xff'
    addr_recv += nodeip + int(8333).to_bytes(2, 'big')

    addr_from = services + b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xff\xff'
    addr_from += myip + int(8333).to_bytes(2, 'big')
    
    nonce = 0x00.to_bytes(8, 'little')

    # We can replace this with something more fun, e.g. a version string like "/Satoshi:0.8.5/"
    user_agent = 0x00.to_bytes(1, 'big')

    # Block height on my node, zero since we don't have any block information
    start_height = 0x00.to_bytes(4, 'little')

    # The message content, which we'll compute the checksum from
    payload = version + services + timestamp + addr_recv + addr_from + nonce
    payload += user_agent + start_height

    checksum = hashlib.sha256(hashlib.sha256(payload).digest()).digest()[:4]

    return (
        'version'.encode('ascii'),
        checksum,
        payload
    )

def add_headers(command, checksum, payload):
    return MAGIC + command + b'\x00' * (12 - len(command)) + len(payload).to_bytes(4, 'little') + checksum + payload


def receive_messages(sock):
    buffer = b''  # Initialize message buffer
    last_message = None  # Initialize last message variable

    while True:
        data = sock.recv(1024)  # Receive data

        if not data:  # If no data is received, the connection has been closed
            print("Connection closed by remote host")
            break

        buffer += data  # Append new data to the buffer

        # Find the start of the next message
        message_start = buffer.find(b'\xf9\xbe\xb4\xd9')

        while message_start != -1:  # While there are messages in the buffer
            # Find the end of the message
            message_end = buffer.find(b'\xf9\xbe\xb4\xd9', message_start + 4)

            if message_end == -1:  # If the end of the message is not found, break the loop
                break

            message = buffer[message_start:message_end]  # Extract the message
            buffer = buffer[message_end:]  # Remove the message from the buffer

            if last_message is not None:  # If there is a previous message, print it
                print("Previous message:", last_message)

            # Print the new message
            print("New message:", message)

            # Store the last message
            last_message = message

            # Find the start of the next message
            message_start = buffer.find(b'\xf9\xbe\xb4\xd9')

        if message_start == -1 and last_message is not None:  # If there is a previous message, print it
            print("Previous message:", last_message)
            last_message = None

    # If there is a message left in the buffer, print it before exiting
    if len(buffer) > 0:
        print("Last message:", buffer)



if __name__ == '__main__':
    # 查询DNS服务器，获取IP地址
    ips = []
    for dns_seed in SEED_DNS:
        try:
            # 查询DNS服务器，获取IP地址列表
            ip_list = socket.gethostbyname_ex(dns_seed)[2]
            ips.extend(ip_list)
        except Exception as e:
            print("Error querying DNS server", dns_seed, e)
            continue

    # 输出查询到的IP地址
    print("Seed nodes IP addresses:", ips)

    for ip in ips:
        # 创建socket连接
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(2)
        try:
            # 连接到节点
            sock.connect((ip, 8333))
            print("Connected to", ip)
            # 发送version消息
            sock.sendall(add_headers(*version_message(socket.inet_aton(ip))))
            sock.sendall(VERACK)
            # 接收version消息
            print(receive_messages(sock))
        except Exception as e:
            print("Error connecting to", ip, e)
            continue
        finally:
            sock.close()