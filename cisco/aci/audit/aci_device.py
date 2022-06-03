import operator
from operator import itemgetter
from pprint import pprint
#region Device Attributes


exampleKeylist = [{'name': {'data': 'host_name', 'hl': 'Hostname'}},
                  {'my_key': {'data': 'my_key', 'hl': 'My Headline'}},
                  {'child_key': {'data': 'my_key', 'hl': 'My Headline', 'child': 'child_attr_key'}}
                  ]

aciFabricKeylist = [{'name': {'data': 'host_name', 'hl': 'Hostname'}},
                    {'serial': {'data': 'proc_board_id', 'hl': 'S/N'}},
                    {'uptime': {'data': 'uptime', 'hl': 'Uptime'}}]

acihwattr = [{'name': {'data': 'name', 'hl': 'Node Name'}},
             {'id': {'data': 'id', 'hl': 'Node ID'}},
             {'role': {'data': 'role', 'hl': 'Role'}},
             {'model': {'data': 'model', 'hl': 'Model'}},
             {'serial': {'data': 'serial', 'hl': 'Serial Number'}},
             {'version': {'data': 'version', 'hl': 'Software Version'}},
             {'adSt': {'data': 'adSt', 'hl': 'Admin State'}},
             {'mgmtip': {'data': 'mgmtip', 'hl': 'OOB Mgmt IP'}},
             {'gw': {'data': 'gw', 'hl': 'OOB Gateway'}},
             {'vrf': {'data': 'vrf', 'hl': 'OOB VRF'}},
             {'epg': {'data': 'epg', 'hl': 'OOB EPG'}},
             {'inbmgmtip': {'data': 'inbmgmtip', 'hl': 'INB Mgmt IP'}},
             {'inbgw': {'data': 'inbgw', 'hl': 'INB Gateway'}},
             {'inbbd': {'data': 'inbbd', 'hl': 'INB BD'}},
             {'inbepg': {'data': 'inbepg', 'hl': 'INB EPG'}}, ]

acifaultsattr = [{'severity': {'data': 'severity', 'hl': 'Severity'}},
                 {'domain': {'data': 'domain', 'hl': 'Domain'}},
                 {'type': {'data': 'type', 'hl': 'Type'}},
                 {'code': {'data': 'code', 'hl': 'Code'}},
                 {'count': {'data': 'count', 'hl': 'Count'}},
                 {'cause': {'data': 'cause', 'hl': 'Cause'}},
                 {'rule': {'data': 'rule', 'hl': 'Rule'}},
                 {'subject': {'data': 'subject', 'hl': 'Subject'}},
                 {'descr': {'data': 'descr', 'hl': 'Description'}}, ]

aciTenantattr = [{'name': {'data': 'name', 'hl': 'Tenant'}},
                 {'descr': {'data': 'descr', 'hl': 'Description'}},
                 {'nameAlias': {'data': 'nameAlias', 'hl': 'Alias'}},
                 {'extMngdBy': {'data': 'extMngdBy', 'hl': 'External Mangement'}}, ]

aciBDattr = [{'fvTenant': {'data': 'fvTenant', 'hl': 'Tenant'}},
             {'name': {'data': 'name', 'hl': 'Bridge Domain'}},
             {'nameAlias': {'data': 'nameAlias', 'hl': 'Alias'}},
             {'tnFvCtxName': {'data': 'tnFvCtxName', 'hl': 'VRF'}},
             {'ip': {'data': 'ip', 'hl': 'IP'}},
             {'mtu': {'data': 'mtu', 'hl': 'MTU'}},
             {'descr': {'data': 'descr', 'hl': 'Description'}},
             {'mac': {'data': 'mac', 'hl': 'MAC'}},
             {'unicastRoute': {'data': 'unicastRoute', 'hl': 'Unicast Routing'}},
             {'mcastAllow': {'data': 'mcastAllow', 'hl': 'Multicast'}},
             {'tnL3extOutName': {'data': 'tnL3extOutName', 'hl': 'L3 Out(s)'}},
             {'unkMacUcastAct': {'data': 'unkMacUcastAct', 'hl': 'unkMacUcastAct'}},
             {'arpFlood': {'data': 'arpFlood', 'hl': 'ARP Flood'}},
             {'ipLearning': {'data': 'ipLearning', 'hl': 'IP Learning'}},
             {'intersiteL2Stretch': {'data': 'intersiteL2Stretch', 'hl': 'Multisite Stretch'}}, ]

