from typing import List

import aci_object
import operator
import json
import requests
import json
import copy
import inspect
import getpass
from pprint import pprint
from operator import itemgetter
import xlsxwriter
from colorama import Fore, Back, Style


class Headline:
    def __init__(self):
        self.keylist = ['id', 'speed', 'adminSt', 'operSt', 'PG', 'descr', 'selDescr', 'layer', 'autoNeg', 'mtu', 'portT', 'guiCiscoPID', 'guiSN', 'guiName',
                        'devId', 'portId', 'platId', 'ver', 'sysName', 'portDesc']
        self.namelist = ['Interface', 'Speed','Admin State', 'Operational State', 'Port Group', 'Interface Desc', 'Int Selector Desc', 'Layer', 'Auto Neg', 'MTU',
                         'Port Type', 'Transceiver', 'Transceiver SN', 'Vender', 'CDP Neighbor', 'CDP Port', 'Platform',
                         'Software Version', 'LLDP Neighbor', 'LLDP Port']



class Interface:
    def __init__(self, name='1/1'):
        self.name = name
        self.portGroup = ''

    def add_new_attribute(self, aci_obj, key):
        setattr(self, key, aci_obj[key])

    def add_all_attribute(self, aci_obj, namelist):
        for n in namelist:
            m = aci_obj.get(n, '')
            add_new_attribute(aci_obj, m)

    def add_child_attribute(self, aci_obj_child, child, attrlist):
        x = len(aci_obj_child)
        grandchild = {}
        for i in attrlist:
            setattr(self, i, '')
        for i in range(0, x, 1):
            if child in aci_obj_child[i]:
                grandchild = aci_obj_child[i][child]
                for y in attrlist:
                    try:
                        setattr(self, y, aci_obj_child[i][child]['attributes'][y])
                    except:
                        setattr(self, y, '')
        return grandchild


    def addphysattributes(self, aci_obj, attrlist):
        for x in attrlist:
            try:
                setattr(self, x, aci_obj[x])
            except:
                setattr(self, x, '')
            finally:
                self.name = aci_obj['id']
                tmp = self.id.split('/')
                self.port = int(tmp[1])
                tmp2 = tmp[0].split('h')
                self.module = int(tmp2[1])

    #def addintselectors(self, aci_obj):


