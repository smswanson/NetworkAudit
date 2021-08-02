from pprint import pprint

# region Define object Keylists Used for building tables and writing to Excel
nxosDeviceKeylist = [{'name': {'data': 'host_name', 'hl': 'Hostname'}},
                     {'serial': {'data': 'proc_board_id', 'hl': 'S/N'}},
                     {'version': {'data': 'kickstart_ver_str', 'hl': 'Version'}},
                     {'chassis': {'data': 'chassis_id', 'hl': 'Chassis'}},
                     {'uptime': {'data': 'uptime', 'hl': 'Uptime'}}]

nxosVlanKeylist = [{'name': {'data': 'vlanshowbr-vlanname', 'hl': 'VLAN Name'}},
                   {'vlanid': {'data': 'vlanshowbr-vlanid', 'hl': 'VLAN ID'}},
                   {'ip': {'data': 'prefix', 'hl': 'IP Address'}},
                   {'state': {'data': 'vlanshowbr-vlanstate', 'hl': 'State'}},
                   {'shutstate': {'data': 'vlanshowbr-shutstate', 'hl': 'Shutdown State'}},
                   {'tree_protocol': {'data': 'tree_protocol', 'hl': 'STP Protocol'}},
                   {'root': {'data': 'root', 'hl': 'Root Bridge'}},
                   {'bridge_mac': {'data': 'bridge_mac', 'hl': 'Bridge MAC'}},
                   {'bridge_priority': {'data': 'bridge_priority', 'hl': 'Bridge Priority'}},
                   {'tree_designated_root': {'data': 'tree_designated_root', 'hl': 'Root MAC'}},
                   {'designated_root_priority': {'data': 'designated_root_priority', 'hl': 'Root Priority'}},
                   {'topology_change_time_since_last': {'data': 'topology_change_time_since_last',
                                                        'hl': 'Last Change (s)'}}
                   ]

#Port-map final write
nxosIntKeylist = [{'interface': {'data': 'interface', 'hl': 'Interface'}},
                  {'name': {'data': 'name', 'hl': 'Description'}},
                  {'vlan': {'data': 'vlan', 'hl': 'Routed/VLAN'}},
                  {'state': {'data': 'state', 'hl': 'State'}},
                  {'speed': {'data': 'speed', 'hl': 'Speed'}},
                  {'ip': {'data': 'ip', 'hl': 'IP Address'}},
                  {'mtu': {'data': 'mtu', 'hl': 'MTU'}},
                  {'vrf_name': {'data': 'vrf_name', 'hl': 'VRF'}},
                  {'type': {'data': 'type', 'hl': 'Type'}},
                  {'device_id': {'data': 'device_id', 'hl': 'Neighbor Device'}},
                  {'platform_id': {'data': 'platform_id', 'hl': 'Platform'}},
                  {'port_id': {'data': 'port_id', 'hl': 'Neighbor Port'}},
                  ]

nxosIPIntKeylist = [{'interface': {'data': 'intf-name', 'hl': 'Interface'}},
                    {'ip': {'data': 'prefix', 'hl': 'IP Address'}},
                    {'mtu': {'data': 'mtu', 'hl': 'MTU'}},
                    {'proto-state': {'data': 'proto-state', 'hl': 'Protocol State'}},
                    {'admin-state': {'data': 'admin-state', 'hl': 'Admin State'}}]

nxosVrfIntKeylist = [{'interface': {'data': 'if_name', 'hl': 'Interface'}},
                     {'vrf_name': {'data': 'vrf_name', 'hl': 'VRF'}}]

nxosCDPKeylist = [{'interface': {'data': 'intf_id', 'hl': 'Interface'}},
                  {'device_id': {'data': 'device_id', 'hl': 'Neighbor Device'}},
                  {'platform_id': {'data': 'platform_id', 'hl': 'Platform'}},
                  {'port_id': {'data': 'port_id', 'hl': 'Neighbor Port'}}]

#todo LLDP Keys need to be identified
nxosLLDPKeylist = [{'interface': {'data': 'intf_id', 'hl': 'Interface'}},
                  {'device_id': {'data': 'device_id', 'hl': 'Neighbor Device'}},
                  {'platform_id': {'data': 'platform_id', 'hl': 'Platform'}},
                  {'port_id': {'data': 'port_id', 'hl': 'Neighbor Port'}}]

