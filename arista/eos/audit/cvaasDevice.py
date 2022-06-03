from pprint import pprint
from operator import itemgetter
import utilities.subnet as subnet
import ipcalc
import re
# region Define object Keylists Used for building tables and writing to Excel
cvDeviceKeylist =  [{'name': {'data': 'hostname', 'hl': 'Hostname'}},
                    {'ipAddress': {'data': 'ipAddress', 'hl': 'Mgmt IP'}},
                    {'serial': {'data': 'serialNumber', 'hl': 'S/N'}},
                    {'version': {'data': 'version', 'hl': 'Version'}},
                    {'model': {'data': 'modelName', 'hl': 'Model'}},
                    {'containerName': {'data': 'containerName', 'hl': 'Container'}},
                    {'mac': {'data': 'systemMacAddress', 'hl': 'System MAC'}},
                    {'deviceStatus': {'data': 'deviceStatus', 'hl': 'Status'}},
                    {'streamingStatus': {'data': 'streamingStatus', 'hl': 'Streaming'}},
                    {'complianceCode': {'data': 'complianceCode', 'hl': 'Compliance Code'}},
                    {'ztp': {'data': 'ztpMode', 'hl': 'ZTP Mode'}}]

cvConfigletKeylist = [{'name': {'data': 'name', 'hl': 'Configlet Name'}},
                      {'containerCount': {'data': 'containerCount', 'hl': 'Container Count'}},
                      {'netElementCount': {'data': 'netElementCount', 'hl': 'Device Count'}},
                      {'note': {'data': 'note', 'hl': 'Notes'}},
                      {'type': {'data': 'type', 'hl': 'Type'}},
                      {'typeStudioConfiglet': {'data': 'typeStudioConfiglet', 'hl': 'Studio Configlet'}},
                      {'reconciled': {'data': 'reconciled', 'hl': 'Reconciled'}},
                      ]
cvContainerKeylist = [{'name': {'data': 'Name', 'hl': 'Container Name'}},
                      {'parentName': {'data': 'parentName', 'hl': 'Parent Name'}},]

#Port-map final write
eosIntKeylist = [{'interface': {'data': 'name', 'hl': 'Interface'}},
                 {'hardware': {'data': 'hardware', 'hl': 'Int HW'}},
                  {'description': {'data': 'description', 'hl': 'Description'}},
                  {'mode': {'data': 'mode', 'hl': 'Mode'}},
                  {'state': {'data': 'interfaceStatus', 'hl': 'State'}},
                  {'bandwidth': {'data': 'bandwidth', 'hl': 'Speed'}},
                  {'ip': {'data': 'ip', 'hl': 'IP Address'}},
                  {'varp': {'data': 'varp', 'hl': 'VARP'}},
                  {'mtu': {'data': 'mtu', 'hl': ' MTU '}},
                  {'vrf': {'data': 'vrf', 'hl': 'VRF'}},
                  {'mac': {'data': 'physicalAddress', 'hl': 'MAC'}},
                  {'type': {'data': 'type', 'hl': 'Type'}},
                  {'vendorSn': {'data': 'vendorSn', 'hl': 'Transceiver S/N'}},
                  {'neighbor': {'data': 'neighbor', 'hl': 'Neighbor Device'}},
                  {'neighborPort': {'data': 'neighborPort', 'hl': 'Neighbor Port'}},
                  ]

eosIPIntKeylist = [{'interface': {'data': 'intf-name', 'hl': 'Interface'}},
                    {'ip': {'data': 'prefix', 'hl': 'IP Address'}},
                    {'mtu': {'data': 'mtu', 'hl': 'MTU'}},
                    {'proto-state': {'data': 'proto-state', 'hl': 'Protocol State'}},
                    {'admin-state': {'data': 'admin-state', 'hl': 'Admin State'}}]

eosVrfIntKeylist = [{'interface': {'data': 'if_name', 'hl': 'Interface'}},
                     {'vrf_name': {'data': 'vrf_name', 'hl': 'VRF'}}]

eosCDPKeylist = [{'interface': {'data': 'intf_id', 'hl': 'Interface'}},
                  {'device_id': {'data': 'device_id', 'hl': 'Neighbor Device'}},
                  {'platform_id': {'data': 'platform_id', 'hl': 'Platform'}},
                  {'port_id': {'data': 'port_id', 'hl': 'Neighbor Port'}}]

