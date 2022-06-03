from datetime import date
from arista.eos.audit.pullConfig import show_collection, getBackup, writeEOSjson
from arista.eos.audit import cvaasAudit, eosAudit
from login import login
import os
from pprint import pprint
import json

#CVaaS Login
token = 'eyJhbGciOiJFUzI1NiIsInR5cCI6IkpXVCJ9.eyJkaWQiOjM5MjM1LCJkc24iOiJhaGVhZF9zdmMiLCJkc3QiOiJhY2NvdW50IiwiZXhwIjoxNjU5MjA2MDY1LCJpYXQiOjE2NTQxOTQ4NzMsInNpZCI6IjllMjZkNDNkMTVmZDU0MzU3NTNmMmUzZjExZjBiZTNhYTBlNjVjYzBiMzY3OTA4MTI3ZTljNDM5ZjcwYTg3MDctNG41SFE1X1RzUGlsRVlaZXpBaUlhX3RVZ3pzMHduMU9qT3FuUC1KcCJ9.X8h4zRdwL75OB2XG9J_kKtIe3IdfLVnp6h1y11MZ0Dho9CWjU4tSAQgfrRMQN23Sq9IjofzINVMo_2ljeOP3Lg'
cvaas = 'www.arista.io'

def setup(time='0000'):
    # Use a breakpoint in the code line below to debug your script.
    version = '0.1'
    script_name = 'CVP-Audit'
    #Set "True" if script is in testing mode
    test = True
    print(f'Running: {script_name}\nVersion: {version}')
    print(f'Date: {time}')
    if test:
        print('\nRunning in Test Mode\n')
    return test

def mkOutputDirectory(directory):
    if not os.path.isdir(directory):
        os.mkdir(directory)
    if not os.path.isdir(directory + 'CVP-Configlets'):
        os.mkdir(directory+ 'CVP-Configlets')
    if not os.path.isdir(directory + 'CVP-Backups'):
        os.mkdir(directory + 'CVP-Backups')
    if not os.path.isdir(directory + 'Running-Cfg-Backups'):
        os.mkdir(directory + 'Running-Cfg-Backups')



def write_output(device, filetype='json'):
    datafile = device.name + '-' + device.serial + '.' + filetype
    print(f'Write Raw Data to {datafile} for {device.name}')
    try:
        with open(datafile, 'w') as outfile:
            json.dump(device.data, outfile)
    except:
        print(f'Error Writing {datafile}')

def eos(ssh_list, directory, filename):
    device_list = []
    for s in ssh_list:
        ssh = s['session']
        ip = s['device']
        json = show_collection(ssh)
        writeEOSjson(json, directory + 'EOS-raw-json')
        device = eosAudit.process_json(json)
        backup_file = device.name +'-'+ device.serial +'-'+ timestamp + '.txt'
        running_cfg = getBackup(ssh, directory + 'Running-Cfg-Backups', backup_file)
        print(f'Disconnecting SSH Session to {ip}')
        ssh.disconnect()
        setattr(device, 'mgmtip', ip)
        device_list.append(device)
    if device_list == []:
        print('No Devices Accessed. Exiting...')
    else:
        eosAudit.portmap(directory + filename, device_list)


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    vpn_connected = True
    test_ip = False
    timestamp = str(date.today())
    test_mode = setup(timestamp)
    project = 'GALIC'
    outputDirectory = project + '/'
    mkOutputDirectory(outputDirectory)
    filename = project + '-cvpAudit_' + timestamp + '.xlsx'
    cvpData = cvaasAudit.getCvpData(cvaas, token)
    cvaasAudit.cvpAudit(outputDirectory, filename, cvpData)
    ####filename_pm = login.get_output_filname(test=test_mode) + '.xlsx'
    filename_pm = project + '-portmap_' + timestamp + '.xlsx'
    swList = []
    if test_ip:
        swList = ['10.90.64.11','10.90.64.12']
    else:
        for a in cvpData['inventory']:
            swList.append(a.ipAddress)


    #Create Sessions directly to switches for Portmap generation
    if vpn_connected:
        pingSwList = []
        for a in swList:
            test = login.test_ip(a)
            if test:
                pingSwList.append(a)
            else:
                pass


        ssh_list = login.create_session(type='eos', test=test_mode, ips=pingSwList)
        eos(ssh_list, outputDirectory, filename_pm)
    else:
        print('VPN not connected. Skipping Switch Port-maps')

    '''filename = login.get_output_filname(test=test_mode) + '.xlsx'
    ssh_list = login.create_session(type='eos', test=test_mode)
    device_list = []'''
    '''for s in ssh_list:
        ssh = s['session']
        ip = s['device']
        json = show_collection(ssh)
        device = eosAudit.process_json(json)
        backup_file = device.name + '-' + device.serial + '-' + timestamp + '.txt'
        running_cfg = getBackup(ssh, backup_file)
        print(f'Disconnecting SSH Session to {ip}')
        ssh.disconnect()
        device_list.append(device)
    if device_list == []:
        print('No Devices Accessed. Exiting...')
    else:
        eosAudit.portmap(filename, device_list)'''