nxosVRFKeylist = [{'vrf_name': {'data': 'vrf_name', 'hl': 'VRF'}},
                  {'vrf_id': {'data': 'vrf_id', 'hl': 'VRF ID'}},
                  {'vrf_state': {'data': 'vrf_state', 'hl': 'VRF State'}},
                  {'vrf_reason': {'data': 'vrf_reason', 'hl': 'VRF Reason'}}]

nxosRouteKeylist = [{'ipprefix': {'data': 'ipprefix', 'hl': 'IP Prefix'}},
                    {'ifname': {'data': 'ifname', 'hl': 'Interface'}},
                    {'ipnexthop': {'data': 'ipnexthop', 'hl': 'IP Next Hop'}},
                    {'pref': {'data': 'pref', 'hl': 'Preference'}},
                    {'metric': {'data': 'metric', 'hl': 'Metric'}},
                    {'uptime': {'data': 'uptime', 'hl': 'Uptime'}},
                    {'ucast-nhops': {'data': 'ucast-nhops', 'hl': 'Unicast Hops'}},
                    {'attached': {'data': 'attached', 'hl': 'Attached'}},
                    {'clientname': {'data': 'clientname', 'hl': 'Client'}},
                    {'ubest': {'data': 'ubest', 'hl': 'ubest'}},
                    ]

nxosSTPKeylist = [{'tree_id': {'data': 'tree_id', 'hl': 'VLAN'}},
                  {'tree_protocol': {'data': 'tree_protocol', 'hl': 'STP Protocol'}},
                  {'tree_designated_root': {'data': 'tree_designated_root', 'hl': 'Root'}},
                  {'bridge_priority': {'data': 'bridge_priority', 'hl': 'Bridge Priority'}},
                  {'bridge_mac': {'data': 'bridge_mac', 'hl': 'Bridge MAC'}},
                  {'designated_root_priority': {'data': 'designated_root_priority', 'hl': 'Root Priority'}},
                  {'topology_change_time_since_last': {'data': 'topology_change_time_since_last', 'hl': 'Last Change'}}
                  ]

nxosBGPVRFKeylist = [{'vrf-name-out': {'data': 'vrf-name-out', 'hl': 'VRF'}},
                     {'vrf-router-id': {'data': 'vrf-router-id', 'hl': 'BGP Router ID'}},
                     {'vrf-local-as': {'data': 'vrf-local-as', 'hl': 'Local-AS'}},
                     ]


root = ''
#endregion

def mergeObj(obj1, obj1attr, obj2, obj2attr, list):
    if hasattr(obj1, obj1attr) and hasattr(obj2, obj2attr):
        o1 = getattr(obj1, obj1attr)
        o2 = getattr(obj2, obj2attr)
        if o1 == o2:
            for a in list:
                try:
                    setattr(obj1, a, getattr(obj2, a))
                except:
                    pass


def copyAttr(obj1, obj2, list):
    for a in list:
        if a == 'keylist':
            pass
        else:
            setattr(obj1, a, getattr(obj2, a))

def getKeys(dict): # Get keys from dictionary
    list = []
    for a in dict.keys():
        list.append(a)
    return list

def getKeyslist(listdict): # Get keys from list of dictionaries
    list = []
    try:
        for a in listdict:
            b = getKeys(a)
            list = list + b
    except:
        print('Failed to get list of dictionary keys')
    return list



def initAttr(obj):
    # Initialize variables based on key list
    for a in obj.keylist:
        a_key = a.keys()
        for b in a_key:
            b_key = b
        try:
            d = a[b_key]['data']
            setattr(obj, b_key, obj.data[d])
        except:
            setattr(obj, b_key, '')

def item2list(item):
    if type(item) is list:
        itemlist = item
    else:
        itemlist = [item]
    return itemlist

