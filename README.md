# How to start
Implenmented using only standard library, no need for install.

```sh
python main.py
```

* Wait for receipt of new block information. Could take a long time.
* Or uncomment print new message to see every message received.
```py
            # print("New message:", message)
```
## Output Example
```
...
Connected to <ip>
Error connecting to <ip> timed out
Connected to <ip>
Connection closed by remote host
Connected to <ip>
block headers: [{'version': 641589248, 'prev_block': '00000000000000000000ef0ea8f134b141687548baebe2a8f5d60b1203071604', 'merkle_root': 'b67b1f6b40075eadf7b46532f4534149e34baa2316f78816a44b9af438022672', 'timestamp': 1683497187, 'bits': 386260225, 'nonce': 3488487704}]
block headers: [{'version': 641589248, 'prev_block': '00000000000000000000ef0ea8f134b141687548baebe2a8f5d60b1203071604', 'merkle_root': 'b67b1f6b40075eadf7b46532f4534149e34baa2316f78816a44b9af438022672', 'timestamp': 1683497187, 'bits': 386260225, 'nonce': 3488487704}, {'version': 536969216, 'prev_block': '000000000000000000041802d1e36499adfe62219a8fa080ff6a29bfb51145c6', 'merkle_root': '0654a3ed24ec2931dfc73a9a470151d30da56c885c395c88a10477c3b94c00ab', 'timestamp': 1683497376, 'bits': 386260225, 'nonce': 1205314160}]
Connection closed by remote host
...
Connected to <ip>
Connection closed by remote host
Connected to <ip>
block headers: [{'version': 641589248, 'prev_block': '00000000000000000000ef0ea8f134b141687548baebe2a8f5d60b1203071604', 'merkle_root': 'b67b1f6b40075eadf7b46532f4534149e34baa2316f78816a44b9af438022672', 'timestamp': 1683497187, 'bits': 386260225, 'nonce': 3488487704}, {'version': 536969216, 'prev_block': '000000000000000000041802d1e36499adfe62219a8fa080ff6a29bfb51145c6', 'merkle_root': '0654a3ed24ec2931dfc73a9a470151d30da56c885c395c88a10477c3b94c00ab', 'timestamp': 1683497376, 'bits': 386260225, 'nonce': 1205314160}, {'version': 623550464, 'prev_block': '0000000000000000000593b07bbe22e10beaa167806fb92ebdeadd73073baab4', 'merkle_root': 'fc1e2c02b9bee0698fc60b342b5235cd82ad3ab18d878dc5937e3911469be9ec', 'timestamp': 1683497436, 'bits': 386260225, 'nonce': 3423304283}]
Error connecting to <ip> timed out
Connected to <ip>
Connection closed by remote host
...
Connected to <ip>
block headers: [{'version': 641589248, 'prev_block': '00000000000000000000ef0ea8f134b141687548baebe2a8f5d60b1203071604', 'merkle_root': 'b67b1f6b40075eadf7b46532f4534149e34baa2316f78816a44b9af438022672', 'timestamp': 1683497187, 'bits': 386260225, 'nonce': 3488487704}, {'version': 536969216, 'prev_block': '000000000000000000041802d1e36499adfe62219a8fa080ff6a29bfb51145c6', 'merkle_root': '0654a3ed24ec2931dfc73a9a470151d30da56c885c395c88a10477c3b94c00ab', 'timestamp': 1683497376, 'bits': 386260225, 'nonce': 1205314160}, {'version': 623550464, 'prev_block': '0000000000000000000593b07bbe22e10beaa167806fb92ebdeadd73073baab4', 'merkle_root': 'fc1e2c02b9bee0698fc60b342b5235cd82ad3ab18d878dc5937e3911469be9ec', 'timestamp': 1683497436, 'bits': 386260225, 'nonce': 3423304283}, {'version': 543162368, 'prev_block': '000000000000000000013a786fd9532a9a48faf886a576e6ff5d84d84adf8f48', 'merkle_root': 'ad98240e3589724e06836d47b028d57915c81e197f65db849ebbe7f0c774d982', 'timestamp': 1683498298, 'bits': 386260225, 'nonce': 1894048264}]
Connection closed by remote host
...
```



# Message Handling Functions
## version_message(nodeip, myip=get_myip())
Creates a Bitcoin version message.

Args: 
nodeip (bytes): The IP address of the remote node. 
myip (bytes): Optional. The IP address of the local node. Defaults to the local IP address.

Returns:  
tuple: A tuple containing: 
command (bytes): The command ('version'). 
checksum (bytes): The checksum for the payload. 
payload (bytes): The actual version message payload.
## pong_msg(nonce)
Creates a Bitcoin pong message. 

Args: 
nonce (bytes): The nonce to include in the pong message.

Returns:  
tuple: A tuple containing: 
command (bytes): The command ('pong'). 
checksum (bytes): The checksum for the payload. 
payload (bytes): The actual pong message payload containing the nonce.
## parse_inv_message(message)
Parses a Bitcoin inv message.

Args: 
message (bytes): The raw inv message. 

Returns:  
list: A list of tuples containing: 
object type (int): The type of inventory object (block, tx, etc.) 
hash (bytes): The hash of the inventory object.
## getdata_msg(inv,count=1)
Creates a Bitcoin getdata message. 

## parse_block_message(payload)
Parses a raw block message payload.

## big_little_endian(s)
Converts a hexadecimal string from big endian to little endian.  

## getheaders_msg(blockhash)
Creates a Bitcoin getheaders message.

## parse_headers_message(payload) 
Parses a raw headers message payload.

## message_handler(sock)
Handles messages received on the socket.

Args: 
sock (socket): The connected socket.

# TODOs
* implement varint parse and use varint instead of hardcoded byte length
* refactor to use aio or multi thread
* add data store method
* improve UI