#todo LLDP Keys need to be identified
eosLLDPKeylist = [{'interface': {'data': 'intf_id', 'hl': 'Interface'}},
                  {'neighbor': {'data': 'neighbor', 'hl': 'LLDP Neighbor'}},
                  {'neighborPort': {'data': 'neighborPort', 'hl': ' LLDP Port'}},
                 ]

eosVRFKeylist = [{'vrf_name': {'data': 'vrf_name', 'hl': 'VRF'}},
                  {'vrf_id': {'data': 'vrf_id', 'hl': 'VRF ID'}},
                  {'vrf_state': {'data': 'vrf_state', 'hl': 'VRF State'}},
                  {'vrf_reason': {'data': 'vrf_reason', 'hl': 'VRF Reason'}}]

eosRouteKeylist = [{'ipprefix': {'data': 'ipprefix', 'hl': 'IP Prefix'}},
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

eosSTPKeylist = [{'tree_id': {'data': 'tree_id', 'hl': 'VLAN'}},
                  {'tree_protocol': {'data': 'tree_protocol', 'hl': 'STP Protocol'}},
                  {'tree_designated_root': {'data': 'tree_designated_root', 'hl': 'Root'}},
                  {'bridge_priority': {'data': 'bridge_priority', 'hl': 'Bridge Priority'}},
                  {'bridge_mac': {'data': 'bridge_mac', 'hl': 'Bridge MAC'}},
                  {'designated_root_priority': {'data': 'designated_root_priority', 'hl': 'Root Priority'}},
                  {'topology_change_time_since_last': {'data': 'topology_change_time_since_last', 'hl': 'Last Change'}}
                  ]

eosBGPVRFKeylist = [{'vrf-name-out': {'data': 'vrf-name-out', 'hl': 'VRF'}},
                     {'vrf-router-id': {'data': 'vrf-router-id', 'hl': 'BGP Router ID'}},
                     {'vrf-local-as': {'data': 'vrf-local-as', 'hl': 'Local-AS'}},
                     ]


root = ''
#endregion
def formatNumber(num):
  if num % 1 == 0:
    return int(num)
  else:
    return num

def atof(text):
    try:
        retval = float(text)
    except ValueError:
        retval = text
    return retval

def natural_keys(text):
    '''
    alist.sort(key=natural_keys) sorts in human order
    http://nedbatchelder.com/blog/200712/human_sorting.html
    (See Toothy's implementation in the comments)
    float regex comes from https://stackoverflow.com/a/12643073/190597
    '''
    return [ atof(c) for c in re.split(r'[+-]?([0-9]+(?:[.][0-9]*)?|[.][0-9]+)', text) ]

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

class cvDevice:
    # Cisco Nexus Device
    def __init__(self, json_data):
        self.keylist = cvDeviceKeylist
        # process uptime
        self.data = json_data
        #self.config = json_data['config']
        self.eth = []
        self.portchannel = []
        self.lo = []
        self.vlanInt = []
        self.vlan = []
        self.nve = []
        self.miscInt = []
        self.mgmt = []
        initAttr(self)

    def getConfigletsAppied(self, client):
        configlets = client.api.get_configlets_by_device_id(self.mac)
        setattr(self, 'configlets', configlets)

    def getRunningConfig(self, client):
        cfg = client.api.get_device_configuration(self.mac)
        setattr(self, 'config', cfg)

    def getVlans(self):
        '''try: # Create Interface Objects'''
        data = self.data['show_vlan']['vlans']
        keys = getKeys(data)
        keys.sort(key=natural_keys)
        vlan_list = []
        for a in keys:
            print('Getting Vlans')
            data[a]['vlanid'] = str(a)
            #try:
            vlan_int = 'Vlan' + str(a)
            try:
                int_bri = self.data['show_ip_int']['interfaces'][vlan_int]['interfaceAddress']
            except:
                print(f'No interface {vlan_int}')
            #try:
            print("TESTING TESTING")
            data[a]['ip'] = int_bri['primaryIp']['address']
            data[a]['mask'] = int_bri['primaryIp']['maskLen']
            testSubnet = ipcalc.Network(data[a]['ip'], data[a]['mask'])
            print(f'testSubnet: {testSubnet.subnet()}')
            #except:
                #print('No IP Data')
            try:
                data[a]['vrf'] = self.data['show_ip_int']['interfaces'][vlan_int]['vrf']
            except:
                print(f'No vrf data {vlan_int}')
            #except:
            #    data[a]['ip'] = ' - '



            vl = eosObj(data[a], eosVlanKeylist)
            vlan_list.append(vl)
        self.vlan = vlan_list


    def getSTP(self):
        stplist = item2list(self.data['show_spanningtree_']['TABLE_tree']['ROW_tree'])
        for a in stplist:
            vlanobj = eosSubObj(a, eosSTPKeylist)

    def getVlanInterfaces(self):
        # Non-physical
        data = self.data['show_ip_int']['interfaces']
        keys = getKeys(data)
        keys.sort(key=natural_keys)
        for a in keys:
            if 'Vlan' in a:
                data[a]['intf-name'] = a
                # Convert BW
                #try:
                int_bri = data[a]['interfaceAddress']
                data[a]['ip'] = int_bri['primaryIp']['address'] + '/' + str(int_bri['primaryIp']['maskLen'])
                #except:
                #    data[a]['ip'] = ''
                for b in self.data['show_ip_varp']['virtualRouters']:
                    if a == b['interface']:
                        tmp_ip = []
                        try:
                            for c in b['virtualIps']:
                                tmp_ip.append(c['ip'])
                            data[a]['varp'] = ','.join(tmp_ip)
                        except:
                            data[a]['varp'] = ''
                int = eosObj(data[a], eosIntKeylist)
                self.vlanInt.append(int)



    def getInterfaces(self):
        data = self.data['show_int']['interfaces']
        keys = getKeys(data)
        keys.sort(key=natural_keys)
        for a in keys:
            tmp = data[a]['bandwidth']
            try:
                tmp_out = float(tmp)/1000000000
                tmp_out = formatNumber(tmp_out)
                bw = str(tmp_out) + 'G'
                data[a]['bandwidth'] = bw
            except:
                pass
            ### Add S/N for Transceiver
            try:
                data[a]['vendorSn'] = self.data['show_interface_transceiver']['interfaces'][a]['vendorSn']
            except:
                data[a]['venderSN'] = ' - '
            # Get VLAN Mode
            try:
                data[a]['type'] = self.data['show_int_status']['interfaceStatuses'][a]['interfaceType']
                vlanInfo = self.data['show_int_status']['interfaceStatuses'][a]['vlanInformation']

                if 'interfaceForwardingModel' in vlanInfo:
                    if vlanInfo['interfaceForwardingModel'] == 'dataLink':
                        data[a]['mode'] = vlanInfo['vlanExplanation']
                    elif vlanInfo['interfaceForwardingModel'] == 'bridged':
                        if vlanInfo['interfaceMode'] == 'bridged':
                            data[a]['mode'] = str(vlanInfo['vlanId']) + ' (Access)'
                        elif vlanInfo['interfaceMode'] == 'trunk':
                            data[a]['mode'] = 'trunk'
                        else:
                            data[a]['mode'] = data[a]['forwardingModel']
                    else:
                        data[a]['mode'] = data[a]['forwardingModel']
                else:
                    data[a]['mode'] = data[a]['forwardingModel']
            except:
                try:
                    data[a]['mode'] = data[a]['forwardingModel']
                except:
                    data[a]['mode'] = ' - '
            # Add IP address
            try:
                int_bri = self.data['show_ip_int']['interfaces'][a]['interfaceAddress']
                data[a]['ip'] = int_bri['primaryIp']['address'] + '/' + str(int_bri['primaryIp']['maskLen'])
            except:
                data[a]['ip'] = ' - '
            # Add LLDP Neighbor
            try:
                for b in self.data['show_lldp_nei']['lldpNeighbors']:
                    if a == b['port']:
                        data[a]['neighbor'] = b['neighborDevice']
                        data[a]['neighborPort'] = b['neighborPort']
            except:
                data[a]['neighbor'] = ' - '
                data[a]['neighborPort'] = ' - '
            # Add VARP Information
            for b in self.data['show_ip_varp']['virtualRouters']:
                if a == b['interface']:
                    tmp_ip = []
                    try:
                        for c in b['virtualIps']:
                            tmp_ip.append(c['ip'])
                        data[a]['varp'] = ','.join(tmp_ip)
                    except:
                        data[a]['varp'] = ' - '
            # Create Interface Object
            int = eosObj(data[a], eosIntKeylist)

            # Sort Interfaces Ethernet, Loopback, Vlan, nve, etc.
            if 'Ethernet' in int.interface:
                self.eth.append(int)
            elif 'Port-Channel' in int.interface:
                self.portchannel.append(int)
            elif 'Vlan' in int.interface:
                self.vlanInt.append(int)
            elif 'Loopback' in int.interface:
                self.lo.append(int)
            elif 'nve' in int.interface:
                self.nve.append(int)
            elif 'Management' in int.interface:
                self.mgmt.append(int)
            else:
                self.miscInt.append(int)
                print(f'Found undefined Interface {int.interface}')

    def getInterfaces2(self):
        #try:
        data = self.data['show_int_status']['interfaceStatuses']
        keys = getKeys(self.data['show_int_status']['interfaceStatuses'])
        keys.sort(key=natural_keys)
        self.getVlanInterfaces()
        for a in keys:
            data[a]['intf-name'] = a
            # Convert BW
            tmp = data[a]['bandwidth']
            tmp_out = float(tmp)/1000000000
            tmp_out = formatNumber(tmp_out)
            bw = str(tmp_out) + 'G'
            data[a]['bandwidth'] = bw
            try:
                data[a]['vendorSn'] = self.data['show_interface_transceiver']['interfaces'][a]['vendorSn']
            except:
                data[a]['venderSN'] = 'n/a'
            vlanInfo = data[a]['vlanInformation']
            if 'interfaceForwardingModel' in vlanInfo:
                if vlanInfo['interfaceForwardingModel'] == 'dataLink':
                    data[a]['vlan'] = vlanInfo['vlanExplanation']
                elif vlanInfo['interfaceForwardingModel'] == 'bridged':
                    if vlanInfo['interfaceMode'] == 'bridged':
                        data[a]['vlan'] = str(vlanInfo['vlanId']) + '( Access)'
                    elif vlanInfo['interfaceMode'] == 'trunk':
                        data[a]['vlan'] = 'trunk'
                    else:
                        data[a]['vlan'] = 'N/A'
                elif vlanInfo['interfaceForwardingModel'] == 'routed':
                    data[a]['vlan'] = 'routed'
                else:
                    data[a]['vlan'] = 'N/A'
            int_bri = self.data['show_ip_int']['interfaces'][a]['interfaceAddress']
            try:
                data[a]['ip'] = int_bri['primaryIp']['address'] + '/' + str(int_bri['primaryIp']['maskLen'])
            except:
                data[a]['ip'] = ''
            try:
                data[a]['mtu'] = int_bri['mtu']
                data[a]['vrf'] = int_bri['vrf']
            except:
                data[a]['mtu'] = ''
                data[a]['vrf'] = ''
            try:
                for b in self.data['show_lldp_nei']['lldpNeighbors']:
                    if a == b['port']:
                        data[a]['neighbor'] = b['neighborDevice']
                        data[a]['neighborPort'] = b['neighborPort']
            except:
                data[a]['neighbor'] = ''
                data[a]['neighborPort'] = ''
            int = eosObj(data[a], eosIntKeylist)
            #pprint(int.interface)

            # Sort Interfaces Ethernet, Loopback, Vlan, nve, etc.
            if 'Ethernet' in int.interface:
                self.eth.append(int)
            elif 'Port-Channel' in int.interface:
                self.portchannel.append(int)
            elif 'Vlan' in int.interface:
                self.vlanInt.append(int)
            elif 'Loopback' in int.interface:
                self.lo.append(int)
            elif 'nve' in int.interface:
                self.nve.append(int)
            elif 'Management' in int.interface:
                self.mgmt.append(int)
            else:
                self.miscInt.append(int)
                print(f'Found undefined Interface {int.interface}')

    def getVRF(self):
        vrflist = []
        setattr(self, 'vrf', [])
        for a in self.data['show_vrf']['TABLE_vrf']['ROW_vrf']:
            vrfobj = eosSubObj(a, eosVRFKeylist)
            self.vrf.append(vrfobj)

    def getRoute(self):
        for a in self.vrf:
            routelist= []
            for b in self.data['show_ip_route']['TABLE_vrf']['ROW_vrf']:
                if a.vrf_name == b['vrf-name-out']:
                    try:
                        for c in b['TABLE_addrf']['ROW_addrf']['TABLE_prefix']['ROW_prefix']:
                            routeobj = eosSubObj(c, eosRouteKeylist)
                            p = c['TABLE_path']['ROW_path']
                            paths = item2list(p)
                            for rt in paths:
                                routesubobj = eosSubObj(rt, eosRouteKeylist)
                                for d in eosRouteKeylist:
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
                bgpvrf = eosSubObj(b, eosBGPVRFKeylist)
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

class cvContainer:
    def __init__(self, json_data):
        self.keylist = cvContainerKeylist
        # process uptime
        self.data = json_data
        self.name = json_data['Name']
        try:
            self.parentName = str(json_data['parentName'])
        except:
            self.parentName = '0'
        # initAttr(self)

class cvConfiglet:
    def __init__(self, json_data):
        self.keylist = cvConfigletKeylist
        # process uptime
        self.data = json_data
        self.name = json_data['name']
        self.config = json_data['config']
        initAttr(self)

def eosIntObj(obj1, data, keylist, extendedkey = 'none'):
    if type(data) is list:
        z = data
    else:
        z = data[extendedkey]

    for a in data:
        if extendedkey != 'none':
            z = a[extendedkey]
        else:
            z = a
    eosObj = eosSubObj(z, keylist)
    tmp_list = vars(eosObj)
    listkeys = tmp_list.keys()
    if 'Eth' in eosObj.interface:
        for b in obj1.eth:
            if b.interface == eosObj.interface:
                copyAttr(b, eosObj, listkeys)
    elif 'port-channel' in eosObj.interface:
        for b in obj1.portchannel:
            if b.interface == eosObj.interface:
                copyAttr(b, eosObj, listkeys)
    elif 'Vlan' in eosObj.interface:
        for b in obj1.vlanInt:
            if b.interface == eosObj.interface:
                copyAttr(b, eosObj, listkeys)
    elif 'loopback' in eosObj.interface:
        for b in obj1.lo:
            if b.interface == eosObj.interface:
                copyAttr(b, eosObj, listkeys)
    elif 'nve' in eosObj.interface:
        for b in obj1.nve:
            if b.interface == eosObj.interface:
                copyAttr(b, eosObj, listkeys)
    elif 'mgmt' in eosObj.interface:
        for b in obj1.mgmt:
            if b.interface == eosObj.interface:
                copyAttr(b, eosObj, listkeys)
    else:
        obj1.miscInt.append(eosObj)
        print(f'Found undefined Interface IP {eosObj.interface}')
    '''except:
        print(f'Get Interface failed for {self.name}')'''

class eosSubObj:
    # Cisco Nexus Interface
    def __init__(self, json_data, keylist):
        self.keylist = keylist
        self.data = json_data
        initAttr(self)

class eosSubObjList:
    def __init__(self, json_data, keylist):
        self.keylist = keylist
        self.data = json_data
        initAttr(self)


class eosObj:
    def __init__(self, json_data, keylist):
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


def BuildDevice(json_data): # Build switch device object
    device = cvDevice(json_data)
    #device.getInterfaces()
    #device.getVlans()
    #device.getVRF()
    #device.getRoute()
    #device.getBGP()
    return device

def cvContainerList(json_data):
    list = []
    json = json_data
    for a in json:
        dev = cvContainer(a)
        list.append(dev)
    #list.sort(key=natural_keys)
    list2 = sorted(list, key=lambda i: i.parentName)
    return list2

def cvConfigletList(json_data):
    list = []
    json = json_data
    for a in json:
        dev = cvConfiglet(a)
        list.append(dev)
    #list.sort(key=natural_keys)
    list2 = sorted(list, key=lambda i: i.name)
    return list2

def BuildCVPObj(json_data):
    pass

def getCVPObjet(json, keylist):
    obj = eosObj(json, keylist)
    return obj




