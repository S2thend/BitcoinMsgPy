SEED_DNS = [
    'bitcoin.seed.memo.cash', 
    'seed.bitcoinstats.com'
]

# Magic bytes, as usual
MAGIC = b'\xf9\xbe\xb4\xd9'
VERACK = b'\xf9\xbe\xb4\xd9\x76\x65\x72\x61\x63\x6b\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x5d\xf6\xe0\xe2'

BLOCK_HEADERS = []

import socket
import time
import urllib.request
import hashlib

def get_myip():
    """
    Returns the IP address of the current machine.
    Fetches the IP address from an external API and returns it as a byte string.
    """
    myip_str = urllib.request.urlopen('https://api.ipify.org').read().decode()
    myip = socket.inet_aton(myip_str)
    return myip

def version_message(nodeip, myip=get_myip()):
    """Creates a Bitcoin version message.
    Args:
        nodeip (bytes): The IP address of the remote node.
        myip (bytes): Optional. The IP address of the local node. Defaults to the local IP address.
    Returns:
        tuple: A tuple containing:
            command (bytes): The command ('version').
            checksum (bytes): The checksum for the payload.
            payload (bytes): The actual version message payload.
    """
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
    """
    Adds command headers to the input payload.
    Args:
        command (bytes): The command to add headers for.
        checksum (bytes): The checksum for the payload.
        payload (bytes): The actual data payload.
    Returns:
        bytes: The payload with command headers added.
    """
    return MAGIC + command + b'\x00' * (12 - len(command)) + len(payload).to_bytes(4, 'little') + checksum + payload

def pong_msg(nonce):
    """Creates a Bitcoin pong message.
    Args:
        nonce (bytes): The nonce to include in the pong message.
    Returns:
        tuple: A tuple containing:
            command (bytes): The command ('pong').
            checksum (bytes): The checksum for the payload.
            payload (bytes): The actual pong message payload containing the nonce.
    """ 
    return add_headers(
        command='pong'.encode('ascii'),
        checksum=hashlib.sha256(hashlib.sha256(nonce).digest()).digest()[:4],
        payload=nonce
    )

def parse_inv_message(message):
    """Parses a Bitcoin inv message.
    Args:
        message (bytes): The raw inv message.
    Returns:
        list: A list of tuples containing:
            object type (int): The type of inventory object (block, tx, etc.)
            hash (bytes): The hash of the inventory object.
    """ 
    # 从消息头的第16-20个字节读取消息长度
    msg_len = int.from_bytes(message[16:20], byteorder='little')

    inventory = []
    # 去掉消息头
    message = message[24:]

    # print("count:",int.from_bytes(message[:1], byteorder='little'))
    message = message[1:]

    i = 0
    # 解析散列值
    while i < len(message):
        obj_type = message[i:i+4]
        hash_value = message[i+4:i+36]
        inventory.append((int.from_bytes(obj_type,byteorder="little"), hash_value))
        i += 36

    return inventory

def getdata_msg(inv,count=1):
    """Creates a Bitcoin getdata message.
    Args:
        inv (list): A list of inventory tuples containing:
            object type (int): The type of inventory object (block, tx, etc.)
            hash (bytes): The hash of the inventory object.
        count (int): The number of inventory objects to request. Defaults to 1.
    Returns:
        tuple: A tuple containing:
            command (bytes): The command ('getdata').
            checksum (bytes): The checksum for the payload.
            payload (bytes): The actual getdata message payload containing the requested inventory objects.
    """ 
    payload = count.to_bytes(1, 'little')
    for i in range(count):
        payload += inv[0].to_bytes(4, 'little')
        payload += inv[1]
    return add_headers(
        command='getdata'.encode('ascii'),
        checksum=hashlib.sha256(hashlib.sha256(payload).digest()).digest()[:4],
        payload=payload
    )

def parse_block_message(payload):
    """Parses a raw block message payload.
    Args:
        payload (bytes): The raw block message payload.
    Returns:
        dict: A dictionary containing:
            version (int): The block version number.
            prev_block (str): The hash of the previous block.
            merkle_root (str): The merkle root hash.
            timestamp (int): The block timestamp.
            bits (int): The target difficulty bits.
            nonce (int): The block nonce.
    """ 
    '''
    4	version	int32_t	Block version information (note, this is signed)
    32	prev_block	char[32]	The hash value of the previous block this particular block references
    32	merkle_root	char[32]	The reference to a Merkle tree collection which is a hash of all transactions related to this block
    4	timestamp	uint32_t	A Unix timestamp recording when this block was created (Currently limited to dates before the year 2106!)
    4	bits	uint32_t	The calculated difficulty target being used for this block
    4	nonce	uint32_t	The nonce used to generate this block… to allow variations of the header and compute different hashes
    '''
    block = {}
    block['version'] = int.from_bytes(payload[:4], byteorder='little')
    block['prev_block'] = big_little_endian(payload[4:36].hex())
    block['merkle_root'] = big_little_endian(payload[36:68].hex())
    block['timestamp'] = int.from_bytes(payload[68:72], byteorder='little')
    block['bits'] = int.from_bytes(payload[72:76], byteorder='little')
    block['nonce'] = int.from_bytes(payload[76:80], byteorder='little')
    return block

def big_little_endian(s):
    """Converts a hexadecimal string from big endian to little endian.
    Args:
        s (str): A hexadecimal string.
    Returns:
        str: The string in little endian byte order.
    """
    result = ''
    for i in range(0, len(s), 2):
        result = s[i] + s[i+1] + result
    return result

