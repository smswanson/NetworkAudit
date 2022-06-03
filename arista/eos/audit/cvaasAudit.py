import write.writexlsx.write2excel as w2x
from pprint import pprint
from login.login import cvaasLogin
from arista.eos.audit.cvaasDevice import BuildDevice, cvContainerList, cvConfigletList
import re
import os
from datetime import date
from arista.eos.audit.pullConfig import show_collection, getBackup, writeEOSjson
from arista.eos.audit import eosAudit
from login import login
import json

# CloudVision Analytics Engine Sysdb path to Interface Configuration.
PATH_INTF_CONFIG = 'Sysdb/interface/config/eth/phy/slice/1/intfConfig'

#region Build Portmap (Ethernet and Logical)
badFill = 'FFC7CE'
badFont = '9C0006'
goodFill = 'C6EFCE'
goodFont = '006100'
neutralFill = 'FFEB9C'
neutralFont = '9C5700'
normalFill = 'FFFFFF'
normalFont = '000000'
def atof(text):
    try:
        retval = float(text)
    except ValueError:
        retval = text
    return retval

def natural_keys(someobject): # example someobject.vlanid
    '''
    alist.sort(key=natural_keys) sorts in human order
    http://nedbatchelder.com/blog/200712/human_sorting.html
    float regex comes from https://stackoverflow.com/a/12643073/190597
    '''
    return [ atof(c) for c in re.split('(\d+)', someobject.name) ]
def cvpWrite(tab, deviceList, headline):
    table = w2x.buildtable(deviceList, headline)
    table.setworksheet(tab)
    table.writetable()
    w2x.setautofitcol(tab)

def cvpAudit(directory, file, data):   # Write Spreadsheet...
    containerList = data['containers']
    configletList = data['configlets']
    inventory = data['inventory']
    filename = directory + file
    #region Build HW List Tab
    wb = w2x.build_workbook(filename, TAB='HW List')
    w2x.writeTab(wb.active, inventory, 'EOS Switches')
    #endregion
    #region Build Provisioning Tab
    tab = w2x.addTab(wb, 'Provisioning')
    w2x.writeTab(tab, containerList, 'Containers')
    w2x.writeTab(tab, configletList, 'Configlets')
    #endregion

    wb.save(filename) # Save the workbook

    for a in configletList:
        writeBackup(directory + 'CVP-Configlets', a, 'cfg')
    for a in data['inventory']:
        writeBackup(directory + 'CVP-Backups', a, 'cfg')


def mkHwList(device_json): # Build devices in list form from json
    device_list = []
    for a in device_json:
        device = BuildDevice(a)
        device_list.append(device)
    device_list.sort(key=natural_keys)
    return device_list


def wrHwList(filename, device_list): # Build Table Object and write to excell
    wb = w2x.build_workbook(filename, TAB='HW List')
    cvTable = w2x.buildtable(device_list, 'EOS Switches')
    cvTable.setworksheet(wb.active)
    cvTable.writetable()
    return wb


def getCvpData(cvaas, token):
    client = cvaasLogin(cvaas, token)
    inventory = client.api.get_inventory()
    containers = client.api.get_containers()
    configlets = client.api.get_configlets()
    # Build objects
    device_list = mkHwList(inventory)
    containerList = cvContainerList(containers['data'])
    configletList = cvConfigletList(configlets['data'])
    # process additional data
    for a in device_list:
        a.getConfigletsAppied(client)
        a.getRunningConfig(client)
    data = {'inventory': device_list,
            'containers': containerList,
            'configlets': configletList}
    return data

def writeBackup(directory, object, filetype='txt'):
    datafile = directory + '/' + object.name + '.' + filetype
    if not os.path.isdir(directory):
        os.mkdir(directory)
    print(f'Write Cfg Backup to {datafile} for {object.name}')
    data = object.config.split('\r')
    try:
        with open(datafile, 'w') as outfile:
            outfile.writelines(data)
    except:
        print(f'Error Writing {datafile}')


def write_raw_output(device, filetype='json'):
    datafile = device.name + '-' + device.serial + '.' + filetype
    print(f'Write Raw Data to {datafile} for {device.name}')
    try:
        with open(datafile, 'w') as outfile:
            json.dump(device.data, outfile)
    except:
        print(f'Error Writing {datafile}')


'''def get_interface_list(client, switch):
    return self.clnt.get('/user/getUser.do?userId={}'.format(username),
                         timeout=self.request_timeout)'''


def cvpWrite(json):
    pass