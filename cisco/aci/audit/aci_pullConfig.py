from login.login import create_aci_session
import os
import datetime
import requests
upload = False ### future use
import json
from pprint import pprint
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
'''################### URLs for desire data/JSON #################################'''
# region APIC URLs
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
fabric_url = '/api/node/mo/uni/fabric.json?rsp-subtree=full'
protpol_url = '/api/node/mo/uni/fabric/protpol.json?query-target=children&rsp-subtree=full'
aep_url = '/api/node/class/infraAttEntityP.json?rsp-subtree=full'
faults_url = '/api/node/class/faultSummary.json?query-target=subtree'
# endregion

def getACIjson(session, APIC, data, data_url, log=True, offline=False):
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

def getACIdata(test):
    aci_data = {}
    upload = False
    podList = ['1', '2', '3']
    podDictList = []
    session = create_aci_session(type='aci', test=test)
    APIC = session['creds']['APIC']
    creds = {}
    creds['aaaUser'] = session['creds']['aaaUser']
    pprint(session)
    filename = session['creds']['filename']
    with requests.Session() as s:
        if not upload:
            p = s.post('https://' + APIC + '/api/aaaLogin.json', json=creds, verify=False)
        else:
            pass
        # print the html returned or something more intelligent to see if it's a successful login page.
        pprint(p.text)

        vrf_dict = getACIjson(s, APIC, 'portgroup', multicast_url, offline=upload)
        #pprint('Multicast Dict')
        #pprint(vrf_dict)
        portgroup_dict = getACIjson(s, APIC, 'portgroup', portgroup_url, offline=upload)
        pcportgroup_dict = getACIjson(s, APIC, 'pcportgroup', pcportgroup_url, offline=upload)
        infra_dict = getACIjson(s, APIC, 'infra', infra_url, offline=upload)
        tenant_dict = getACIjson(s, APIC, 'tenant', tenant_url, offline=upload)
        fabric_dict = getACIjson(s, APIC, 'fabric', fabric_url, offline=upload)
        fabric_dict_raw = getACIjson(s, APIC, 'fabric_node', fabric_node_url, offline=upload)
        domain_dict = getACIjson(s, APIC, 'domain', domain_url, offline=upload)
        protpol_dict = getACIjson(s, APIC, 'protpol', protpol_url, offline=upload)
        aep_dict = getACIjson(s, APIC, 'aep', aep_url, offline=upload)
        ethpmPhysIf_dict = getACIjson(s, APIC, 'ethpmPhysIf', ethpmPhysIf_url, offline=upload)
        for a in podList:
            b = str(a)
            podnum = 'pod-' + b
            try:
                pod_dict = getACIjson(s, APIC, podnum, '/api/node/mo/topology/' + podnum +'.json?query-target=children', offline=upload)
                podDictList.append(pod_dict)
            except:
                pprint(podnum + ' Not Found')

        controller_dict = getACIjson(s, APIC, 'controller', controller_url, offline=upload)
        auth_dict = getACIjson(s, APIC, 'auth', auth_url, offline=upload)
        faults_dict = getACIjson(s, APIC, 'faults', faults_url, offline=upload)
        dlist = {'imdata': []}
    aci_data = {'filename': filename,
                'vrf_dict': vrf_dict,
                'portgroup_dict': portgroup_dict,
                'pcportgroup_dict': pcportgroup_dict,
                'infra_dict': infra_dict,
                'tenant_dict': tenant_dict,
                'fabric_dict': fabric_dict,
                'fabric_dict_raw': fabric_dict_raw,
                'domain_dict': domain_dict,
                'protpol_dict': protpol_dict,
                'aep_dict': aep_dict,
                'ethpmPhysIf_dict': ethpmPhysIf_dict,
                'podDictList': podDictList,
                'controller_dict': controller_dict,
                'auth_dict': auth_dict,
                'faults_dict': faults_dict,
                'dlist': dlist, }
    return aci_data