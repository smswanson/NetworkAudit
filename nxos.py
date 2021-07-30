from datetime import date
from cisco.nxos.audit.pullConfig import show_collection, getBackup
from cisco.nxos.audit import nxosAudit as nx
from login import login
import json
# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.


def print_setup(time='0000'):
    # Use a breakpoint in the code line below to debug your script.
    version = '0.1'
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

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    timestamp = str(date.today())
    test_mode = print_setup(timestamp)
    ssh_list = login.create_session(test_mode)
    device_list = []
    for s in ssh_list:
        ssh = s['session']
        ip = s['device']
        device = show_collection(ssh)
        backup_file = device.name + '-' + device.serial + '-' + timestamp + '.txt'
        running_cfg = getBackup(ssh, backup_file)
        print(f'Disconnecting SSH Session to {ip}')
        ssh.disconnect()
        device_list.append(device)
    filename = 'test0001.xlsx'
    if device_list == []:
        print('No Devices Accessed. Exiting...')
    else:
        nx.portmap('lab-portmap.xlsx', device_list)