class nxosDevice:
    # Cisco Nexus Device
    def __init__(self, json_data):
        self.keylist = nxosDeviceKeylist
        # process uptime
        try:
            time = json_data['show_version']['kern_uptm_hrs'] + ':' + \
                   json_data['show_version']['kern_uptm_mins'] + ':' + \
                   json_data['show_version']['kern_uptm_secs']
        except:
            time = ''
        try:
            uptime = json_data['show_version']['kern_uptm_days'] + ', ' + time
        except:
            uptime = ''
        json_data['show_version'].update({'uptime': uptime})
        self.data = json_data
        self.name = json_data['show_hostname']['hostname']
        self.serial = json_data['show_version']['proc_board_id']
        self.version = json_data['show_version']['kickstart_ver_str']
        self.chassis = json_data['show_version']['chassis_id']
        self.uptime = time
        self.eth = []
        self.portchannel = []
        self.lo = []
        self.vlanInt = []
        self.vlan = []
        self.nve = []
        self.miscInt = []
        self.mgmt = []


    def getVlans(self):
        '''try: # Create Interface Objects'''
        for a in self.data['show_vlan']['TABLE_vlanbrief']['ROW_vlanbrief']:
            vl = nxosSubObj(a, nxosVlanKeylist)
            setattr(vl, 'root', 'none')
            for b in self.vlanInt:
                vlanIntId = b.interface.lstrip('Vlan')
                if vl.vlanid == vlanIntId:
                    setattr(vl, 'vlanInt', b)
            self.vlan.append(vl)
        '''except:
            print('VLANs Issues')'''
        #try: # Get spanning-tree Information
        stpmerge = getKeyslist(nxosSTPKeylist)
        '''try:
            pprint(self.data['show_spanningtree']['TABLE_tree']['ROW_tree'])
        except:
            pass'''
        try:
            stplist = item2list(self.data['show_spanningtree']['TABLE_tree']['ROW_tree'])
        except:
            stplist = []
        '''try:'''
        if stplist == []:
            pass
        else:
            '''try:'''
            for a in stplist:
                vlanobj = nxosSubObj(a, nxosSTPKeylist)
                if hasattr(self, 'vlan'):
                    for vl in self.vlan:
                        mergeObj(vl, 'vlanid', vlanobj, 'tree_id', stpmerge)
                        # Set Root
                        try:
                            if vl.bridge_mac == vl.tree_designated_root:
                                setattr(vl, 'root', self.name)
                            else:
                                setattr(vl, 'root', vl.tree_designated_root)
                        except:
                            setattr(vl, 'root', 'none')
        if hasattr(self, 'vlanInt'): # Perform some checks
            if self.vlanInt != []:
                if hasattr(self, 'vlan'):  # Perform some checks
                    if self.vlan != []:
                        for a in self.vlanInt:
                                for b in self.vlan:
                                    intname = a.interface.lstrip('Vlan')
                                    if intname == b.vlanid:
                                        setattr(b, 'ip', a.ip)





            '''except:
                print('Failed to add Spanning-Tree information')'''

    def getSTP(self):
        stplist = item2list(self.data['show_spanningtree_']['TABLE_tree']['ROW_tree'])
        for a in stplist:
            vlanobj = nxosSubObj(a, nxosSTPKeylist)


    def getInterfaces(self):
        #try:
        for a in self.data['show_int_status']['TABLE_interface']['ROW_interface']:
            int = nxosSubObj(a, nxosIntKeylist)
            # Sort Interfaces Ethernet, Loopback, Vlan, nve, etc.
            if 'Eth' in int.interface:
                self.eth.append(int)
            elif 'port-channel' in int.interface:
                self.portchannel.append(int)
            elif 'Vlan' in int.interface:
                self.vlanInt.append(int)
            elif 'loopback' in int.interface:
                self.lo.append(int)
            elif 'nve' in int.interface:
                self.nve.append(int)
            elif 'mgmt' in int.interface:
                self.mgmt.append(int)
            else:
                self.miscInt.append(int)
                print(f'Found undefined Interface {int.interface}')
        nxosIntObj(self, self.data['show_ip_int']['TABLE_intf'], nxosIPIntKeylist, extendedkey='ROW_intf')
        nxosIntObj(self, self.data['show_vrf_interface']['TABLE_if']['ROW_if'], nxosVrfIntKeylist)
        try:
            nxosIntObj(self, self.data['show_cdp_nei']['TABLE_cdp_neighbor_brief_info']['ROW_cdp_neighbor_brief_info'],
                       nxosCDPKeylist)
        except:
            pass


    def getVRF(self):
        vrflist = []
        setattr(self, 'vrf', [])
        for a in self.data['show_vrf']['TABLE_vrf']['ROW_vrf']:
            vrfobj = nxosSubObj(a, nxosVRFKeylist)
            self.vrf.append(vrfobj)

    def getRoute(self):
        for a in self.vrf:
            routelist= []
            for b in self.data['show_ip_route']['TABLE_vrf']['ROW_vrf']:
                if a.vrf_name == b['vrf-name-out']:
                    try:
                        for c in b['TABLE_addrf']['ROW_addrf']['TABLE_prefix']['ROW_prefix']:
                            routeobj = nxosSubObj(c, nxosRouteKeylist)
                            p = c['TABLE_path']['ROW_path']
                            paths = item2list(p)
                            for rt in paths:
                                routesubobj = nxosSubObj(rt, nxosRouteKeylist)
                                for d in nxosRouteKeylist:
                                    k = d.keys()
                                    for e in k:  # Return the key
                                        f = e
                                    attr1 = ''
                                    attr2 = ''
                                    try:
                                        attr1 = getattr(routeobj, f)
                                        attr2 = getattr(routesubobj, f)
                                    except:
                                        pass
                                    if attr1 == '':
                                        if attr2 != '':
                                            setattr(routeobj, f, attr2)
                                        else:
                                            pass
                                    else:
                                        pass
                                routelist.append(routeobj)
                        setattr(a, 'routes', routelist)
                    except:
                        print(f'FAILED to find route for {a.vrf_name}')
                        routelist = []


    def getBGP(self):
        TABLE_vrf = self.data['show_bgp_all_summary']['TABLE_vrf']
        ROW_vrf = 'ROW_vrf'
        TABLE_list = item2list(TABLE_vrf)
        setattr(self, 'bgp', [])
        for a in TABLE_list:
            ROW_list = item2list(a[ROW_vrf])
            for b in ROW_list:
                bgpvrf = nxosSubObj(b, nxosBGPVRFKeylist)
                self.bgp.append(bgpvrf)



    def newattr(self, key, attrlist):
        for a in attrlist:
            try:
                for b in a.keys():
                    c = a[b]['data']
                    new = self.data[key][c]
                setattr(self, b, new)
            except:
                print(f'Failed to find Key {a} in {key}')


