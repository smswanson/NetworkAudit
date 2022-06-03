import aci_obj2
import requests
import json
import copy
import inspect
import getpass
import login.login as login
from pprint import pprint
from operator import itemgetter, attrgetter
import write.writexlsx.write_pyxl as write_pyxl
from colorama import Fore, Back, Style
import os.path

offline = False


def splitDn(string, splitlist = [3, 3, 4]):
    # Example string uni/tn-LAB/ap-LAB-01_AP/epg-LAB_TEST-03_EPG
    # Example split list [
    outputlist = []
    tmp = string.split('/')
    l = len(tmp)
    for a in range(1, l):
        try:
            out = tmp[a][splitlist[a-1]:]
        except:
            out = tmp[a]
        outputlist.append(out)
    return outputlist


def processChild(child, parent, family_tree = [], kid_list = []):
    ### family_tree is a list of objects for grandparents and great-grandparents
    if hasattr(parent, child):
        for z in getattr(parent, child):
            z.setaciattr('name', 'name')
            setattr(z, parent.type, parent.name)
            if family_tree:
                for a in family_tree:
                    setattr(z, a.type, a.name)
            if kid_list:
                for a in kid_list:
                    setattr(z, a.type, a.name)


def setkidattr(obj, attr_list=['name']):
    for b in obj:
        for c in attr_list:
            if c in b.attributes:
                    b.setaciattr(c, c)


def getACIdata(session, APIC, data, data_url, log=True, offline=False):
    print('\nGetting ' + data + ' Data')
    directory = './aci-audit-output/'
    logfile = data + '_raw.json'
    if not os.path.isdir(directory):
        os.mkdir(directory)
    if offline:
        try:
            with open(logfile) as json_file:
                data_dict = json.load(json_file)
                pprint('JSON Data Loaded for ' + logfile)
                json_file.close()
        except:
            pprint('Failed to Open: ' + logfile)


    else:
        data_raw = session.get('https://' + APIC + data_url)
        data_dict = data_raw.json()
        if log:
            logfile = data + '_raw.json'
            file_path = os.path.join(directory, logfile)
            with open(file_path, 'w') as file:
                file.write(json.dumps(data_dict, indent=4))  # use `json.loads` to do the reverse
                file.close()
    return data_dict