class Switch:
    def __init__(self, name='Switch'):
        self.name = name
        self.interfaces = []
        self.nodeId = ''
        self.podId = '1'
        self.Switches = {}
        self.keylist = []
        self.namelist = []
        self.intProfile = ''

    def add_child_attribute(self, aci_obj_child, child, attrlist):
        x = len(aci_obj_child)
        grandchild = {}
        for i in attrlist:
            setattr(self, i, '')
        for i in range(0, x, 1):
            if child in aci_obj_child[i]:
                grandchild = aci_obj_child[i][child]
                for y in attrlist:
                    try:
                        setattr(self, y, aci_obj_child[i][child]['attributes'][y])
                    except:
                        setattr(self, y, '')
        return grandchild

    def set_headline(self, keylist, namelist):
        self.keylist = keylist
        self.namelist = namelist

    def getlist(self): # todo : Remove
        dict = self.__dict__
        list = dict.keys()
        list.sort(key=lambda dict: (dict['module'], dict['port']))
        return list

    def addswitchattributes(self, aci_obj):
        list = ['name', 'nodeId', 'podId', 'nodeRole', 'model', 'id', 'runningVer']
        for i in list:
            if i in aci_obj:
                setattr(self, i, aci_obj[i])
        self.Headline = Headline

    def add_leaf_sel(self, selectorlist):
        for i in leafsellist:
            for j in i.blk:
                if j == self.nodeId:
                    setattr(self, 'infraLeafS', i.LeafS)



    def add_interfaces(self, aciinterfaces, acicdp, acilldp, infraport_dict):
        node = self.nodeId
        pod = self.podId
        int_phys_dict = aciinterfaces
        cdp_dict = acicdp
        lldp_dict = acilldp
        portsobj = aci_object.aciObj(name='infraAccPortP', dict=infraport_dict)
        intobj = aci_object.aciObj(name='l1PhysIf', dict=int_phys_dict, children=False, childrenkey=['ethpmPhysIf'], children2=True, childrenkey2=['ethpmFcot'])
        cdpobj = aci_object.aciObj(name='cdpIf', dict=cdp_dict, children=True)
        lldpobj = aci_object.aciObj(name='lldpIf', dict=lldp_dict, children=True)
        profile_list = []

        interfaces = []
        for y in intobj.data: ### Create Interface Objects
            int_name = y[intobj.name]['attributes']['id']
            int1 = Interface(name=int_name)  # Object with name ethX_Y
            int1.addphysattributes(y[intobj.name]['attributes'], self.keylist) # Add Attributes
            s = int_name.split('/')
            t = s[0].split('h')
            setattr(int1, 'port', int(s[1]))  # Set port for sorting and future use.
            setattr(int1, 'module', int(t[1]))  # Set module for sorting and future use.
            tmp = {'name': int1.name, 'port': int1.port, 'module': int1.module}
            ethpmPhysIf = int1.add_child_attribute(y[intobj.name]['children'], 'ethpmPhysIf', ['operSt', 'operSpeed'])
            try:
                ethpmFcot = int1.add_child_attribute(ethpmPhysIf['children'], 'ethpmFcot', ['guiCiscoPID', 'guiSN', 'guiName'])
                if int1.guiCiscoPID == '':
                    ethpmFcot = int1.add_child_attribute(ethpmPhysIf['children'], 'ethpmFcot',
                                                         ['typeName', 'guiSN', 'guiName'])
                    int1.guiCiscoPID = int1.typeName
                else:
                    pass
            except:
                pass
            interfaces.append(tmp)
            setattr(self, int_name, int1) # Add Attribute (interface Object) to Switch Object
        interfaces.sort(key=itemgetter('module', 'port')) # Create list of sorted interfaces
        intlist = []
        for i in interfaces: # append new list of names to <switch object>.interfaces
            intlist.append(i['name'])
        setattr(self, 'interfaces', intlist)
        for x in cdpobj.data:
            try:
                cdp_id = x[cdpobj.name]['attributes']['id']
                cdp_int = getattr(self, cdp_id)
                cdpAdjEp = cdp_int.add_child_attribute(x[cdpobj.name]['children'], 'cdpAdjEp', ['platId', 'devId', 'portId', 'ver'])
            except:
                pass
        for x in lldpobj.data:
            try:
                lldp_id = x[lldpobj.name]['attributes']['id']
                lldp_int = getattr(self, lldp_id)
                lldpAdjEp = lldp_int.add_child_attribute(x[lldpobj.name]['children'], 'lldpAdjEp', ['sysName', 'portDesc'])
            except:
                pass
        ### eth = merge_children('ethpmPhysIf')

    def add_intselectors(self, leaf_profiles):                          # Single Switch Level
        for p in leaf_profiles:                                         # Switch / Leaf Profile Level
            #pprint('Leafprof: ' + leaf_profiles[p].switchprofile + ' : ' + self.intProfile)
            if self.intProfile in leaf_profiles[p].switchprofile:
                for s in self.interfaces:                               # Sw interface Level
                    for t in leaf_profiles[p].sellist:                  # Leaf Int Selector Level
                        sel_int = getattr(leaf_profiles[p], t)
                        sw_int = getattr(self, s)
                        try:
                            if sel_int.eth == sw_int.name:
                                setattr(sw_int, 'PG', sel_int.PG)
                                setattr(sw_int, 'selDescr', sel_int.selDescr)
                            else:
                                pass
                        except:
                            pass

def merge_children(topkey, children, acichild): # todo : Remove if not needed
    out = {}
    for y in acichild: ### Create Interface Objects
        a = y[topkey]
        for z in a:
            for c in children:
                if c in z:
                    out.update({'child': z[c]})
    return out

