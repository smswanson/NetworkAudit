from datetime import date
from cisco.nxos.audit.pullConfig import show_collection, getBackup, writeNXOSjson, getCollectionJson
from cisco.nxos.audit import nxosAudit as nx
from login import login
from pprint import pprint
import json
import os
# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.


def print_setup(time='0000'):
    # Use a breakpoint in the code line below to debug your script.
    version = '1.1'
    script_name = 'NXOS-Audit'
    #Set "True" if script is in testing mode
    test = True
    print(f'Running: {script_name}\nVersion: {version}')
    print(f'Date: {time}')
    if test:
        print('\nRunning in Test Mode\n')
    return test


def write_output(device, filetype='json'):
    datafile = device.name + '-' + device.serial + '.' + filetype
    print(f'Write Raw Data to {datafile} for {device.name}')
    try:
        with open(datafile, 'w') as outfile:
            json.dump(device.data, outfile)
    except:
        print(f'Error Writing {datafile}')

def appendDirectory(directory, file):
    if not os.path.isdir(directory):
        os.mkdir(directory)
    filename = os.path.join(directory, file)
    return filename
# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    timestamp = str(date.today())
    test_mode = print_setup(timestamp)
    creds = login.getNxosCredentials(test_mode)
    file = creds['filename'] + '.xlsx'
    project = creds['project']
    directory = project
    nxos_dir = directory + '/' + 'nxos_json'
    if not os.path.isdir(directory):
        os.mkdir(directory)
    filename = os.path.join(directory, file)
    if not os.path.isdir(nxos_dir):
        os.mkdir(nxos_dir)
    #ssh_list = login.create_session(type='nxos', test=test_mode)
    device_list = []
    if creds['offline']:
        device_list = getCollectionJson(project)
    else:
        ip_list = creds['ip_list']
        pprint(ip_list)
        del creds['ip_list']   # Cleanup Dictionary for login
        del creds['filename']  # Cleanup Dictionary for login
        del creds['project']   # Cleanup Dictionary for login
        del creds['offline']  # Cleanup Dictionary for login
        for ip in ip_list:
            session = login.getNxosSession(ip, creds)
            device = show_collection(session)
            backup_file = device.name + '-' + device.serial + '-' + timestamp + '.txt'
            backup_file = appendDirectory(project + '/backups', backup_file)
            running_cfg = getBackup(session, backup_file)
            writeNXOSjson(device.data, project + '/nxos_json')
            print(f'Disconnecting SSH Session to {ip}')
            session.disconnect()
            device_list.append(device)

    if device_list == []:
        print('No Devices Accessed. Exiting...')
    else:
        nx.portmap(filename, device_list)