def __main__():
    version = 'ver1.11'
    script_name = 'Configuration Generator'
    pprint('Running ' + script_name + ' Version: ' + version)
    test = True
    upload = False
    offline = 'no'
    name_pwd = login.get_login('aci', test=test) # Get credentials
    APIC = name_pwd['APIC']
    excel_file = name_pwd['filename'] + '.xlsx'
    podList = [1,2]
    podDictList = []
    worksheetNames = ['HW Overview', 'System', 'Fabric Access', 'Faults']


    '''################### URLs for desire data/JSON #################################'''
    #region APIC URLs
    '''#infra_url = '/api/node/mo/uni/infra.json?query-target=subtree=infraPortBlk'
    ###'/api/node/mo/uni/infra.json?query-target=subtree&target-subtree-class=infraAccPortP&query-target-filter=not(wcard(infraAccPortP.dn,"__ui"))&query-target=subtree&target-subtree-class=infraFexP,infraHPortS,infraPortBlk&subscription=yes'
    #'/api/node/mo/uni/infra.json?query-target=subtree'	'''
    multicast_url = '/api/node/mo/uni/tn-common/ctx-SHARED-VRF/pimctxp.json?rsp-subtree=full'
    auth_url = '/api/node/mo/uni/userext.json?rsp-subtree=full'
    tenant_url = '/api/node/class/fvTenant.json?rsp-subtree=full'
    controller_url = '/api/node/class/topology/pod-1/node-1/firmwareCtrlrRunning.json?query-target=subtree'
    fabric_node_url = '/api/node/class/dhcpClient.json?rsp-subtree=full'
    infra_url = '/api/node/mo/uni/infra.json?rsp-subtree=full'
    ethpmPhysIf_url = '/api/node/class/ethpmPhysIf.json?rsp-subtree=full'
    portgroup_url = '/api/node/class/infraAccPortGrp.json?rsp-subtree=full'
    pcportgroup_url = '/api/node/class/infraAccBndlGrp.json?rsp-subtree=full'
    domain_url = '/api/node/mo/uni.json?query-target=subtree&target-subtree-class=l2extDomP,l3extDomP,physDomP,vmmDomP&target-subtree-class=infraRsVlanNs,infraRtDomP'
    #domain_url = '/api/node/mo/uni/phys-DC1_PHYS_DOM.json?query-target=self&rsp-subtree=full'
    #domain_url = '/api/node/mo/uni/phys.json?query-target=subtree&target-subtree-class=l2extDomP,l3extDomP,physDomP,vmmDomP&target-subtree-class=infraRsVlanNs,infraRtDomP&query-target=subtree'
    ## Policy Groups
    #pg_url = '/api/node/class/infraAccPortGrp.json?rsp-subtree=full'
    #aep_url = '/api/node/mo/uni/infra.json?query-target=subtree&target-subtree-class=infraAttEntityP&target-subtree-class=infraRtAttEntP&query-target=subtree'
    #bd_url = '/api/node/mo/uni/tn-TEST_PROD_TENANT/BD-TEST_PROD_BD_1'
    #epg_url = ''
    #ctr_url = ''
    fabric_url = '/api/node/mo/uni/fabric.json?rsp-subtree=full'
    protpol_url = '/api/node/mo/uni/fabric/protpol.json?query-target=children&rsp-subtree=full'
    aep_url = '/api/node/class/infraAttEntityP.json?rsp-subtree=full'
    '''pod1_url = '/api/node/mo/topology/pod-1.json?query-target=children'
    pod2_url = '/api/node/mo/topology/pod-2.json?query-target=children'
    pod3_url = '/api/node/mo/topology/pod-3.json?query-target=children'
    pod4_url = '/api/node/mo/topology/pod-4.json?query-target=children' '''
    faults_url = '/api/node/class/faultSummary.json?query-target=subtree'
    #endregion
    #region Pull Data from APICs
    with requests.Session() as s:
        if not upload:
            p = s.post('https://' + APIC + '/api/aaaLogin.json', json=name_pwd, verify=False)
        else:
            pass
        # print the html returned or something more intelligent to see if it's a successful login page.
        pprint(p.text)
        return s
        # print('\n\n\n\n\n')
        # An authorised request.
        # = s.get('https://' + APIC + infra_url)

        vrf_dict = getACIdata(s, APIC, 'portgroup', multicast_url, offline=upload)
        #pprint('Multicast Dict')
        #pprint(vrf_dict)
        portgroup_dict = getACIdata(s, APIC, 'portgroup', portgroup_url, offline=upload)
        pcportgroup_dict = getACIdata(s, APIC, 'pcportgroup', pcportgroup_url, offline=upload)
        infra_dict = getACIdata(s, APIC, 'infra', infra_url, offline=upload)
        tenant_dict = getACIdata(s, APIC, 'tenant', tenant_url, offline=upload)
        fabric_dict = getACIdata(s, APIC, 'fabric', fabric_url, offline=upload)
        fabric_dict_raw = getACIdata(s, APIC, 'fabric_node', fabric_node_url, offline=upload)
        domain_dict = getACIdata(s, APIC, 'domain', domain_url, offline=upload)
        protpol_dict = getACIdata(s, APIC, 'protpol', protpol_url, offline=upload)
        aep_dict = getACIdata(s, APIC, 'aep', aep_url, offline=upload)
        ethpmPhysIf_dict = getACIdata(s, APIC, 'ethpmPhysIf', ethpmPhysIf_url, offline=upload)
        for a in podList:
            b = str(a)
            podnum = 'pod-' + b
            try:
                pod_dict = getACIdata(s, APIC, podnum, '/api/node/mo/topology/' +  podnum +'.json?query-target=children', offline=upload)
                podDictList.append(pod_dict)
            except:
                pprint(podnum + ' Not Found')

        controller_dict = getACIdata(s, APIC, 'controller', controller_url, offline=upload)
        auth_dict = getACIdata(s, APIC, 'auth', auth_url, offline=upload)
        faults_dict = getACIdata(s, APIC, 'faults', faults_url, offline=upload)
        dlist = {'imdata': []}

    Full_Tenant = aci_obj2.aciobjlist(tenant_dict, 'imdata')
    Tenant = aci_obj2.filteraciobjlist(Full_Tenant, 'fvTenant')
    Domain = aci_obj2.aciobjlist(domain_dict, 'imdata')
    Infra = aci_obj2.aciobjlist(infra_dict, 'imdata')
    Fabric = aci_obj2.aciobjlist(fabric_dict, 'imdata')
    PortGroup = aci_obj2.aciobjlist(portgroup_dict, 'imdata')
    PCPortGroup = aci_obj2.aciobjlist(pcportgroup_dict, 'imdata')
    Auth = aci_obj2.aciobjlist(auth_dict, 'imdata')
    Faults = aci_obj2.aciobjlist(faults_dict, 'imdata')
    AEP = aci_obj2.aciobjlist(aep_dict, 'imdata')
    podObjList = []
    for a in podDictList:
        podObj = aci_obj2.aciobjlist(a, 'imdata')
        podObjList.append(podObj)
    BD = []
    EPG = []
    AP = []
    VRF = []
    ''' Tenant Processing '''
    BD_attr = ['intersiteL2Stretch', 'ipLearning', 'name', 'nameAlias',
               'unicastRoute', 'mcastAllow', 'mac', 'mtu', 'descr', 'arpFlood', 'unkMacUcastAct']
    EPG_attr = ['name', 'nameAlias', 'descr']
    #endregion
    ''''''''''''''''''''''''                      ''''''''''''''''''''''''
    '''                      System Overview: POD '''
    ''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
    #region Switch Overview
    Pod = []
    for a in podObjList:
        for b in a:
            if b.type == 'fabricNode':
                attr = ['adSt', 'apicType', 'id', 'serial', 'version', 'nameAlias', 'role', 'model', 'dn']
                b.setaciattrlist(attr)
                Pod = Pod + [b]
    Pod = sorted(Pod, key=attrgetter('id'))
    #endregion
    ''''''''''''''''''''''''''''''''''''''''''''''''''
    '''                Faults                     '''
    ''''''''''''''''''''''''''''''''''''''''''''''''''
    #region Process Faults
    fault_list = ['severity', 'domain', 'type', 'code', 'count', 'cause', 'rule', 'subject', 'descr']
    for a in Faults:
        a.setaciattrlist(fault_list)

    #endregion
    ''''''''''''''''''''''''''''''''''''''''''''''''''
    '''                Admin                       '''
    ''''''''''''''''''''''''''''''''''''''''''''''''''
    #region Process Admin
    account = ['accountStatus', 'descr', 'expires', 'expiration', 'firstName', 'lastName', 'name', 'nameAlias']
    tacacs = ['name', 'descr', 'authProtocol', 'port', 'epgDn', 'operState', 'monitorServer']
    radius = ['name', 'descr', 'authPort', 'authProtocol', 'monitorServer', 'operState', 'epgDn']
    for a in Auth:
        a.filterkids('aaaUser', 'aaaUser', account)
        a.filterkids('aaaRadiusEp', 'aaaRadiusEp')
        if hasattr(a, 'aaaRadiusEp'): # aaaRadiusProviderGroup aaaProviderRef
            for b in a.aaaRadiusEp:
                radlist = []
                b.filterkids('aaaRadiusProviderGroup', 'aaaRadiusProviderGroup', ['name', 'descr'])
                if hasattr(b, 'aaaRadiusProviderGroup'):
                    for c in b.aaaRadiusProviderGroup: # aaaProviderRef
                        c.filterkids('aaaProviderRef', 'aaaProviderRef', ['name', 'descr', 'order'])
                        if hasattr(c, 'aaaProviderRef'):
                            for d in c.aaaProviderRef:
                                d.setparentattr(c, 'provGrp', 'name')
                                d.setparentattr(c, 'provGrpDescr', 'descr')
                                setattr(d, 'authType', 'Radius')
                b.filterkids('aaaRadiusProvider', 'aaaRadiusProvider', radius)
                if hasattr(b, 'aaaRadiusProvider'):
                    for c in b.aaaRadiusProvider:
                        tmp = c.epgDn
                        # tmp2 = tmp.split('/')
                        tmp3 = tmp.split('/tn-')
                        tmp4 = tmp3[1].split('/mgmtp-')
                        epgTn = tmp4[0]
                        if '/oob-' in tmp4[1]:
                            tmp5 = tmp4[1].split('/oob-')
                            epgAp = tmp5[0]
                            epgName = tmp5[1]
                        elif '/inb' in tmp4[1]:
                            tmp5 = tmp4[1].split('/inb-')
                            epgAp = tmp5[0]
                            epgName = tmp5[1]
                        else:
                            tmp5 = tmp4[1].split('/')
                            epgAp = tmp5[0]
                            epgName = tmp5[1]
                        setattr(c, 'epgAp', epgAp)
                        setattr(c, 'epgTn', epgTn)
                        setattr(c, 'epgName', epgName)
                        setattr(c, 'authType', 'RADIUS')
        a.filterkids('aaaTacacsPlusEp', 'aaaTacacsPlusEp')
        if hasattr(a, 'aaaTacacsPlusEp'):
            for b in a.aaaTacacsPlusEp:
                b.filterkids('aaaTacacsPlusProviderGroup', 'aaaTacacsPlusProviderGroup', ['name', 'descr'])
                if hasattr(b, 'aaaTacacsPlusProviderGroup'):
                    for c in b.aaaTacacsPlusProviderGroup:
                        c.filterkids('aaaProviderRef', 'aaaProviderRef', ['name', 'descr', 'order'])
                        if hasattr(c, 'aaaProviderRef'):
                            for d in c.aaaProviderRef:
                                d.setparentattr(c, 'provGrp', 'name')
                                d.setparentattr(c, 'provGrpDescr', 'descr')
                                setattr(d, 'authType', 'TACACS+')
                b.filterkids('aaaTacacsPlusProvider', 'aaaTacacsPlusProvider', tacacs)
                if hasattr(b, 'aaaTacacsPlusProvider'):
                    for c in b.aaaTacacsPlusProvider:
                        try:
                            tmp = c.epgDn
                            #tmp2 = tmp.split('/')
                            tmp3 = tmp.split('/tn-')
                            tmp4 = tmp3[1].split('/mgmtp-')
                            epgTn = tmp4[0]
                            if '/oob-' in tmp4[1]:
                                tmp5 = tmp4[1].split('/oob-')
                                epgAp = tmp5[0]
                                epgName = tmp5[1]
                            elif '/inb' in tmp4[1]:
                                tmp5 = tmp4[1].split('/inb-')
                                epgAp = tmp5[0]
                                epgName = tmp5[1]
                            else:
                                tmp5 = tmp4[1].split('/')
                                epgAp = tmp5[0]
                                epgName = tmp5[1]
                            setattr(c, 'epgAp', epgAp)
                            setattr(c, 'epgTn', epgTn)
                            setattr(c, 'epgName', epgName)
                            setattr(c, 'authType', 'TACACS+')
                        except:
                            pass

    #endregion
    ''''''''''''''''''''''''''''''''''''''''''''''''''
    '''                Tenant                     '''
    ''''''''''''''''''''''''''''''''''''''''''''''''''
    #region Process Tenant
    ospfExtP_list = ['name', 'descr', 'nameAlias', 'areaId', 'areaType', 'areaCost', 'areaCtrl']
    l3extpath_list = ['addr', 'encap', 'ifInstT', 'mac', 'mode', 'mtu', 'tDn']
    prov = []
    cons = []
    mgmt_ip = []
    inbmgmt_ip = []
    for a in Tenant:
        a.setaciattr('name', 'name')
        #setattr(y, 'fvTenant', y.name) mgmtMgmtP
        a.filterkids('mgmtMgmtP', 'mgmtMgmtP', ['name'])
        a.filterkids('vzFilter', 'vzFilter', ['name', 'nameAlias', 'descr'])
        a.filterkids('vzBrCP', 'vzBrCP', ['name', 'nameAlias', 'descr'])
        a.filterkids('fvBD', 'fvBD', BD_attr)    ### Get Bridge Domains
        a.filterkids('fvAp', 'fvAp', ['name'])    ### Get App Profiles
        a.filterkids('fvCtx', 'fvCtx', ['name'])  ### Get VRFs
        a.filterkids('l3extOut', 'l3extOut', ['name', 'nameAlias']) ### Get L3out --- need kid: l3extRsEctx
        a.filterkids('dhcpRelayP', 'dhcpRelayP', ['name', 'descr', 'owner'])
        a.filterkids('l3extOut', 'l3extOut', ['name', 'descr', 'nameAlias'])
        if hasattr(a, 'l3extOut'): # l3extInstP
            for b in a.l3extOut:
                b.filterkids('ospfExtP', 'ospfExtP', ospfExtP_list)
                b.filterkids('l3extRsEctx', 'l3extRsEctx', ['tnFvCtxName', 'tDn'])
                b.filterkids('l3extLNodeP', 'l3extLNodeP', ['name', 'descr']) # Node Profile # l3extRsNodeL3OutAtt
                b.filterkids('l3extInstP', 'l3extInstP', ['name', 'descr'])  # External Subnet (EPG) # l3extSubnet - 'ip'
                if hasattr(b, 'ospfExtP'):
                    for c in b.ospfExtP:
                        setattr(c, 'l3out', b.name)
                        setattr(c, 'l3outdescr', b.descr)
                if hasattr(b, 'l3extLNodeP'):
                    for c in b.l3extLNodeP:
                        c.filterkids('l3extRsNodeL3OutAtt', 'l3extRsNodeL3OutAtt',['rtrId', 'rtrIdLoopBack', 'tDn'])
                        c.filterkids('l3extLIfP', 'l3extLIfP', ['addr', 'name'])
                        if hasattr(c, 'l3extLIfP'):
                            for d in c.l3extLIfP: # l3extRsPathL3OutAtt
                                d.filterkids('ospfRsIfPol', 'ospfRsIfPol', ['tnOspfIfPolName'])
                                d.filterkids('l3extRsPathL3OutAtt', 'l3extRsPathL3OutAtt', l3extpath_list)
                                if hasattr(d, 'l3extRsPathL3OutAtt'):
                                    for e in d.l3extRsPathL3OutAtt:
                                        if hasattr(e, 'mode'):
                                            if e.mode == 'regular':
                                                e.mode = 'trunk'
                                        if hasattr(e, 'tDn'):
                                            if 'protpaths' in e.tDn:
                                                path = splitDn(e.tDn, [4, 10, 8])
                                                setattr(e, 'pod', path[0])
                                                setattr(e, 'nodeId', path[1])
                                                inter = path[2].rstrip(']')
                                                setattr(e, 'interface', inter)
                                                setattr(e, 'tenant', a.name)
                                            else:
                                                path = splitDn(e.tDn, [4,6,8])
                                                setattr(e, 'pod', path[0])
                                                setattr(e, 'nodeId', path[1])
                                                inter = path[2] + '/' + path[3][:-1]
                                                setattr(e, 'interface', inter)
                                                setattr(e, 'tenant', a.name)
        if hasattr(a, 'mgmtMgmtP'):
            for b in a.mgmtMgmtP:
                b.filterkids('mgmtOoB', 'mgmtOoB', ['name'])
                b.filterkids('mgmtInB', 'mgmtInB', ['name'])
                if hasattr(b, 'mgmtOoB'):
                    for c in b.mgmtOoB:
                        c.filterkids('mgmtRsOoBCtx', 'mgmtRsOoBCtx', ['tnFvCtxName'])
                        c.filterkids('mgmtRsOoBStNode', 'mgmtRsOoBStNode', ['addr', 'gw', 'tDn'])
                        if hasattr(c, 'mgmtRsOoBCtx'):
                            for d in c.mgmtRsOoBCtx:
                                if hasattr(c, 'mgmtRsOoBStNode'):
                                    for e in c.mgmtRsOoBStNode:
                                        setattr(e, 'vrf', d.tnFvCtxName)
                                        setattr(e, 'epg', c.name)
                                        mgmt_ip = mgmt_ip + [e]
                if hasattr(b, 'mgmtInB'):
                    for c in b.mgmtInB:
                        c.filterkids('mgmtRsMgmtBD', 'mgmtRsMgmtBD', ['tnFvBDName'])
                        c.filterkids('mgmtRsInBStNode', 'mgmtRsInBStNode', ['addr', 'gw', 'tDn'])
                        if hasattr(c, 'mgmtRsMgmtBD'):
                            for d in c.mgmtRsMgmtBD:
                                if hasattr(c, 'mgmtRsInBStNode'):
                                    for e in c.mgmtRsInBStNode:
                                        setattr(e, 'bd', d.tnFvBDName)
                                        setattr(e, 'epg', c.name)
                                        inbmgmt_ip = inbmgmt_ip + [e]
        if hasattr(a, 'dhcpRelayP'):
            dhcpepg = []
            dhcpaddr = []
            for b in a.dhcpRelayP:
                b.filterkids('dhcpProvDhcp', 'dhcpProvDhcp', ['name', 'descr', 'addr'])
                if hasattr(b, 'dhcpProvDhcp'):
                    for c in b.dhcpProvDhcp:
                        dhcpepg = dhcpepg + [c.name]
                        dhcpaddr = dhcpaddr + [c.addr]
                    setattr(b, 'dhcpepg', ','.join(dhcpepg))
                    setattr(b, 'dhcpaddr', ','.join(dhcpaddr))
                    b.setparentattr(a, 'owner', 'name')
        if hasattr(a, 'vzFilter'):
            entry_list = ['name', 'nameAlias', 'descr', 'sFromPort', 'sToPort', 'dFromPort', 'dToPort',
                          'prot', 'stateful', 'etherT']
            for z in getattr(a, 'vzFilter'):
                z.filterkids('vzEntry', 'vzEntry', entry_list)
                if hasattr(z, 'vzEntry'):
                    for y in z.vzEntry:
                        y.setparentattr(z, 'filterAlias', 'nameAlias')
                        y.setparentattr(z, 'filterdescr', 'descr')
                        if hasattr(y, 'sToPort') and hasattr(y, 'sFromPort'):
                            if y.sFromPort != y.sToPort:
                                b = '-'.join([y.sFromPort, y.sToPort])
                            else:
                                b = y.sFromPort
                            setattr(y, 'srcPort', b)
                        if hasattr(y, 'dToPort') and hasattr(y, 'dFromPort'):
                            if y.dFromPort != y.dToPort:
                                b = '-'.join([y.dFromPort, y.dToPort])
                            else:
                                b = y.dFromPort
                            setattr(y, 'destPort', b)


                #if hasattr(z, 'vzEntry'):
        if hasattr(a, 'vzBrCP'):
            for z in a.vzBrCP:
                z.filterkids('vzSubj', 'vzSubj', ['name'])
                z.filterkids('vzRtProv', 'vzRtProv', ['tDn'])
                z.filterkids('vzRtCons', 'vzRtCons', ['tDn'])
                setattr(z, a.type, a.name)
                if hasattr(z, 'vzSubj'):
                    for y in z.vzSubj:
                        setattr(y, a.type, a.name)
                        setattr(y, z.type, z.name)
                        y.filterkids('vzRsSubjFiltAtt', 'vzRsSubjFiltAtt')
                        if hasattr(y, 'vzRsSubjFiltAtt'):
                            filter_list = []
                            for b in y.vzRsSubjFiltAtt:
                                sub_str = b.attributes['tnVzFilterName'] + '(' + b.attributes['action'] + ')'
                                filter_list.append(sub_str)
                        filters = ','.join(filter_list)
                        setattr(y, 'filter_list', filters)


        for z in a.fvCtx:
            setattr(z, a.type, a.name)
            z.setaciattr('name', 'name')
        for z in a.fvBD:
            setattr(z, 'ip', '')
            setattr(z, 'tenant', a.name)
            #z.setaciattrlist(BD_attr)
            z.filterkids('fvSubnet', 'fvSubnet', ['name', 'ip'], ['ip'])
            z.filterkids('fvRsCtx', 'fvRsCtx', ['tnFvCtxName'], ['tnFvCtxName'])  ### VRF: "tnFvCtxName"
            z.filterkids('fvRsBDToOut', 'fvRsBDToOut', ['tnL3extOutName'], ['tnL3extOutName'])  ### L3out: "tnL3extOutName"
        a.fvBD.sort(key=lambda x: (x.ip, x.name), reverse=False)
            ### for a in
        pprint(a.fvBD)

        ''' Get EPG Information '''
        for x in a.fvAp:
            x.setaciattr('name', 'name')
            setattr(x, a.type, a.name)
            x.filterkids('fvAEPg', 'fvAEPg', EPG_attr)
            if hasattr(x, 'fvAEPg'): # fvRsPathAtt
                x.fvAEPg.sort(key=lambda x: x.name, reverse=False)
                for y in x.fvAEPg: #
                    y.setaciattr('name', 'name')
                    setattr(y, a.type, a.name)
                    setattr(y, x.type, x.name)
                    y.filterkids('fvRsCons', 'fvRsCons', ['tnVzBrCPName', 'tDn'])
                    y.filterkids('fvRsProv', 'fvRsProv', ['tnVzBrCPName', 'tDn'])
                    y.filterkids('fvRsBd', 'fvRsBd', ['tnFvBDName'])
                    y.filterkids('fvCtrctCtxDefCont', 'fvCtrctCtxDefCont')
                    y.filterkids('fvRtFuncToEpg', 'fvRtFuncToEpg')
                    y.filterkids('fvRsDomAtt', 'fvRsDomAtt', ['epgCos'])
                    y.filterkids('fvRsPathAtt', 'fvRsPathAtt', ['encap', 'instrImedcy', 'mode', 'tDn'])
                    if hasattr(y, 'fvRsPathAtt'):
                        for b in y.fvRsPathAtt:
                            if hasattr(b, 'tDn'):
                                setattr(b, 'epg', y.name)
                                if 'protpaths-' in b.tDn:
                                    interface = splitDn(b.tDn, [4, 10, 8])
                                    inter = interface[2].rstrip(']')
                                else:
                                    interface = splitDn(b.tDn, [4,6,8])
                                    inter = interface[2] + '/' + interface[3][:-1]
                                setattr(b, 'pod', interface[0])
                                setattr(b, 'leaf', interface[1])
                                setattr(b, 'interface', inter)
                                if b.mode == 'regular':
                                    b.mode = 'trunk'
                        y.fvRsPathAtt.sort(key=lambda x: (x.pod, x.leaf, x.interface), reverse=True)

                    for b in y.fvRsBd:  ### Single BD Associated
                        if hasattr(b, 'tnFvBDName'):
                            setattr(y, 'tnFvBDName', b.tnFvBDName)
                    dom_list = []
                    if hasattr(y, 'fvRsDomAtt'):
                        for c in y.fvRsDomAtt:  ###
                            for cc in Domain:
                                if cc.attributes['dn'] == c.attributes['tDn']:
                                    dom_list.append(cc.attributes['name'])
                        dom = ','.join(dom_list)
                        setattr(y, 'DOM', dom)   ### Set list of domains to DOM attr


                EPG.append(x.fvAEPg)    ### Copy EPG to EPG list
        ''' Copy objects to specific list '''
        AP.append(a.fvAp)
        BD.append(a.fvBD)
        VRF.append(a.fvCtx)
    #Subnet = aci_obj2.filteraciobjlist(Full_Tenant, 'fvSubnet')
    #EPG = aci_obj2.filteraciobjlist(Full_Tenant, 'fvAEPg')
    #AP = aci_obj2.filteraciobjlist(Full_Tenant, 'fvAP')
    #fvnsVlanInstP
    #endregion
    ''''''''''''''''''''''''''''''''''''''''''''''''''
    '''                Infra                    '''
    ''''''''''''''''''''''''''''''''''''''''''''''''''
    #region Process Infra
    infraInfra = aci_obj2.filteraciobjlist(Infra, 'infraInfra')
    intPolattr = ['name', 'ctrl', 'descr', 'speed', 'adminSt', 'mode', 'adminTxSt', 'adminRxSt', 'vlanScope', 'minLinks',
                  'maxLinks', 'autoNeg']
    int_policies = []
    FWS = ['domainValidation', 'enforceSubnetCheck', 'enableRemoteLeafDirect', 'validateOverlappingVlans',
           'reallocateGipo', 'unicastXrEpLearnDisable', 'opflexpAuthenticateClients']
    for a in infraInfra:
        a.filterkids('infraSetPol', 'infraSetPol', FWS)
        a.filterkids('epIpAgingP', 'epIpAgingP', ['adminSt'])
        a.filterkids('infraCPMtuPol', 'infraCPMtuPol', ['CPMtu'])
        a.filterkids('dhcpRelayP', 'dhcpRelayP', ['name', 'descr', 'owner'])
        if hasattr(a, 'dhcpRelayP'):
            dhcpepg = []
            dhcpaddr = []
            for b in a.dhcpRelayP:
                b.filterkids('dhcpProvDhcp', 'dhcpProvDhcp', ['name', 'descr', 'addr'])
                if hasattr(b, 'dhcpProvDhcp'):
                    for c in b.dhcpProvDhcp:
                        dhcpepg = dhcpepg + [c.name]
                        dhcpaddr = dhcpaddr + [c.addr]
                    setattr(b, 'dhcpepg', ','.join(dhcpepg))
                    setattr(b, 'dhcpaddr', ','.join(dhcpaddr))



        a.filterkids('fvnsVlanInstP', 'fvnsVlanInstP', ['name', 'descr'])
        if hasattr(a, 'fvnsVlanInstP'):
            vlan_domain = []
            for b in a.fvnsVlanInstP:
                b.filterkids('fvnsRtVlanNs', 'fvnsRtVlanNs', ['tCl', 'tDn'])
                if hasattr(b, 'fvnsRtVlanNs'):
                    for c in b.fvnsRtVlanNs:
                        vlan_domain = vlan_domain + [c.tDn]
                setattr(a, 'vlan-dom', vlan_domain)
                b.filterkids('fvnsEncapBlk', 'fvnsEncapBlk', ['allocMode', 'from', 'to'])
                if hasattr(b, 'fvnsEncapBlk'):
                    vl = []
                    for c in b.fvnsEncapBlk:
                        tmp1 = getattr(c, 'from')
                        tmp1 = tmp1.split('-')
                        tmp2 = getattr(c, 'to')
                        tmp2 = tmp2.split('-')
                        range =  tmp1[1] + '-' + tmp2[1]
                        vl = vl + [range]
                        setattr(b, 'allocMode', c.allocMode)
                    vlanrange = ','.join(vl)
                setattr(b, 'vlanrange', vlanrange)



        # Interface Policies
        a.filterkids('fabricHIfPol', 'fabricHIfPol', intPolattr)
        a.fabricHIfPol.sort(key=lambda x: x.name)
        int_policies = int_policies + a.fabricHIfPol
        a.filterkids('lacpLagPol', 'lacpLagPol', intPolattr)
        a.lacpLagPol.sort(key=lambda x: x.name)
        int_policies = int_policies + a.lacpLagPol
        a.filterkids('stpIfPol', 'stpIfPol', intPolattr)
        a.stpIfPol.sort(key=lambda x: x.name)
        int_policies = int_policies + a.stpIfPol
        #a.filterkids('stormctrlIfPol', 'stormctrlIfPol')
        #a.filterkids('qosSdIfPol', 'qosSdIfPol')
        #setIntPol(a.qosSdIfPol)
        #a.filterkids('qosPfcIfPol', 'qosPfcIfPol')
        #setIntPol(a.qosPfcIfPol)
        #a.filterkids('qosIngressDppIfPol', 'qosIngressDppIfPol')
        #setIntPol(a.qosIngressDppIfPol)
        a.filterkids('qosEgressDppIfPol', 'qosEgressDppIfPol', intPolattr)
        a.qosEgressDppIfPol.sort(key=lambda x: x.name)
        int_policies = int_policies + a.qosEgressDppIfPol
        a.filterkids('qosDppIfPol', 'qosDppIfPol', intPolattr)
        a.qosDppIfPol.sort(key=lambda x: x.name)
        int_policies = int_policies + a.qosDppIfPol
        a.filterkids('qoeIfPol', 'qoeIfPol', intPolattr)
        a.qoeIfPol.sort(key=lambda x: x.name)
        int_policies = int_policies + a.qoeIfPol
        a.filterkids('monIfInfraPol', 'monIfInfraPol', intPolattr)
        a.monIfInfraPol.sort(key=lambda x: x.name)
        int_policies = int_policies + a.monIfInfraPol
        a.filterkids('mcpIfPol', 'mcpIfPol', intPolattr)
        a.mcpIfPol.sort(key=lambda x: x.name)
        int_policies = int_policies + a.mcpIfPol
        #setIntPol(a.mcpIfPol)
        a.filterkids('lldpIfPol', 'lldpIfPol', intPolattr)
        a.lldpIfPol.sort(key=lambda x: x.name)
        int_policies = int_policies + a.lldpIfPol
        a.filterkids('l2PortSecurityPol', 'l2PortSecurityPol', intPolattr)
        a.l2PortSecurityPol.sort(key=lambda x: x.name)
        int_policies = int_policies + a.l2PortSecurityPol
        a.filterkids('l2PortAuthPol', 'l2PortAuthPol', intPolattr)
        a.l2PortAuthPol.sort(key=lambda x: x.name)
        int_policies = int_policies + a.l2PortAuthPol
        a.filterkids('l2IfPol', 'l2IfPol', intPolattr)
        a.l2IfPol.sort(key=lambda x: x.name)
        int_policies = int_policies + a.l2IfPol
        a.filterkids('hIfPol', 'hIfPol', intPolattr)
        a.hIfPol.sort(key=lambda x: x.name)
        int_policies = int_policies + a.hIfPol
        a.filterkids('fcIfPol', 'fcIfPol', intPolattr)
        a.fcIfPol.sort(key=lambda x: x.name)
        int_policies = int_policies + a.fcIfPol
        a.filterkids('coppIfPol', 'coppIfPol', intPolattr)
        a.coppIfPol.sort(key=lambda x: x.name)
        int_policies = int_policies + a.coppIfPol
        a.filterkids('cdpIfPol', 'cdpIfPol', intPolattr)
        a.cdpIfPol.sort(key=lambda x: x.name)
        int_policies = int_policies + a.cdpIfPol
        a.filterkids('fvnsVlanInstP', 'fvnsVlanInstP')    ### Get VLAN Pools
        for b in a.fvnsVlanInstP:
            b.setaciattr('name', 'name')
            b.filterkids('fvnsRtVlanNs', 'fvnsRtVlanNs')  ### Get Bridge Domains
            b.filterkids('fvnsEncapBlk', 'fvnsEncapBlk')
            dom_list = []
            for c in b.fvnsRtVlanNs:  ###
                for cc in Domain:
                    if cc.attributes['dn'] == c.attributes['tDn']:
                        dom_list.append(cc.attributes['name'])
            setattr(b, 'DOM', dom_list)  ### Set list of domains to DOM attr

    # Domain information
    for a in Domain:
        if a.type != 'infraRsVlanNs':
            for b in Domain:
                if b.type == 'physDomP':
                    tmp = 'phys-' + b.name + '/'
                elif b.type == 'vmmDomP':
                    tmp = 'vmmp-VMware-' + b.name + '/'
                elif b.type == 'l3extDomP':
                    tmp = 'l3dom-' + b.name + '/'
                elif b.type == 'l2extDomP':
                    tmp = 'l2dom-' + b.name + '/'
                else:
                    tmp = 'NOT FOUND'
                if tmp != 'NOT FOUND':
                    for c in Domain:
                        if c.type == 'infraRsVlanNs':
                            if tmp in c.attributes['dn']:
                                tmp2 = c.attributes['tDn']
                                tmp3 = tmp2.split('-[')
                                tmp4 = tmp3[1].split(']-')
                                vlan = tmp4[0]
                                setattr(b, 'vlanpool', vlan)
    #endregion
    ''''''''''''''''''''''''''''''''''''''''''''''''''
    '''                Fabric                      '''
    ''''''''''''''''''''''''''''''''''''''''''''''''''
    #region Process Interface Policies and Portgroups
    snmpDG = []
    syslogDG = []
    podPol = []
    for a in Fabric: # fabricPodPGrp fabricFuncP
        a.filterkids('datetimeFormat', 'datetimeFormat', ['displayFormat', 'showOffset', 'tz'])
        a.filterkids('mgmtConnectivityPrefs', 'mgmtConnectivityPrefs', ['interfacePref'])
        a.filterkids('aaaPreLoginBanner', 'aaaPreLoginBanner', ['message', 'switchMessage', 'guiTextMessage'])
        a.filterkids('bgpInstPol', 'bgpInstPol', ['name'])
        a.filterkids('snmpGroup', 'snmpGroup', ['name', 'descr'])
        a.filterkids('syslogGroup', 'syslogGroup', ['name', 'descr', 'format'])
        a.filterkids('syslogGroup', 'syslogGroup', ['name', 'descr', 'format'])
        a.filterkids('fabricFuncP', 'fabricFuncP', ['name', 'descr'])
        if hasattr(a, 'fabricFuncP'):
            for b in a.fabricFuncP:
                b.filterkids('fabricPodPGrp', 'fabricPodPGrp', ['name', 'descr'])
                if hasattr(b, 'fabricPodPGrp'):
                    for c in b.fabricPodPGrp:
                        c.filterkids('fabricRtPodPGrp', 'fabricRtPodPGrp', ['tDn'])
                        c.filterkids('fabricRsSnmpPol', 'fabricRsSnmpPol', ['tnSnmpPolName'])
                        c.filterkids('fabricRsPodPGrpIsisDomP', 'fabricRsPodPGrpIsisDomP', ['tnIsisDomPolName'])
                        c.filterkids('fabricRsPodPGrpCoopP', 'fabricRsPodPGrpCoopP', ['tnCoopPolName'])
                        c.filterkids('fabricRsPodPGrpBGPRRP', 'fabricRsPodPGrpBGPRRP', ['tnBgpInstPolName'])
                        c.filterkids('fabricRsTimePol', 'fabricRsTimePol', ['tnDatetimePolName'])
                        c.filterkids('fabricRsMacsecPol', 'fabricRsMacsecPol', ['tnMacsecFabIfPolName'])
                        c.filterkids('fabricRsCommPol', 'fabricRsCommPol', ['tnCommPolName'])
                        for d in c.fabricRsSnmpPol:
                            setattr(c, 'tnSnmpPolName', d.tnSnmpPolName)
                        for d in c.fabricRsPodPGrpIsisDomP:
                            setattr(c, 'tnIsisDomPolName', d.tnIsisDomPolName)
                        for d in c.fabricRsPodPGrpCoopP:
                            setattr(c, 'tnCoopPolName', d.tnCoopPolName)
                        for d in c.fabricRsPodPGrpBGPRRP:
                            setattr(c, 'tnBgpInstPolName', d.tnBgpInstPolName)
                        for d in c.fabricRsTimePol:
                            setattr(c, 'tnDatetimePolName', d.tnDatetimePolName)
                        for d in c.fabricRsMacsecPol:
                            setattr(c, 'tnMacsecFabIfPolName', d.tnMacsecFabIfPolName)
                        for d in c.fabricRsCommPol:
                            setattr(c, 'tnCommPolName', d.tnCommPolName)
                        podPol.append(c)
        if hasattr(a, 'syslogGroup'):
            for b in a.syslogGroup: #
                b.filterkids('syslogRemoteDest', 'syslogRemoteDest', ['name', 'descr', 'adminState', 'epgDn', 'host',
                                                                      'severity', 'forwardingFacility', 'format',
                                                                      'port'])
                if hasattr(b, 'syslogRemoteDest'):
                    for c in b.syslogRemoteDest:
                        setattr(c, 'syslogGroup', b.name)
                        setattr(c, 'syslogGroupDescr', b.descr)
                        setattr(c, 'format', b.format)
                        syslogDG.append(c)


        if hasattr(a, 'snmpGroup'):
            for b in a.snmpGroup: #
                b.filterkids('snmpTrapDest', 'snmpTrapDest', ['host', 'descr', 'port', 'secName', 'ver', 'v3SecLvl',
                                                              'epgDn'])
                if hasattr(b, 'snmpTrapDest'):
                    for c in b.snmpTrapDest:
                        setattr(c, 'snmpGroup', b.name)
                        setattr(c, 'snmpGroupDescr', b.descr)
                        snmpDG.append(c)
        if hasattr(a, 'bgpInstPol'):
            for b in a.bgpInstPol:
                b.filterkids('bgpAsP', 'bgpAsP', ['asn'])
                b.filterkids('bgpRRP', 'bgpRRP', ['name'])
                if hasattr(b, 'bgpRRP'):
                    for c in b.bgpRRP:
                        c.filterkids('bgpRRNodePEp', 'bgpRRNodePEp', ['id', 'descr', 'podId'])
                        if hasattr(c, 'bgpRRNodePEp'):
                            for d in c.bgpRRNodePEp:
                                if hasattr(b, 'bgpAsP'):
                                    for e in b.bgpAsP:
                                        if hasattr(e, 'asn'):
                                            setattr(d, 'asn', e.asn)
                                            setattr(d, 'rr', b.name)
    listofdicts = []
    listofdicts.append({'kid': 'infraRsStpIfPol', 'name': 'tnStpIfPolName'})
    listofdicts.append({'kid': 'infraRsMcpIfPol', 'name': 'tnMcpIfPolName'})
    listofdicts.append({'kid': 'infraRsCdpIfPol', 'name': 'tnCdpIfPolName'})
    listofdicts.append({'kid': 'infraRsL2IfPol', 'name': 'tnL2IfPolName'})
    listofdicts.append({'kid': 'infraRsLldpIfPol', 'name': 'tnLldpIfPolName'})
    listofdicts.append({'kid': 'infraRsHIfPol', 'name': 'tnFabricHIfPolName'})
    for a in PortGroup:
        a.setaciattr('descr', 'descr')
        for b in listofdicts:
            a.filterkids(b['kid'], b['kid'], [b['name']])
            a.setsinglechildattr(b['kid'], b['name'], b['name'])
        a.filterkids('infraRsAttEntP', 'infraRsAttEntP', ['tDn'])
        if hasattr(a, 'infraRsAttEntP'):
            for b in a.infraRsAttEntP:
                tmp = b.tDn
                if 'attentp-' in tmp:
                    tmp2 = tmp.split('attentp-')
                    setattr(a, 'aep', tmp2[1])
    PortGroup.sort(key=lambda x: x.name)
    listofdicts.append({'kid': 'infraRsLacpPol', 'name': 'tnLacpLagPolName'})
    for a in PCPortGroup:
        a.setaciattr('descr', 'descr')
        for b in listofdicts:
            a.filterkids(b['kid'], b['kid'], [b['name']])
            a.setsinglechildattr(b['kid'], b['name'], b['name'])
        a.filterkids('infraRsAttEntP', 'infraRsAttEntP', ['tDn'])
        if hasattr(a, 'infraRsAttEntP'):
            for b in a.infraRsAttEntP:
                tmp = b.tDn
                if 'attentp-' in tmp:
                    tmp2 = tmp.split('attentp-')
                    setattr(a, 'aep', tmp2[1])
    PCPortGroup.sort(key=lambda x: x.name)

    #endregion
    #region Process AEP
    aepepg_list = ['encap', 'mode', 'tDn']
    for a in AEP:
        a.setaciattrlist(['name', 'descr'])
        a.filterkids('infraGeneric', 'infraGeneric')
        a.filterkids('infraRsDomP', 'infraRsDomP', ['tCl', 'tDn'])
        if hasattr(a, 'infraGeneric'):
            for b in a.infraGeneric:
                b.filterkids('infraRsFuncToEpg', 'infraRsFuncToEpg', aepepg_list)
                if hasattr(b, 'infraRsFuncToEpg'):
                    for c in b.infraRsFuncToEpg:
                        epg_ls = splitDn(c.tDn)
                        setattr(c, 'tn', epg_ls[0])
                        setattr(c, 'ap', epg_ls[1])
                        setattr(c, 'epg', epg_ls[2])
                        setattr(c, 'aep', a.name)
                        setattr(c, 'aepDescr', a.descr)
                        if c.mode == 'regular':
                            c.mode = 'trunk'
                    b.infraRsFuncToEpg.sort(key=lambda x: x.encap)
        if hasattr(a, 'infraRsDomP'):
            aepdom_list = []
            for b in a.infraRsDomP:
                for bb in Domain:
                    if bb.attributes['dn'] == b.tDn:
                        setattr(b, 'domName', bb.name)
                        setattr(b, 'domType', bb.type)
                        setattr(c, 'aep', a.name)
                        setattr(c, 'aepDescr', a.descr)
                        aepdom_list.append(b.domName)
            setattr(a, 'domList', ','.join(aepdom_list))
    AEP.sort(key=lambda x: x.name)
    #endregion
    ''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
    '''                  Merge Data                            '''
    ''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
    # Merge Pod and mgmt_ip
    for a in Pod:
        for b in mgmt_ip:
            if b.tDn == a.dn:
                setattr(a, 'mgmtip', b.addr)
                setattr(a, 'gw', b.gw)
                setattr(a, 'vrf', b.vrf)
                setattr(a, 'epg', b.epg)
        for b in inbmgmt_ip:
            if b.tDn == a.dn:
                setattr(a, 'inbmgmtip', b.addr)
                setattr(a, 'inbgw', b.gw)
                setattr(a, 'inbbd', b.bd)
                setattr(a, 'inbepg', b.epg)

    ''' def create_file(excel_file='test') '''

    pprint('Creating Excel File: ' + excel_file)
    wb = write_pyxl.mkXLSX(excel_file, 'HW Overview')
    '''# wb = xlsxwriter.Workbook(excel_file)
    # CAT_FORMAT_GRAY = wb.add_format({'border': 2, 'bold': True, 'font_color': 'white', 'bg_color': 'gray',
                                'align': 'center'})
    CAT_FORMAT = wb.add_format({'border': 2, 'bold': True, 'font_color': 'white', 'bg_color': 'green',
                                'align': 'center'})
    HL_FORMAT = wb.add_format({'border': 2, 'bold': True, 'font_color': 'white', 'bg_color': 'green'})
    HL_FORMAT_GRAY = wb.add_format({'border': 2, 'bold': True, 'font_color': 'white', 'bg_color': 'gray'})
    D_FORMAT = wb.add_format({'border': 1, 'bold': True, 'font_color': 'black', 'bg_color': 'white'})
    UP_FORMAT = wb.add_format({'bold': True, 'font_color': 'black', 'bg_color': 'white'})
    cell_format = [CAT_FORMAT]'''
    #region Write data Variables
    switch_hl_keylist = ['name', 'nodeId', 'podId', 'id', 'nodeRole', 'model', 'runningVer']
    switch_hl_namelist = ['Name', 'Node ID', 'Pod', 'ID', 'Role', 'Model', 'Version']
    ''' System Overview '''
    pod= ['name', 'id', 'role', 'model', 'serial', 'version', 'adSt', 'mgmtip', 'gw', 'vrf', 'epg', 'inbmgmtip',
          'inbgw', 'inbbd', 'inbepg']
    pod_hl = ['Node Name', 'Node ID', 'Role', 'Model', 'Serial Number', 'Software Version', 'Admin State', 'OOB Mgmt IP',
              'OOB Gateway', 'OOB VRF', ' OOB EPG', 'INB Mgmt IP', 'INB Gateway', 'INB BD', 'INB EPG']
    bgp=['rr', 'podId', 'id', 'descr', 'asn']
    bgp_hl = ['Route Reflector Polciy', 'Pod', 'Node ID', 'Description', 'BGP ASN']
    mtu_hl = ['Control Plane MTU']
    mtu = ['CPMtu']
    mgmt_hl = ['APIC Connectivity Preference']
    mgmt = ['interfacePref']
    ipage_hl = ['IP Aging']
    ipage = ['adminSt']
    fws_hl = ['Disable Remote EP Learning', 'Enforce Subnet Check', 'Reallocate Gipo', 'Enforce Domain Validation',
              'Opflex Client Authentication']
    fws = ['unicastXrEpLearnDisable', 'enforceSubnetCheck', 'reallocateGipo', 'domainValidation', 'opflexpAuthenticateClients']
    tz_hl = ['Disaply Format', 'Show Offset', 'Timezone']
    tz=['displayFormat', 'showOffSet', 'tz']

    ''' Tenant Data '''
    Tenant_hl_namelist = ['Tenant', 'VRF', 'Stretched']
    BD_hl_keylist = ['fvTenant', 'name', 'nameAlias', 'tnFvCtxName', 'ip', 'mtu', 'descr', 'mac', 'unicastRoute',
                    'mcastAllow', 'tnL3extOutName', 'unkMacUcastAct', 'arpFlood', 'ipLearning', 'intersiteL2Stretch']
    BD_hl_namelist = ['Tenant', 'Bridge Domain', 'Alias', 'VRF', 'IP', 'MTU', 'Description', 'MAC', 'Unicast Routing',
                      'Multicast Routing', 'L3 Out', 'unkMacUcastAct', 'Arp Flood', 'IP Learning', 'Intersite Stretch']
    EPG_hl_namelist = ['Tenant', 'App Profile', 'EPG', 'Alias', 'BD', 'Domains', 'Description']
    EPG_hl_keylist = ['fvTenant', 'fvAp', 'name', 'nameAlias', 'tnFvBDName', 'DOM', 'descr']
    CON_hl_namelist = ['Tenant', 'Contract', 'Subject', 'Filters']
    CON_hl_keylist = ['fvTenant', 'vzBrCP', 'name', 'filter_list']
    FILTER_hl_namelist = ['Tenant', 'Filter', 'Filter Alias', 'Filter Description', 'Filter Entry',
                          'Entry Alias', 'Entry Description', 'Ether Type', 'Source Port', 'Destination Port',
                          'Protocol', 'Stateful']
    FILTER_hl_keylist = ['fvTenant', 'vzFilter', 'filterAlias', 'filterdescr', 'name', 'nameAlias', 'descr',
                         'etherT', 'srcPort', 'destPort', 'prot', 'stateful']
    EC_namelist = ['Tenant', 'App Profile', 'EPG', 'EPG Alias', 'Contract', 'Provided', 'Consumed']
    EC_keylist = ['fvTenant', 'fvAp', 'name', 'nameAlias', 'contract', 'prov', 'cons']
    static = ['pod', 'leaf', 'interface', 'encap', 'mode']
    static_hl = ['Pod', 'Node ID', 'Interface','Encapsulation', 'Mode']

    ''' Fabric Access Data '''
    # DHCP
    dhcp_hl = ['DHCP Relay', 'Destination EPG', 'DHCP Server', 'Policy Owner', 'Description']
    dhcp = ['name', 'dhcpepg', 'dhcpaddr', 'owner', 'descr']
    # VLAN Pools
    vlan_pool_hl = ['VLAN Pools', 'VLANs', 'Alocation Mode', 'Description']
    vlan_pool = ['name', 'vlanrange', 'allocMode', 'descr']
    domains_hl = ['Domain', 'VLAN Pool', 'Description', 'Type']
    domains = ['name', 'vlanpool', 'descr', 'type']
    pg = ['name', 'descr', 'tnFabricHIfPolName', 'aep', 'tnLacpLagPolName', 'tnLldpIfPolName', 'tnCdpIfPolName',
          'tnMcpIfPolName' ]
    pg_hl = ['Policy Group', 'Description', 'Link Level', 'AEP', 'Port-Channel Policy', 'LLDP', 'CDP', 'MCP']
    ''' Interface Policies '''
    IntPol_hl_namelist = ['Interface Policies', 'Policy Type', 'Policy', 'Config', 'Description', 'Adv Config']
    L2interface_hl = ['VLAN Scope', 'Config', 'Description']
    L2interface = ['name', 'vlanScope', 'descr']
    lacp_hl = ['Port-Channel Policies', 'Mode', 'Description', 'Adv Config', 'Min Links', 'Max Links']
    lacp = ['name', 'mode', 'descr', 'ctrl', 'minLinks', 'maxLinks']
    cdp_hl = ['CDP Policies', 'Admin State', 'Description']
    cdp = ['name', 'adminSt', 'descr']
    mcp_hl = ['MCP Policies', 'Admin State', 'Description']
    mcp = ['name', 'adminSt', 'descr']
    lldp_hl = ['LLDP Policies', 'TX State', 'RX State', 'Description']
    lldp = ['name', 'adminTxSt', 'adminRxSt', 'descr']
    link_hl = ['Link Level Policies', 'Speed', 'Auto Negotiation', 'Description']
    link = ['name', 'speed', 'autoNeg', 'descr']
    stp_hl = ['Spanning-Tree Policies', 'Config', 'Description']
    stp = ['name', 'ctrl', 'descr']
    aep_dom = ['name', 'descr', 'domList']
    aep_dom_hl = ['AEP', 'Description', 'Domain(s)']
    aep_epg_hl = ['Tenant', 'App Profile', 'EPG', 'Encapsulation', 'Mode', ]
    aep_epg = ['tn', 'ap', 'epg', 'encap', 'mode']
    IntPol_hl_namelist = ['Interface Policies', 'Policy Type', 'Policy', 'Config', 'Description', 'Adv Config']
    IntPol_hl_keylist3 = ['type', 'name', 'speed', 'descr', '']
    IntPol_hl_keylist = ['type', 'name', 'ctrl', 'descr', '']
    podPol_key = ['name', 'descr', 'tnDatetimePolName', 'tnSnmpPolName', 'tnCommPolName', 'tnBgpInstPolName',
                  'tnCoopPolName', 'tnIsisDomPolName', 'tnMacsecFabIfPolName', ]
    podPol_hl = ['Pod Policy', 'Description', 'Date/Time Policy', 'SNMP Policy', 'Communication Policy', 'BGP Policy',
                  'COOP Policy', 'IS-IS Policy', 'MAC Security Policy', ]

    ''''''''''''''
    '''                   Admin                      '''
    provGrp = ['authType', 'provGrp', 'provGrpDescr', 'name', 'descr', 'order']
    provGrp_hl = ['Authentication Type', 'Domain', 'Domain Description', 'Auth Provider', 'Auth Description', 'Order']
    tac = ['name', 'descr', 'authProtocol', 'port', 'operState', 'monitorServer', 'epgTn', 'epgAp', 'epgName']
    rad = ['name', 'descr', 'authProtocol', 'authPort', 'operState', 'monitorServer','epgTn', 'epgAp', 'epgName']
    auth_hl = ['Provider', 'Description', 'Authentication Protocol', 'Port', 'Operation State', 'Monitor Server',
               'EPG Tenant', 'EPG App Profile', 'EPG']
    fault = ['severity', 'domain', 'type', 'code', 'count', 'cause', 'rule', 'subject', 'descr']
    fault_hl = ['Severity', 'Domain', 'Type', 'Code', 'Count', 'Cause', 'Rule', 'Subject', 'Description']
    snmpDG_key = ['snmpGroup', 'snmpGroupDescr', 'host', 'ver', 'port', 'secName', 'v3SecLvl']
    snmpDG_hl = ['SNMP Dest Group', 'Description', 'Host', 'SNMP Version', 'Port', 'Security Name', 'Security Level']
    syslogDG_key = ['syslogGroup', 'syslogGroupDescr', 'host', 'format', 'port', 'adminState', 'severity',
                  'forwardingFacility']
    syslogDG_hl = ['SYSLOG Dest Group', 'Description', 'Host', 'Message Format', 'Port', 'Admin State', 'Severity',
                 'Forwarding Facility']
    #endregion

    #region Create Worksheets
    for a in worksheetNames:
        write_pyxl.addSheet(wb, a)
    #wsHw = wb.add_worksheet('HW Overview')
    #wsSystem = write_pyxl.addSheet(wb, 'System')
    # wsAdmin = wb.add_worksheet('Admin')
    #wsFabricAccess = wb.add_worksheet('Fabric Access')
    #wsFabricPolcies = wb.add_worksheet('Fabric Policies')
    # wsL3outs = wb.add_worksheet('L3 Outs')
    Tenant_list = []
    Tenant_obj_list = {}
    for a in Tenant:
        Tenant_list.append(a.name)
        Tenant_obj_list.update({a.name: 'Tenant-' + a.name})
        write_pyxl.addSheet(wb, a.name)

    '''      Faults Tab. Should be last Tab    '''
    #wsFaults = wb.add_worksheet('Faults')
    #endregion
    ''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
    '''                        Switch Overview Section                   '''
    ''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
    #region Switch Overview
    ROW = 1
    COL = 1
    wsHw = wb['HW Overview']
    ROW = write_pyxl.write_merge(wsHw, ROW, COL, ROW, len(pod_hl), 'Node Overview')
    ROW = write_pyxl.write_hl_category(wsHw, ROW, COL, 'Cisco ACI Nodes', pod_hl)
    for a in Pod:
        if a.type == 'fabricNode':
            ROW = write_pyxl.write_line(wsHw, a, pod, ROW, COL)
    #write_data.write_hl(wsTenant, Tenant_hl_namelist, 0, 1,)
    #write_data.write_hl(wsSystem, System_hl_namelist, 0, 1,)
    #endregion
    ''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
    '''                        System Overview Section                   '''
    ''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
    #region Write System Overview
    ROW = 2
    COL = 1
    wsSystem = wb['System']
    ROW = write_pyxl.write_merge(wsSystem, ROW, COL, ROW, len(bgp_hl), 'System Overview')
    for a in infraInfra:
        if hasattr(a, 'infraCPMtuPol'):
            for b in a.infraCPMtuPol:
                ROW1 = write_pyxl.write_hl(wsSystem, mtu_hl, ROW-1, 1)
                ROW = write_pyxl.write_line(wsSystem, b, mtu, ROW, 2)
        if hasattr(a, 'epIpAgingP'):
            for b in a.epIpAgingP:
                ROW1 = write_pyxl.write_hl(wsSystem, ipage_hl, ROW-1, 1)
                ROW = write_pyxl.write_line(wsSystem, b, ipage, ROW, 2)
    for a in Fabric:
        if hasattr(a, 'mgmtConnectivityPrefs'):
            for b in a.mgmtConnectivityPrefs:
                ROW1 = write_pyxl.write_hl(wsSystem, mgmt_hl, ROW - 1, 1)
                ROW = write_pyxl.write_line(wsSystem, b, mgmt, ROW, 2)
        if hasattr(a, 'datetimeFormat'):
            for b in a.datetimeFormat:
                ROW = write_pyxl.write_hl_category(wsSystem, ROW, COL, 'Timezone Settings', tz_hl)
                ROW = write_pyxl.write_line(wsSystem, b, tz, ROW, COL)
    ROW += 1
    ROW = write_pyxl.write_hl_category(wsSystem, ROW, COL, 'Fabric Wide Setting', fws_hl)
    for a in infraInfra: # Fabric Wide Settings
        for b in a.infraSetPol:
            ROW = write_pyxl.write_line(wsSystem, b, fws, ROW, COL)
    ROW = write_pyxl.write_hl_category(wsSystem, ROW, COL, 'BGP Route Reflector', bgp_hl)
    for a in Fabric:
        if hasattr(a, 'bgpInstPol'):
            for b in a.bgpInstPol:
                for c in b.bgpRRP:
                    if hasattr(c, 'bgpRRNodePEp'):
                        for d in c.bgpRRNodePEp:
                            ROW = write_pyxl.write_line(wsSystem, d, bgp, ROW, COL)
    #endregion
    ''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
    '''                        Write Admin Section                       '''
    ''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
    #region Write Admin Section
    ROW = ROW + 2
    #COL = 0
    wsAdmin = wsSystem # Merge System and Admin Tabs
    category = 'Admin Policies'
    ROW = write_pyxl.write_merge(wsAdmin, ROW, COL, ROW, len(provGrp_hl), category)
    ROW = write_pyxl.write_hl_category(wsAdmin, ROW, COL, 'AAA Provider Groups', provGrp_hl)

    for a in Auth:
        if hasattr(a, 'aaaRadiusEp'):
            for b in a.aaaRadiusEp:
                if hasattr(b, 'aaaRadiusProviderGroup'):
                    for c in b.aaaRadiusProviderGroup:  # aaaProviderRef
                        if hasattr(c, 'aaaProviderRef'):
                            for d in c.aaaProviderRef:
                                ROW = write_pyxl.write_line(wsAdmin, d, provGrp, ROW, COL)

        if hasattr(a, 'aaaTacacsPlusEp'):
            for b in a.aaaTacacsPlusEp:
                if hasattr(b, 'aaaTacacsPlusProviderGroup'):
                    for c in b.aaaTacacsPlusProviderGroup:  # aaaProviderRef
                        if hasattr(c, 'aaaProviderRef'):
                            for d in c.aaaProviderRef:
                                ROW = write_pyxl.write_line(wsAdmin, d, provGrp, ROW, COL)

    ROW = write_pyxl.write_hl_category(wsAdmin, ROW, COL, 'Authentication Providers', auth_hl)
    for a in Auth:
        if hasattr(a, 'aaaRadiusEp'):  # aaaRadiusProviderGroup aaaProviderRef
            for b in a.aaaRadiusEp:
                if hasattr(b, 'aaaRadiusProvider'):
                    for c in b.aaaRadiusProvider:
                        ROW = write_pyxl.write_line(wsAdmin, c, rad, ROW, COL)
        if hasattr(a, 'aaaTacacsPlusEp'):  # aaaRadiusProviderGroup aaaProviderRef
            for b in a.aaaTacacsPlusEp:
                if hasattr(b, 'aaaTacacsPlusProvider'):
                    for c in b.aaaTacacsPlusProvider:
                        ROW = write_pyxl.write_line(wsAdmin, c, tac, ROW, COL)

    if snmpDG:
        ROW = write_pyxl.write_hl_category(wsAdmin, ROW, COL, 'SNMP Destination Groups', snmpDG_hl)
        for a in snmpDG:
            ROW = write_pyxl.write_line(wsAdmin, a, snmpDG_key, ROW, COL)
    if syslogDG:
        ROW = write_pyxl.write_hl_category(wsAdmin, ROW, COL, 'SYSLOG Destination Groups', syslogDG_hl)
        for a in syslogDG:
            ROW = write_pyxl.write_line(wsAdmin, a, syslogDG_key, ROW, COL)
    #endregion
    ''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
    '''                        Faults Section                   '''
    ''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
    #region Write Faults
    ROW = 1
    COL = 1
    wsFaults = wb['Faults']
    ROW = write_pyxl.write_hl_category(wsFaults, ROW, COL, 'Faults', fault_hl)
    for a in Faults:
        ROW = write_pyxl.write_line(wsFaults, a, fault, ROW, COL)
    #endregion


    ''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
    '''                       Write Tenant Data                          '''
    ''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
    #region Write Tenant Data
    ROW = 1
    COL = 1
    l3node = ['pod', 'nodeId', 'rtrId', 'rtrIdLoopBack']
    l3node_hl = ['Pod', 'Node ID', 'Router ID', 'Loopback']
    ospfExtP_list = ['l3out', 'l3outdescr', 'name', 'descr', 'nameAlias', 'areaId', 'areaType', 'areaCost', 'areaCtrl']
    ospfExtP_list_hl = ['L3 Out', 'L3 Out Description', 'OSPF Policy', 'Description', 'Alias', 'Area ID', 'Area Type',
                        'Area Cost', 'Area Control']
    l3extpath_list = ['tenant', 'pod', 'nodeId', 'interface', 'addr', 'mtu', 'encap', 'ifInstT', 'mac', 'mode']
    l3extpath_list_hl = ['Tenant', 'Pod', 'Node ID', 'Interface', 'Address', 'MTU', 'Enacpsulation', 'Interface Type',
                         'MAC Addr', 'Interface Mode']
    for a in Tenant:
        # CAT_FORMAT = wb.add_format({'border': 2, 'bold': True, 'font_color': 'white', 'bg_color': 'green',
        #                             'align': 'center'})
        ROW = 1
        COL = 1
        category = 'Tenant ' + a.name
        ROW = write_pyxl.write_merge(wb[a.name], ROW, COL, ROW, len(BD_hl_namelist), category)
        tlist = ['fvTenant', 'name']
        ROW = write_pyxl.write_hl_category(wb[a.name], ROW, COL, 'VRFs', Tenant_hl_namelist)
        for b in a.fvCtx:
            ROW = write_pyxl.write_line(wb[a.name], b, tlist, ROW, COL)
        ROW = write_pyxl.write_hl_category(wb[a.name], ROW, COL, 'Bridge Domains', BD_hl_namelist)
        for b in a.fvBD:
            ROW = write_pyxl.write_line(wb[a.name], b, BD_hl_keylist, ROW, COL)
        #ROW = write_data.write_hl(Tenant_obj_list[a.name], EPG_hl_namelist, ROW, COL,)
        ROW = write_pyxl.write_hl_category(wb[a.name], ROW, COL, 'Endpoint Groups', EPG_hl_namelist)
        for b in a.fvAp: # Application profiles and EPGs
            if hasattr(b, 'fvAEPg'):
                for c in b.fvAEPg:
                    ROW = write_pyxl.write_line(wb[a.name], c, EPG_hl_keylist, ROW, COL)
        # ROW = write_data.write_hl(wb[a.name], CON_hl_namelist, ROW, COL,)
        ROW = write_pyxl.write_hl_category(wb[a.name], ROW, COL, 'Contracts', CON_hl_namelist)
        for b in a.vzBrCP: # Contracts
            if hasattr(b, 'vzSubj'):
                for c in b.vzSubj:
                    ROW = write_pyxl.write_line(wb[a.name], c, CON_hl_keylist, ROW, COL)
        # ROW = write_pyxl.write_hl(wb[a.name], FILTER_hl_namelist, ROW, COL,)
        ROW = write_pyxl.write_hl_category(wb[a.name], ROW, COL, 'Filters', FILTER_hl_namelist)
        for b in a.vzFilter: # Filters
            if hasattr(b, 'vzEntry'):
                for c in b.vzEntry:
                    ROW = write_pyxl.write_line(wb[a.name], c, FILTER_hl_keylist, ROW, COL)
        # EPG To Contract Mapping
        # ROW = write_pyxl.write_hl(wb[a.name], EC_namelist, ROW, COL)
        for b in a.fvAp: # EPG to Contract Mapping
            if hasattr(b, 'fvAEPg'):
                ROW = write_pyxl.write_hl_category(wb[a.name], ROW, COL, 'EPG to Contract Mapping', EC_namelist)
                break
        for b in a.fvAp: # EPG to Contract Mapping
            if hasattr(b, 'fvAEPg'):
                for c in b.fvAEPg:
                    if hasattr(c, 'fvRsProv'):
                        for d in c.fvRsProv:
                            setattr(c, 'prov', 'Yes')
                            setattr(c, 'cons', 'No')
                            tmp = d.tDn.split('ni/tn-')
                            tmp2 = tmp[1].split('/')
                            tn = tmp2[0]
                            contract = tn + '/' + d.tnVzBrCPName
                            setattr(c, 'contract', contract)
                            if hasattr(c, 'fvRsCons'):
                                test = False
                                for e in c.fvRsCons:
                                    if e.tDn == d.tDn:
                                        tmp = e.tDn.split('ni/tn-')
                                        tmp2 = tmp[1].split('/')
                                        tn = tmp2[0]
                                        contract = tn + '/' + d.tnVzBrCPName
                                        setattr(c, 'contract', contract)
                                        setattr(c, 'cons', 'Yes')
                                        test = True
                                        ROW = write_pyxl.write_line(wb[a.name], c, EC_keylist, ROW,
                                                                    COL)
                                        break
                                    else:
                                        tmp = e.tDn.split('ni/tn-')
                                        tmp2 = tmp[1].split('/')
                                        tn = tmp2[0]
                                        contract = tn + '/' + d.tnVzBrCPName
                                        setattr(c, 'contract', contract)
                                        setattr(c, 'cons', 'No')
                                if not test:
                                    ROW = write_pyxl.write_line(wb[a.name], c, EC_keylist, ROW,
                                                                COL)
                            else:
                                tmp = d.tDn.split('ni/tn-')
                                tmp2 = tmp[1].split('/')
                                tn = tmp2[0]
                                contract = tn + '/' + d.tnVzBrCPName
                                setattr(c, 'contract', contract)
                                setattr(c, 'prov', 'Yes')
                                setattr(c, 'cons', 'No')
                                ROW = write_pyxl.write_line(wb[a.name], c, EC_keylist, ROW, COL)
                    if hasattr(c, 'fvRsCons'):
                        for d in c.fvRsCons:
                            tmp = d.tDn.split('ni/tn-')
                            tmp2 = tmp[1].split('/')
                            tn = tmp2[0]
                            contract = tn + '/' + d.tnVzBrCPName
                            setattr(c, 'contract', contract)
                            setattr(c, 'cons', 'Yes')
                            setattr(c, 'prov', 'No')
                            if hasattr(c, 'fvRsProv'):
                                test = False
                                for e in c.fvRsProv:
                                    if e.tDn == d.tDn:
                                        tmp = e.tDn.split('ni/tn-')
                                        tmp2 = tmp[1].split('/')
                                        tn = tmp2[0]
                                        contract = tn + '/' + d.tnVzBrCPName
                                        setattr(c, 'contract', contract)
                                        setattr(c, 'cons', 'Yes')
                                        test = True
                                        break
                                    else:
                                        tmp = d.tDn.split('ni/tn-')
                                        tmp2 = tmp[1].split('/')
                                        tn = tmp2[0]
                                        contract = tn + '/' + d.tnVzBrCPName
                                        setattr(c, 'contract', contract)
                                        setattr(c, 'prov', 'No')
                                if not test:
                                    ROW = write_pyxl.write_line(wb[a.name], c, EC_keylist, ROW,
                                                                COL)
                            else:
                                tmp = d.tDn.split('ni/tn-')
                                tmp2 = tmp[1].split('/')
                                tn = tmp2[0]
                                contract = tn + '/' + d.tnVzBrCPName
                                setattr(c, 'contract', contract)
                                setattr(c, 'prov', 'No')
                                setattr(c, 'cons', 'Yes')
                                ROW = write_pyxl.write_line(wb[a.name], c, EC_keylist, ROW, COL)

        #region L3 Outs
        wsL3outs = wb[a.name]
        if hasattr(a, 'l3extOut'):  # l3extInstP
            for b in a.l3extOut:
                if hasattr(b, 'ospfExtP'):
                    ROW = write_pyxl.write_hl_category(wsL3outs, ROW, COL, 'OSPF Configuration', ospfExtP_list_hl)
                    break
        if hasattr(a, 'l3extOut'):  # l3extInstP
            for b in a.l3extOut:
                if hasattr(b, 'ospfExtP'):
                    for c in b.ospfExtP:
                        ROW = write_pyxl.write_line(wsL3outs, c, ospfExtP_list, ROW, COL)
        if hasattr(a, 'l3extOut'): # l3extInstP
            for b in a.l3extOut:
                if hasattr(b, 'l3extLNodeP'):
                    for c in b.l3extLNodeP:
                        if hasattr(c, 'l3extRsNodeL3OutAtt'):
                            ROW = write_pyxl.write_hl_category(wsL3outs, ROW, COL, 'Layer 3 Nodes', l3node_hl)
                            break
        if hasattr(a, 'l3extOut'): # l3extInstP
            for b in a.l3extOut:
                if hasattr(b, 'l3extLNodeP'):
                    for c in b.l3extLNodeP:
                        if hasattr(c, 'l3extRsNodeL3OutAtt'):
                            for d in c.l3extRsNodeL3OutAtt:
                                nodes = splitDn(d.tDn, [4,5])
                                setattr(d, 'pod', nodes[0])
                                setattr(d, 'nodeId', nodes[1])
                                ROW = write_pyxl.write_line(wsL3outs, d, l3node, ROW, COL)

        if hasattr(a, 'l3extOut'): # l3extInstP
            ROW = write_pyxl.write_hl_category(wsL3outs, ROW, COL, 'Layer 3 Out Interfaces', l3extpath_list_hl)
            for b in a.l3extOut:
                if hasattr(b, 'l3extLNodeP'):
                    for c in b.l3extLNodeP:
                        if hasattr(c, 'l3extLIfP'):
                            for d in c.l3extLIfP: # l3extRsPathL3OutAtt
                                if hasattr(d, 'l3extRsPathL3OutAtt'):
                                    for e in d.l3extRsPathL3OutAtt:
                                        ROW = write_pyxl.write_line(wsL3outs, e, l3extpath_list, ROW, COL)
        #endregion
        ROW_MAIN = ROW + 2
        COL = 1
        ROW_MAIN = write_pyxl.write_merge(wb[a.name], ROW_MAIN, COL, ROW_MAIN, len(static_hl), 'EPG Static Bindings')
        ROW_MAX = 1
        COL = 1
        COL2 = 5


        for b in a.fvAp:  # EPG to tp static Binding
            if hasattr(b, 'fvAEPg'):
                for c in b.fvAEPg: #fvRsPathAtt
                    if hasattr(c, 'fvRsPathAtt'):
                        ROW = ROW_MAIN
                        for d in c.fvRsPathAtt:
                            if hasattr(d, 'pod'): # write_merge(WS, startRow, startCol, endRow, endCol, text, merge_format):
                                ROW = write_pyxl.write_merge(wb[a.name], ROW_MAIN, COL, ROW_MAIN, COL2, c.name)
                                ROW = write_pyxl.write_hl(wb[a.name], static_hl, ROW, COL)
                                break
                        for d in c.fvRsPathAtt:
                            if hasattr(d, 'pod'):
                                ROW = write_pyxl.write_line(wb[a.name], d, static, ROW, COL)
                                if ROW >= ROW_MAX:
                                    ROW_MAX = ROW
                        for d in c.fvRsPathAtt:
                            if hasattr(d, 'pod'):
                                COL = COL2 + 1
                                COL2 = COL2 + 5
                                break

        ROW = ROW_MAX   # Set Row to the max Row list
        COL = 0

    # HL_FORMAT = wb.add_format({'border': 2, 'bold': True, 'font_color': 'white', 'bg_color': 'green'})
    # CAT_FORMAT = wb.add_format({'border': 2, 'bold': True, 'font_color': 'white', 'bg_color': 'green',
    #                             'align': 'center'})
    #endregion
    ''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
    '''                       Write L3OUT Data                          '''
    ''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
    #region Write L3out Data
    '''
    ROW = 0
    COL = 0
    ROW = write_pyxl.write_hl_category(wsL3outs, ROW, COL, 'A', 'D',
                                       'OSPF Configuration', ospfExtP_list_hl)
    for a in Tenant:
        if hasattr(a, 'l3extOut'): # l3extInstP
            for b in a.l3extOut:
                if hasattr(b, 'ospfExtP'):
                    for c in b.ospfExtP:
                        ROW = write_pyxl.write_line(wsL3outs, c, ospfExtP_list, ROW, COL)


    for a in Tenant:
        if hasattr(a, 'l3extOut'): # l3extInstP
            for b in a.l3extOut:
                if hasattr(b, 'l3extLNodeP'):

                    for c in b.l3extLNodeP:
                        # c.filterkids('l3extRsNodeL3OutAtt', 'l3extRsNodeL3OutAtt',['rtrId', 'rtrIdLoopBack', 'tDn'])
                        # c.filterkids('l3extLIfP', 'l3extLIfP', ['addr', 'name'])
                        if hasattr(c, 'l3extRsNodeL3OutAtt'):
                            ROW = write_pyxl.write_hl_category(wsL3outs, ROW, COL, 'A', 'D',
                                                               'Layer 3 Nodes', l3node_hl)
                            for d in c.l3extRsNodeL3OutAtt:
                                nodes = splitDn(d.tDn, [4,5])
                                setattr(d, 'pod', nodes[0])
                                setattr(d, 'nodeId', nodes[1])
                                ROW = write_pyxl.write_line(wsL3outs, d, l3node, ROW, COL)
                        if hasattr(c, 'l3extLIfP'):
                            for d in c.l3extLIfP: # l3extRsPathL3OutAtt
                                #d.filterkids('ospfRsIfPol', 'ospfRsIfPol', ['tnOspfIfPolName'])
                                #d.filterkids('l3extRsPathL3OutAtt', 'l3extRsPathL3OutAtt', l3extpath_list)
                                if hasattr(d, 'l3extRsPathL3OutAtt'):
                                    ROW = write_pyxl.write_hl_category(wsL3outs, ROW, COL, 'A', 'F',
                                                                       'Layer 3 Out Interfaces', l3extpath_list_hl,
                                                                       HL_FORMAT)
                                    for e in d.l3extRsPathL3OutAtt:
                                        ROW = write_pyxl.write_line(wsL3outs, e, l3extpath_list, ROW, COL)



    '''
    #endregion
    ''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
    '''                      Write Fabric Access Data                    '''
    ''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
    #region Write Fabric Access

    ROW = 2
    COL = 1
    category = 'Fabric Access'
    wsFabricAccess = wb['Fabric Access']
    ROW = write_pyxl.write_merge(wsFabricAccess, ROW, COL, ROW, len(podPol_hl), category)
    ROW = ROW + 1
    if podPol:
        ROW = write_pyxl.write_hl_category(wsFabricAccess, ROW, COL,'Pod Policies', podPol_hl,
                                           HL_FORMAT)
        for a in podPol:
            ROW = write_pyxl.write_line(wsFabricAccess, a, podPol_key, ROW, COL)

    ROW = write_pyxl.write_hl_category(wsFabricAccess, ROW, COL, 'DHCP Relay', dhcp_hl)
    for a in infraInfra: # Write DHCP Relay
        for b in a.dhcpRelayP:
            if hasattr(b, 'dhcpaddr'):
                ROW = write_pyxl.write_line(wsFabricAccess, b, dhcp, ROW, COL)
    for a in Tenant:
        if hasattr(a, 'dhcpRelayP'):
            for b in a.dhcpRelayP:
                if b.dhcpaddr != '':
                    ROW = write_pyxl.write_line(wsFabricAccess, b, dhcp, ROW, COL)
    for a in infraInfra: # Write VLAN Pools
        ROW = write_pyxl.write_hl_category(wsFabricAccess, ROW, COL, 'VLAN Pools', vlan_pool_hl)
        for b in a.fvnsVlanInstP:
            ROW = write_pyxl.write_line(wsFabricAccess, b, vlan_pool, ROW, COL)


    ROW = write_pyxl.write_hl_category(wsFabricAccess, ROW, COL, 'Domains', domains_hl)
    for a in Domain:
        if a.type == 'infraRsVlanNs':
            pass
        else:
            if a.type == 'infraRtDomP':
                pass
            else:
                ROW = write_pyxl.write_line(wsFabricAccess, a, domains, ROW, COL)
    #region Write AEP
    ROW = write_pyxl.write_hl_category(wsFabricAccess, ROW, COL, 'Attachable Entity Profiles (AEP)', aep_dom_hl)
    for a in AEP:
            ROW = write_pyxl.write_line(wsFabricAccess, a, aep_dom, ROW, COL)

    for a in AEP:
        if hasattr(a, 'infraGeneric'):
            aep_hl = 'AEP: ' + a.name
            ROW = write_pyxl.write_hl_category(wsFabricAccess, ROW, COL, aep_hl, aep_epg_hl)
            for b in a.infraGeneric:
                if hasattr(b, 'infraRsFuncToEpg'):
                    test = 'xyz'
                    for c in b.infraRsFuncToEpg:
                        # if c.aep == test:
                        if hasattr(c, 'epg'):
                            ROW = write_pyxl.write_line(wsFabricAccess, c, aep_epg, ROW, COL)
                        '''else:
                            test = c.aep
                            aep_hl = 'AEP: ' + c.aep
                            if hasattr(c, 'epg'):'''

                                #ROW = write_pyxl.write_line(wsFabricAccess, c, aep_epg, ROW, COL)
    #endregion
    #region Write Policy Groups
    ROW = write_pyxl.write_hl_category(wsFabricAccess, ROW, COL, 'Policy Groups', pg_hl)
    for a in PortGroup:
        ROW = write_pyxl.write_line(wsFabricAccess, a, pg, ROW, COL)
    for a in PCPortGroup:
        ROW = write_pyxl.write_line(wsFabricAccess, a, pg, ROW, COL)
    #endregion
    #region Interface Polcies
    for a in infraInfra:
        ROW = write_pyxl.write_hl_category(wsFabricAccess, ROW, COL, 'Interface Policies', link_hl)
        for b in a.fabricHIfPol:
            ROW = write_pyxl.write_line(wsFabricAccess, b, link, ROW, COL)
        ROW = write_pyxl.write_hl(wsFabricAccess, lacp_hl, ROW, COL)
        for b in a.lacpLagPol:
            ROW = write_pyxl.write_line(wsFabricAccess, b, lacp, ROW, COL)
        ROW = write_pyxl.write_hl(wsFabricAccess, cdp_hl, ROW, COL)
        for b in a.cdpIfPol:
            ROW = write_pyxl.write_line(wsFabricAccess, b, cdp, ROW, COL)
        ROW = write_pyxl.write_hl(wsFabricAccess, lldp_hl, ROW, COL)
        for b in a.lldpIfPol:
            ROW = write_pyxl.write_line(wsFabricAccess, b, lldp, ROW, COL)
        ROW = write_pyxl.write_hl(wsFabricAccess, mcp_hl, ROW, COL)
        for b in a.mcpIfPol:
            ROW = write_pyxl.write_line(wsFabricAccess, b, mcp, ROW, COL)
        ROW = write_pyxl.write_hl(wsFabricAccess, stp_hl, ROW, COL)
        for b in a.stpIfPol:
            ROW = write_pyxl.write_line(wsFabricAccess, b, stp, ROW, COL)
        ROW = write_pyxl.write_hl(wsFabricAccess, L2interface_hl, ROW, COL)
        for b in a.l2IfPol:
            ROW = write_pyxl.write_line(wsFabricAccess, b, L2interface, ROW, COL)
    #endregion
    #endregion


    #region End Script
    ROW = 1
    COL = 1
    SW_ROW = 2
    # fabric_switches.sort(key=itemgetter('nodeId'))  # Create list of sorted switches
    '''for i in sorted_sw:
        WS = wb.add_worksheet(fabric_switches[i].name)
        pprint('Switch name: ' + fabric_switches[i].name)
        pprint('int Profile: ' + fabric_switches[i].intProfile)
        worksheet_list.append(WS)
        ROW_END = write_pyxl.write_portmap(WS, fabric_switches[i], ROW, COL, cell_format)
        SW_ROW = write_pyxl.write_line(ws1, fabric_switches[i], switch_hl_keylist, SW_ROW, COL)'''

    '''wb.worksheets_objs.sort(key=lambda x: x.name)'''


    print('Closing Excel File')
    wb.save(excel_file)
    wb.close()
    pprint(script_name + ': ' + version + ' --- Complete')
    AnyKey = input("Press Enter")
    #endregion


''' Call Main Function'''
__main__()