def getleafsel(InfraNodes):
    leafsellist = []
    for x in InfraNodes.data:
        name = x[InfraNodes.name]['attributes']['name']
        try:
            infraRsAccPortP = aci_object.AciChild(x[InfraNodes.name], 'infraRsAccPortP', parentkey=name)
        except:
            pass
        try:
            infraLeafS = aci_object.AciChild(x[InfraNodes.name], 'infraLeafS', parentkey=name)
            setattr(infraLeafS, 'LeafS', infraLeafS.data[0]['infraLeafS']['attributes']['name'])
        except:
            continue
        nodeblklist = []
        for y in infraLeafS.data:
            infraNodeBlk = aci_object.AciChild(y[infraLeafS.name], 'infraNodeBlk', parentkey=infraLeafS.LeafS)
            for z in infraNodeBlk.data:
                start = int(z[infraNodeBlk.name]['attributes']['from_'])
                end = int(z[infraNodeBlk.name]['attributes']['to_'])
                if start == end:
                    nodeblklist.append(str(start))
                elif end > start:
                    for i in range(start, end + 1, 1):
                        nodeblklist.append(str(i))
                else:
                    pass
        setattr(infraLeafS, 'blk', nodeblklist)
        leafsellist.append(infraLeafS)
        for x in infraRsAccPortP.data:
            try:
                tmp = x[infraRsAccPortP.name]['attributes']['tDn'].split('accportprof-')
                tmp2 = tmp[1]
                int_profile = tmp2
            except:
                int_profile = ''
            for y in leafsellist:
                if y.parent == infraRsAccPortP.parent:
                    try:
                        setattr(y, 'intProfile', int_profile)
                    except:
                        pass
    return leafsellist


class LeafIntProfile:
    def __init__(self, name='TEST'):
        self.name = name
        self.sellist = []
    def addinterfacesel(self, parent):
        intsellist = []
        test = False
        try:
            infraHPortS = aci_object.AciChild(parent, 'infraHPortS', parentkey=parent['attributes']['name'])
            test = True
        except:
            pass

        if test:
            intsellist = []
            for x in infraHPortS.data:
                int1 = x[infraHPortS.name]['attributes']['name']
                intsel = IntSelector(int1)
                infraRsAccBaseGrp = aci_object.AciChild(x[infraHPortS.name], 'infraRsAccBaseGrp', parentkey=int1)
                setattr(intsel, 'selDescr', x[infraHPortS.name]['attributes']['descr'])
                for y in infraRsAccBaseGrp.data:
                    int2 = y[infraRsAccBaseGrp.name]['attributes']['tDn']
                    if 'accportgrp-' in int2:
                        tmp = int2.split('accportgrp-')
                    elif 'accbundle-' in int2:
                        tmp = int2.split('accbundle-')
                    PG = tmp[1]
                    setattr(intsel, 'PG', PG)
                infraPortBlk= aci_object.AciChild(x[infraHPortS.name], 'infraPortBlk', parentkey=int1)
                for z in infraPortBlk.data:
                    fromCard = z[infraPortBlk.name]['attributes']['fromCard']
                    toCard = z[infraPortBlk.name]['attributes']['toCard']
                    fromPort = z[infraPortBlk.name]['attributes']['fromPort']
                    toPort = z[infraPortBlk.name]['attributes']['toPort']
                    if fromCard == toCard:
                        if fromPort == toPort:
                            eth = 'eth' + fromCard + '/' + fromPort
                            setattr(intsel, 'eth', eth)
                setattr(self, intsel.name, intsel)
                intsellist.append(intsel.name)
        self.sellist = intsellist


class IntSelector:
    def __init__(self, name=''):
        self.name = name
        self.int = ''



def add_profiles(aciinfra):
    leaflist = {}
    aciinfra.get_aci_infra_json()
    portsobj = aci_object.aciObj(name='infraAccPortP', dict=aciinfra.infraport)
    prof_list = []
    for x in portsobj.data:
        profile_name = x[portsobj.name]['attributes']['name']
        leaflist[profile_name] = LeafIntProfile(name=profile_name)
        #leaf_obj = aci_object.AciChild(portsobj)
        try:
            node = aci_object.AciChild(x[portsobj.name], 'infraRtAccPortP', parentkey=profile_name)
        except:
            pass
        switchprofile = []
        for y in node.data:
            # pprint(y[node.name]['attributes']['tDn'])
            tmp = y[node.name]['attributes']['tDn'].split('nprof-')
            switchprofile.append(tmp[1])
            setattr(leaflist[profile_name], 'switchprofile', switchprofile)
            leaflist[profile_name].addinterfacesel(x[portsobj.name])
    return leaflist



