import json
from arista.eos.audit.device import BuildDevice
import pprint
import os

def write_json(json_data, name='json-output.json'):
    filename = name
    try:
        print(f'\nWriting JSON File: {filename}')
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(json_data, f, ensure_ascii=False, indent=4)
    except:
        print(f'\nError Writing {filename}\n')

def cli_cmd_json(session, COMMAND, delay=0):
    print(f'Getting {COMMAND}')
    json_out = {}
    try:
        json_out = json.loads(session.send_command(COMMAND, delay_factor=delay))
    except:
        print(f'FAILED- {COMMAND}---FAILED')
    return json_out

def cli_cmd(session, COMMAND, delay=0):
    print(f'Getting {COMMAND}')
    txt_out = ''
    try:
        txt_out = session.send_command(COMMAND, delay_factor=delay)
    except:
        print(f'FAILED- {COMMAND}---FAILED')
    return txt_out
    #Start Collections

def show_collection(session):
    show = {}
    show['show_version'] = cli_cmd_json(session, 'show version | json', delay=2)
    show['show_hostname'] = cli_cmd_json(session, 'show hostname | json', delay=2)
    show['show_int'] = cli_cmd_json(session, 'show interfaces | json', delay=2)
    show['show_int_status'] = cli_cmd_json(session, 'show interface status | json', delay=2)
    show['show_ip_int'] = cli_cmd_json(session, 'show ip interface | json', delay=2)
    show['show_ip_varp'] = cli_cmd_json(session, 'show ip virtual-router vrf all | json', delay=2)
    show['show_vrf_interface'] = cli_cmd_json(session, 'show vrf interface | json', delay=2)
    show['show_ip_route'] = cli_cmd_json(session, 'show ip route vrf all | json', delay=2)
    show['show_lldp_nei'] = cli_cmd_json(session, 'show lldp neighbor | json', delay=2)
    show['show_mac_address_table'] = cli_cmd_json(session, 'show mac address-table | json', delay=2)
    show['show_vlan'] = cli_cmd_json(session, 'show vlan | json', delay=2)
    show['show_vrf'] = cli_cmd_json(session, 'show vrf | json', delay=2)
    show['show_vrf_interface'] = cli_cmd_json(session, 'show vrf interface | json', delay=2)
    show['show_interface_transceiver'] = cli_cmd_json(session, 'show interface transceiver | json', delay=2)
    show['show_spanningtree'] = cli_cmd_json(session, 'show spanning-tree | json', delay=2)
    show['show_ip_bgp_summary'] = cli_cmd_json(session, 'show ip bgp summary vrf all | json', delay=2)
    device = BuildDevice(show)
    return show

def getBackup(session, directory, filename):
    show_run = cli_cmd(session, 'show running-config', delay=5)
    if not os.path.isdir(directory):
        os.mkdir(directory)
    file_path = os.path.join(directory, filename)
    try:
        print(f'\nWriting Backup File: {filename}')
        with open(file_path, 'w') as outfile:
            for line in show_run:
                outfile.write(line)
    except:
        print(f'\nError Writing {filename}\n')
    return show_run

def writeEOSjson(json, directory, offline=False):
    name = json['show_hostname']['hostname']
    print('\nGetting ' + name + ' Data')
    logfile = name + '_raw.json'
    if not os.path.isdir(directory):
        os.mkdir(directory)
    file_path = os.path.join(directory, logfile)
    write_json(json, file_path)
    if offline:
        try:
            with open(logfile) as json_file:
                data_dict = json.load(json_file)
                pprint('JSON Data Loaded for ' + logfile)
                json_file.close()
        except:
            pprint('Failed to Open: ' + logfile)
def process_json(sw_json):
    pass

def getConfiglet():
    pass