def getheaders_msg(blockhash):
    """Creates a Bitcoin getheaders message.
    Args:
        blockhash (str): A block hash.
    Returns:
        tuple: A tuple containing:
            command (bytes): The command ('getheaders').
            checksum (bytes): The checksum for the payload.
            payload (bytes): The actual getheaders message payload containing the block hash.
    """
    # Construct the payload
    version = int(70015).to_bytes(4, 'little')
    num_locator_hashes = b'\x01'
    locator_hashes = bytes.fromhex(blockhash)
    hash_stop = b'\x00' * 32
    payload = version + num_locator_hashes + locator_hashes + hash_stop
    return add_headers(
        command='getheaders'.encode('ascii'),
        checksum=hashlib.sha256(hashlib.sha256(payload).digest()).digest()[:4],
        payload=payload
    )

def parse_headers_message(payload):
    """Parses a raw headers message payload.
    Args:
        payload (bytes): The raw headers message payload.
    Returns:
        list: A list of dictionaries containing:
            version (int): The block version number.
            prev_block (str): The hash of the previous block.
            merkle_root (str): The merkle root hash.
            timestamp (int): The block timestamp.
            bits (int): The target difficulty bits.
            nonce (int): The block nonce.
    """
    # 从payload中解析出块头数量
    payload = payload[1:]

    headers = []
    # 解析每个块头
    while len(payload) > 81:
        # 从payload中读取块头数据
        version = int.from_bytes(payload[0:4], byteorder='little')
        prev_block = payload[4:36]
        merkle_root = payload[36:68]
        timestamp = int.from_bytes(payload[68:72], byteorder='little')
        bits = int.from_bytes(payload[72:76], byteorder='little')
        nonce = int.from_bytes(payload[76:80], byteorder='little')

        # 将块头数据保存为字典
        header = {
            'version': version,
            'prev_block': prev_block.hex(),
            'merkle_root': merkle_root.hex(),
            'timestamp': timestamp,
            'bits': bits,
            'nonce': nonce
        }
        headers.append(header)

        # 更新payload数据
        payload = payload[81:]

    return headers

# TODO: Implement this function
# def read_varint(payload):
#     """
#     从payload中读取varint值并返回（varint值，剩余的payload数据）元组。
#     """
#     size = payload[0:1]
#     if size < 0xfd:
#         return size, payload[1:]
#     elif size == 0xfd:
#         return int.from_bytes(payload[1:3], byteorder='little'), payload[3:]
#     elif size == 0xfe:
#         return int.from_bytes(payload[1:5], byteorder='little'), payload[5:]
#     else:
#         return int.from_bytes(payload[1:9], byteorder='little'), payload[9:]


def message_handler(sock):
    """Handles messages received on the socket.
    Args:
        sock (socket): The connected socket.
    """ 
    buffer = b''  # Initialize message buffer

    while True:
        data = sock.recv(1024)  # Receive data

        if not data:  # If no data is received, the connection has been closed
            print("Connection closed by remote host")
            break

        buffer += data  # Append new data to the buffer

        # Find the start of the next message
        message_start = 0

        while message_start != -1:  # While there are messages in the buffer
            # Find the end of the message
            message_end = buffer.find(b'\xf9\xbe\xb4\xd9', message_start + 4)

            if message_end == -1:  # If the end of the message is not found, break the loop
                break

            message = buffer[message_start:message_end]  # Extract the message
            buffer = buffer[message_end:]  # Remove the message from the buffer

            # Print the new message
            # print("New message:", message)

            if message.find(b'ping') != -1:
                sock.sendall(pong_msg(message[24:32]))
            elif message.find(b'inv') != -1:
                invs = parse_inv_message(message)
                # print("inv list:", invs)
                for inv in invs:
                    if inv[0] == 2:
                        sock.sendall(getdata_msg(inv))
            elif message.find(b'getblocks') != -1:
                pass
            elif message.find(b'merkleblock') != -1:
                pass
            elif message.find(b'cmpctblock') != -1:
                pass
            elif message.find(b'getblocktxn') != -1:
                pass
            elif message.find(b'blocktxn') != -1:
                pass
            elif message.find(b'block') != -1:
                block_header = parse_block_message(message[24:])
                BLOCK_HEADERS.append(block_header)
                print("block headers:", BLOCK_HEADERS)
            elif message.find(b'getheaders') != -1:
                pass
            elif message.find(b'sendheaders') != -1:
                pass
            elif message.find(b'headers') != -1:
                headers = parse_headers_message(message[24:])
                # print("headers:", headers)


    # If there is a message left in the buffer, print it before exiting
    if len(buffer) > 0:
        pass
        # print("Last message:", buffer)



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

    while True:
        for ip in ips:
            # 创建socket连接
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(20)
            try:
                # 连接到节点
                sock.connect((ip, 8333))
                print("Connected to", ip)
                # 发送version消息
                sock.sendall(add_headers(*version_message(socket.inet_aton(ip))))
                sock.sendall(VERACK)
                # sock.sendall(getheaders_msg(big_little_endian('00000000000000000000e3ef748217eba564fb5075e6f18fc7cbfc98db5ea844')))
                # 接收version消息
                message_handler(sock)
            except Exception as e:
                print("Error connecting to", ip, e)
                continue
            finally:
                sock.close()