aciEPGattr = [{'fvTenant': {'data': 'fvTenant', 'hl': 'Tenant'}},
              {'fvAp': {'data': 'fvAp', 'hl': 'App Profile'}},
              {'name': {'data': 'name', 'hl': 'EPG'}},
              {'nameAlias': {'data': 'nameAlias', 'hl': 'Alias'}},
              {'tnFvBDName': {'data': 'tnFvBDName', 'hl': 'BD'}},
              {'DOM': {'data': 'DOM', 'hl': 'Domains'}},
              {'descr': {'data': 'descr', 'hl': 'Description'}},
              {'nameAlias': {'data': 'nameAlias', 'hl': 'Alias'}}, ]

aciCONattr = [{'fvTenant': {'data': 'fvTenant', 'hl': 'Tenant'}},
              {'vzBrCP': {'data': 'vzBrCP', 'hl': 'Contract'}},
              {'descr': {'data': 'descr', 'hl': 'Description'}},
              {'name': {'data': 'name', 'hl': 'Subject'}},
              {'filter_list': {'data': 'filter_list', 'hl': 'Filters'}}, ]

aciSBJattr = [{'fvTenant': {'data': 'fvTenant', 'hl': 'Tenant'}},
              {'revFltPorts': {'data': 'revFltPorts', 'hl': 'Reverse Flt Ports'}},
              {'descr': {'data': 'descr', 'hl': 'Description'}},
              {'name': {'data': 'name', 'hl': 'Subject'}},
              {'filter_list': {'data': 'filter_list', 'hl': 'Filters'}}, ]

CON_hl_namelist = ['Tenant', 'Contract', 'Subject', 'Filters']
CON_hl_keylist = ['fvTenant', 'vzBrCP', 'name', 'filter_list']

aciL3OUTattr = [{'l3extOut': {'data': 'l3extOut', 'hl': 'L3 Out'}},
                {'descr': {'data': 'descr', 'hl': 'Description'}},
                {'l3extRsEctx': {'data': 'l3extRsEctx', 'hl': 'VRF', 'child': True }}, ]



#endregion

def initAttr(obj):
    # Initialize variables based on key list
    for a in obj.keylist:
        a_key = a.keys()
        tmp = []
        for b in a_key:
            b_key = b
        '''if a[b_key].has_key('child'):
            if a[b_key]['child']:
                for c in obj.children:
                    print("Processing Children")
                    try:
                        d = c['b_key']['attributes'][a[b_key]['data']]
                        tmp.append(d)
                    except:
                        pass
                setattr(obj, b_key, tmp)'''
        # else:
        try:
            d = a[b_key]['data']
            setattr(obj, b_key, obj.attributes[d])
        except:
            setattr(obj, b_key, '')



class aciSubObj:
    # Cisco Nexus Interface
    def __init__(self, json_data, keylist):
        self.keylist = keylist
        self.data = json_data
        initAttr(self)


def aciobjlist(dict={}, topkey='imdata', type='', keylist={}):
    if topkey == '': ### if no topkey, assume dict is list of dictionaries
        data = dict
    else: ### else use topkey to get list under it
        data = dict[topkey]
    list = []
    for x in data:
        try:
            key = type
            newObj = aciobj(type=key, dict=x, keylist=keylist)
            list.append(newObj)
        except:
            pass
    return list


def filteraciobjlist(list, key):
    new_list = []
    for x in list:
        if x.type == key:
            new_list.append(x)
    return new_list

class acifabric:
    def __init__(self, dict={}):
        if dict == {}:
            pprint("New acifabric has no dictionary")
        else:
            self.type = 'ACI Fabric'