def add_switches(aci_obj):
    SwitchList = {}
    FabricNode_dict = aci_obj.fabricnode
    InfraNode_dict = aci_obj.infranode
    FabricNodes = aci_object.aciObj(name='dhcpClient', dict=FabricNode_dict)
    InfraNodes = aci_object.aciObj(name='infraNodeP', dict=InfraNode_dict)
    leafsellist = getleafsel(InfraNodes)

    for x in FabricNodes.data:  ### Process ACI JSON Data
        name = x[FabricNodes.name]['attributes']['name']
        SwitchList[name] = Switch(name=name)
        SwitchList[name].addswitchattributes(x[FabricNodes.name]['attributes'])
        ###pprint(leafsellist)
        for y in leafsellist:
            for z in y.blk:
                ### pprint(SwitchList[name].nodeId + ' - ' + z)
                if SwitchList[name].nodeId == z:
                    #SwitchList[name].name
                    setattr(SwitchList[name], 'intProfile', y.intProfile)
    return SwitchList

class AciJsonCollect:
    def __init__(self, name='JSON', uname_pwd={}, apic='192.168.10.1'):
        self.name = name
        self.creds = uname_pwd
        self.apic = apic
    def get_aci_fabric_json(self):
        fabric_node_url = '/api/node/class/dhcpClient.json'
        pprint('\n Logging into APIC\n')
        with requests.Session() as s:
            p = s.post('https://' + self.apic + '/api/aaaLogin.json', json=self.creds, verify=False)
            print(Fore.GREEN + '\nCollecting Fabric Node Data')
            fabric_node_raw = s.get('https://' + self.apic + fabric_node_url)
        setattr(self, 'fabricnode', fabric_node_raw.json())

    def get_aci_interfaces_json(self, switch_obj):
        self.pod = switch_obj.podId
        self.node = switch_obj.nodeId
        with requests.Session() as s:
            p = s.post('https://' + self.apic + '/api/aaaLogin.json', json=self.creds, verify=False)
            print('\nCollecting Interface Data for Node: ' + self.node + ' in Pod ' + self.pod)
            int_phys_raw = s.get('https://' + self.apic + '/api/node/class/topology/pod-' + self.pod + '/node-' +
                                 self.node + '/l1PhysIf.json?rsp-subtree=full')
        return int_phys_raw.json()

    def get_aci_cdp_json(self, switch_obj):
        self.pod = switch_obj.podId
        self.node = switch_obj.nodeId
        with requests.Session() as s:
            cdp_url = '/cdpIf.json?rsp-subtree=children&rsp-subtree=full'
            p = s.post('https://' + self.apic + '/api/aaaLogin.json', json=self.creds, verify=False)
            print('\nCollecting CDP Data for Node: ' + self.node + ' in Pod ' + self.pod)
            int_cdp_raw = s.get('https://' + self.apic + '/api/node/class/topology/pod-' + self.pod + '/node-' +
                                self.node + cdp_url)
        return int_cdp_raw.json()

    def get_aci_lldp_json(self, switch_obj):
        self.pod = switch_obj.podId
        self.node = switch_obj.nodeId
        with requests.Session() as s:
            lldp_url = '/lldpIf.json?rsp-subtree=children&rsp-subtree=full'
            p = s.post('https://' + self.apic + '/api/aaaLogin.json', json=self.creds, verify=False)
            print('\nCollecting LLDP Data for Node: ' + self.node + ' in Pod ' + self.pod)
            int_lldp_raw = s.get('https://' + self.apic + '/api/node/class/topology/pod-' + self.pod + '/node-' +
                                self.node + lldp_url)
        return int_lldp_raw.json()


    def get_aci_infra_json(self):
        infra_port_url = '/api/node/mo/uni/infra.json?query-target=subtree&target-subtree-class=infraAccPortP&rsp-subtree=children&rsp-subtree=full'
        infra_node_url = '/api/node/mo/uni/infra.json?query-target=subtree&target-subtree-class=infraNodeP&rsp-subtree=children&rsp-subtree=full'
        pprint('\n Logging into APIC\n')
        with requests.Session() as s:
            p = s.post('https://' + self.apic + '/api/aaaLogin.json', json=self.creds, verify=False)
            print(Fore.GREEN + '\nCollecting Infra Data')
            infra_node_raw = s.get('https://' + self.apic + infra_node_url)
            infra_port_raw = s.get('https://' + self.apic + infra_port_url)
        setattr(self, 'infranode', infra_node_raw.json())
        setattr(self, 'infraport', infra_port_raw.json())


