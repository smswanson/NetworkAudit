import write.writexlsx.write2excel as w2x
from pprint import pprint
from arista.eos.audit.device import BuildDevice
from utilities.subnet import subnet
import re

#region Build Portmap (Ethernet and Logical)
badFill = 'FFC7CE'
badFont = '9C0006'
goodFill = 'C6EFCE'
goodFont = '006100'
neutralFill = 'FFEB9C'
neutralFont = '9C5700'
normalFill = 'FFFFFF'
normalFont = '000000'

portTests = [{'data': 'connected', 'fill': goodFill, 'font': goodFont},
             {'data': 'notconnect', 'fill': neutralFill, 'font': neutralFont},
             {'data': 'suspnd', 'fill': badFill, 'font': badFont},
             {'data': 'noOperMem', 'fill': badFill, 'font': badFont},
             {'data': 'down', 'fill': badFill, 'font': badFont},
             {'data': 'errDisable', 'fill': badFill, 'font': badFont},]
portstatus = [{'key': 'state', 'test': portTests}]
#endregion

def atof(text):
    try:
        retval = float(text)
    except ValueError:
        retval = text
    return retval

def natural_keys(someobject):
    '''
    alist.sort(key=natural_keys) sorts in human order
    http://nedbatchelder.com/blog/200712/human_sorting.html
    float regex comes from https://stackoverflow.com/a/12643073/190597
    '''
    return [ atof(c) for c in re.split('(\d+)', someobject.vlanid) ]



def process_json(json):
    device = BuildDevice(json)
    return device


def portmap(filename, device_list):   # Write the portmap XLSX for all switches...
    wb = hwlist(filename, device_list)
    setvlanroot(device_list)
    vlan(wb, device_list)
    for a in device_list:
        ports(wb, a)
        #routing_table(wb, a)
        # vlan(wb, a)
    wb.save(filename) # Save the workbook


def hwlist(filename, device_list):
    wb = w2x.build_workbook(filename, TAB='HW List')
    eosTable = w2x.buildtable(device_list, 'EOS Switches')
    eosTable.setworksheet(wb.active)
    eosTable.writetable()
    return wb


def ports(WB, device):
    list = ['mgmt', 'eth', 'portchannel', 'lo', 'vlanInt', 'nve']
    headline_list = ['Management', 'Ethernet', 'Port-Channel', 'Loopback', 'VLAN Interface', 'NVE',]
    i = 0
    row = 1
    newtab = w2x.addTab(WB, device.name)
    while i != 5:
        if hasattr(device, list[i]):
            attr = getattr(device, list[i])
            if attr == []:
                pass
            else:
                table = w2x.buildtable(attr, headline_list[i] + ' Port-Map: ' + device.name)
                table.hl = True
                table.hltest = portstatus
                table.row = row
                table.setworksheet(newtab)
                table.writetable()
                row = table.row + 1
        i = i + 1
    if hasattr(device, 'vlan'):
        if device.vlan == []:
            pprint('device.vlan is empty')
        else:
            pprint('Build VLAN Table')
            table = w2x.buildtable(device.vlan, 'VLANs')
            table.hl = True
            table.setworksheet(newtab)
            table.row = row
            table.writetable()
            row = table.row + 1

    w2x.setautofitcol(table.ws)


def routing_table(WB, device):
    tabname = device.name + ' Routes'
    newtab = w2x.addTab(WB, tabname)
    row = 1
    col = 1
    if hasattr(device, 'bgp'):
        table = w2x.buildtable(device.bgp, 'BGP Neighbors')
        table.row = row
        table.setworksheet(newtab)
        table.writetable()
        col = len(table.keys) + 2
        print(f'Column: {col}')

    if hasattr(device, 'vrf'):
        for a in device.vrf:
            if hasattr(a, 'routes'):
                table = w2x.buildtable(a.routes, 'Routing Table for VRF: ' + a.vrf_name)
                table.row = row
                table.col = col
                table.endcol = table.col + table.endcol
                table.setworksheet(newtab)
                table.writetable()
                row = table.row + 1
    w2x.setautofitcol(table.ws)

def get_listDeviceAttributes(device_list, attribute):
    list = []
    for a in device_list:
        value = getattr(a, attribute)
        list.append(value)
    return list

def vlan(WB, devices):
    #Merge all device VLANs
    vlan_list = []
    vlan_name_list = []
    for a in devices:
        vlan_name_list = get_listDeviceAttributes(vlan_list, 'name')
        for b in a.vlan:
            #b.ip = subnet(b.ip, b.mask)
            if b.name in vlan_name_list:
                for c in vlan_list:
                    if b.name == c.name:
                        c.ip.append(b.ip)
                        if b.subnet == c.subnet:
                            pass
                        elif c.subnet == '' and b.subnet != '':
                            print(f'c: {c.subnet}/{b.subnet}')
                            c.subnet = b.subnet
                        else:
                            pass
            else:
                b.ip = [b.ip]
                vlan_list.append(b)
    for b in vlan_list:
        tmp = set(b.ip)
        b.ip = ','.join(list(tmp))



    vlan_list.sort(key=natural_keys)

    tabname = 'VLANs'
    newtab = w2x.addTab(WB, tabname)
    row = 1
    table = w2x.buildtable(vlan_list, 'VLANs')
    table.setworksheet(newtab)
    table.hl = True
    table.row = row
    table.writetable()
    w2x.setautofitcol(table.ws)


def setvlanroot(device_list):
    vlanlist = []
    for a in device_list:
        for b in a.vlan:
            if hasattr(b, 'bridge_mac') and hasattr(b, 'tree_designated_root'):
                if b.tree_designated_root == b.bridge_mac:
                    b.root = a.name
                    for c in device_list:
                        for d in c.vlan:
                            if hasattr(d, 'bridge_mac') and hasattr(d, 'tree_designated_root'):
                                if d.vlanid == b.vlanid:
                                    if d.tree_designated_root == b.tree_designated_root:
                                        d.root = a.name
                                    else:
                                        d.root = d.tree_designated_root
                                else:
                                    pass