class aciobj:
    def __init__(self, type='fvTenant', dict={}, keylist={}):
        if dict == {}:
            pprint("New aciobj has no dictionary")
        else:
            self.keylist = keylist
            self.keylistkeys = []
            self.data = dict[type]
            self.type = type
            self.family = []
            self.attributes = dict[type]['attributes']
            initAttr(self)   ### Pull Attributes for object using keylist
            if 'children' in self.data.keys():
                self.children = dict[type]['children']
                # self.kids = aciobjlist(dict=self.data, topkey='children')
                # self.numkids = len(self.kids)
            else:
                self.children = []
                self.kids = []
                self.numkids = 0
            try: # list the keys for each dict in keylist (1 per row)
                for a in keylist:
                    b = a.keys()
                    for c in b:
                        d = c
                    self.keylistkeys.append(d)
            except:
                print(f'keylistkeys failed for {self.type}')

    def buildattr(self, attr, json, topkey, type, keylist):
        try:
            newobj = aciobjlist(json, topkey, type, keylist)
            setattr(self, attr, newobj)
        except:
            print(f'Failed to process {attr}')

    def setaciattr(self, name, key): ### Creates new attribute from 'attributes'
        try:
            setattr(self, name, self.attributes[key])
        except:
            print(f'Not able to set attribute for {name} and {key}')


    def setaciattrlist(self, key_list):
        if key_list:
            for z in key_list:
                if z in self.attributes:
                    setattr(self, z, self.attributes[z])

    def getchildattr(self, childkey=''): ### Gets attributes from children and adds to parent
        if hasattr(self, 'children'):
            for a in self.children:
                if a[childkey]:
                    for b in self.keylist:
                        for c in b.keys():
                            d = c
                        try:
                            if childkey == d:
                                setattr(self, self.keylist[b], a[childkey]['attributes'][d])
                        except:
                            print(f'Failed to get Child Attribute {childkey}')


    def filterkids(self, name, key, attr_list=[], kid_attr_list=[]):
        # Creates new attribute for specific children in list format
        list = []
        family = []
        if self.numkids != 0:
            for x in self.kids:
                if x.type == key:
                    x.family = [self.type] + self.family
                    setattr(x, 'parent', self.type)
                    for a in x.family:
                        if hasattr(self, a):
                            setattr(x, a, getattr(self, a))  # Set family
                    if attr_list:
                        x.setaciattrlist(attr_list)
                        if kid_attr_list:
                            for y in kid_attr_list:
                                if hasattr(x, y):
                                    setattr(self, y, getattr(x, y))
                    list.append(x)
            setattr(self, name, list)
    def setparentattr(self, parent, attrname, attr):
        if hasattr(parent, attr):
            setattr(self, attrname, getattr(parent, attr))

    def setsinglechildattr(self, attrchild, newattrname, attr): # Note returns last child attr in list
        if hasattr(self, attrchild):
            tmp = getattr(self, attrchild)
            for a in tmp:
                if hasattr(a, attr):
                    tmp1 = getattr(a, attr)
                    setattr(self, newattrname, getattr(a, attr))



    '''def setFamilyTree(self, child, family_tree = []):
        ### family_tree is a list of objects for grandparents and great-grandparents
        if hasattr(parent, self.type):
            for z in getattr(parent, self.type):
                setattr(z, parent.type, parent.name)
                if family_tree:
                    for a in family_tree:
                        setattr(z, a.type, a.name)
                if kid_list:
                    for a in kid_list:
                        setattr(z, a.type, a.name)'''

    def sortaci(self, key):
        self.sort(key=itemgetter(key), reverse=True)

    '''family = [kid1: {'name': 'name', 'attr': [], kidlist: []]

    def filterfamily(self, root, family):
        for a in self:
            for b in family:
                a.filterkids(family[b]['name'], 'bgpRRNodePEp', family[b]['attr'])'''

class aciBuildDevice:
    def __init__(self, json):
        self.buildattr('faults', json['faults_dict'], 'imdata', 'faultSummary', acifaultsattr)
        self.buildattrlist('hwlist', json['podDictList'], 'imdata', 'fabricNode', acihwattr)
        self.buildattr('tenants', json['tenant_dict'], 'imdata', 'fvTenant', acihwattr)
        # Tenant build
        for a in self.tenants:
            a.buildattr('bd', a.children, '', 'fvBD', aciBDattr)
            a.buildattr('epg', a.children, '', 'fvEp', aciEPGattr)
            a.buildattr('contract', a.children, '', 'vzBrCP', aciCONattr)
            a.buildattr('l3out', a.children, '', 'l3extOut', aciL3OUTattr)
            #for b in a.contract:
            #    b.buildattr('subject', b.children, '','vzSubj', aciSBJattr)

    def buildattr(self, attr, json, topkey, type, keylist): # list of objects
        try:
            newobj = aciobjlist(json, topkey, type, keylist)
            try:
                setattr(newobj, a.type, a.name)
            except:
                pass
            setattr(self, attr, newobj)
        except:
            print(f'Failed to process {attr}')

    def buildattrlist(self, attr, list, topkey, type, keylist): # List of lists of objects
        #try:
        attrlist = []
        for a in list:
            newobj = aciobjlist(a, topkey, type, keylist)
            if newobj == []:
                continue
            else:
                attrlist.append(newobj)
        setattr(self, attr, attrlist)
        #except:
            #print(f'Failed to process {attr}')

    def buildchildattr(self, attr, json, topkey, ptype, ctype, keylist):
        pass

    def setattrlist(self, attr, key, value):
        try:
            for a in self.attr:
                setattr(a, key, value)
        except:
            print(f'Failed to set {attr} with {key} and {value}')
