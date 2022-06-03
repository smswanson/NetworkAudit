

def subnet(ip, cidr=24):
    #addr = [0, 0, 0, 0]
    mask = [0, 0, 0, 0]
    cidr = 0
    ipSubnet = ''
    try:
        addr = [int(x) for x in ip.split(".")]
        cidr = int(cidr)
        mask = [(((1 << 32) - 1) << (32 - cidr) >> i) & 255 for i in reversed(range(0, 32, 8))]


        netw = [addr[i] & mask[i] for i in range(4)]
        bcas = [(addr[i] & mask[i]) | (255 ^ mask[i]) for i in range(4)]
        ipSubnet = '.'.join(map(str, addr)) + '/' + cidr
    except:
        pass
        #print(f'{ip}/{cidr}')
    '''print("Address: {0}".format('.'.join(map(str, addr))))
    print("Mask: {0}".format('.'.join(map(str, mask))))
    print("Cidr: {0}".format(cidr))
    print("Network: {0}".format('.'.join(map(str, netw))))
    print("Broadcast: {0}".format('.'.join(map(str, bcas))))'''
    return ipSubnet