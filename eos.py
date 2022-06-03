from datetime import date
from arista.eos.audit.pullConfig import show_collection, getBackup, writeEOSjson
from arista.eos.audit import eosAudit
from login import login
import json
# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.


def print_setup(time='0000'):
    # Use a breakpoint in the code line below to debug your script.
    version = '0.1'
    script_name = 'EOS-Audit'
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
    filename = login.get_output_filname(test=test_mode) + '.xlsx'
    ssh_list = login.create_session(type='eos', test=test_mode)
    device_list = []
    for s in ssh_list:
        ssh = s['session']
        ip = s['device']
        json = show_collection(ssh)
        device = eosAudit.process_json(json)
        backup_file = device.name + '-' + device.serial + '-' + timestamp + '.txt'
        running_cfg = getBackup(ssh, 'output/', backup_file)
        print(f'Disconnecting SSH Session to {ip}')
        ssh.disconnect()
        device_list.append(device)
    if device_list == []:
        print('No Devices Accessed. Exiting...')
    else:
        eosAudit.portmap(filename, device_list)



