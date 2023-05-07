SEED_DNS = [
    'bitcoin.seed.memo.cash', 
    'seed.bitcoinstats.com'
]

# Magic bytes, as usual
MAGIC = b'\xf9\xbe\xb4\xd9'

import socket







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