def nxosIntObj(obj1, data, keylist, extendedkey = 'none'):
    if type(data) is list:
        z = data
    else:
        z = data[extendedkey]

    for a in data:
        if extendedkey != 'none':
            z = a[extendedkey]
        else:
            z = a
    nxosObj = nxosSubObj(z, keylist)
    tmp_list = vars(nxosObj)
    listkeys = tmp_list.keys()
    if 'Eth' in nxosObj.interface:
        for b in obj1.eth:
            if b.interface == nxosObj.interface:
                copyAttr(b, nxosObj, listkeys)
    elif 'port-channel' in nxosObj.interface:
        for b in obj1.portchannel:
            if b.interface == nxosObj.interface:
                copyAttr(b, nxosObj, listkeys)
    elif 'Vlan' in nxosObj.interface:
        for b in obj1.vlanInt:
            if b.interface == nxosObj.interface:
                copyAttr(b, nxosObj, listkeys)
    elif 'loopback' in nxosObj.interface:
        for b in obj1.lo:
            if b.interface == nxosObj.interface:
                copyAttr(b, nxosObj, listkeys)
    elif 'nve' in nxosObj.interface:
        for b in obj1.nve:
            if b.interface == nxosObj.interface:
                copyAttr(b, nxosObj, listkeys)
    elif 'mgmt' in nxosObj.interface:
        for b in obj1.mgmt:
            if b.interface == nxosObj.interface:
                copyAttr(b, nxosObj, listkeys)
    else:
        obj1.miscInt.append(nxosObj)
        print(f'Found undefined Interface IP {nxosObj.interface}')
    '''except:
        print(f'Get Interface failed for {self.name}')'''

class nxosSubObj:
    # Cisco Nexus Interface
    def __init__(self, json_data, keylist):
        self.keylist = keylist
        self.data = json_data
        initAttr(self)

class nxosSubObjList:
    def __init__(self, json_data, keylist):
        self.keylist = keylist
        self.data = json_data
        initAttr(self)


class nxosObj:
    def __init__(self, json_data, table, row, keylist):
        self.keylist = keylist
        self.data = json_data
        initAttr(self)

class xlsxObj:
    def __init__(self, json_data):
        pass


class vrf:
    def __init__(self, json_data):
        routes = []
        self.data = json_data



class route:
    def __init__(self, json_data, keylist):
        self.keylist = keylist
        self.data = json_data
        initAttr(self)


def nxosBuildDevice(json_data):
    device = nxosDevice(json_data)
    device.getInterfaces()
    device.getVlans()
    device.getVRF()
    device.getRoute()
    device.getBGP()
    return device







