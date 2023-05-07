# How to start
Implenmented using only standard library, no need for install.

```sh
python main.py
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
