import json
from cisco.nxos.audit.device import nxosBuildDevice
import pprint


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
    show['show_feature'] = cli_cmd_json(session, 'show feature | json', delay=2)
    show['show_int_status'] = cli_cmd_json(session, 'show interface status | json', delay=2)
    show['show_ip_int'] = cli_cmd_json(session, 'show ip interface vrf all | json', delay=2)
    show['show_vrf_interface'] = cli_cmd_json(session, 'show vrf interface | json', delay=2)
    show['show_ip_route'] = cli_cmd_json(session, 'show ip route vrf all | json', delay=2)
    show['show_cdp_nei'] = cli_cmd_json(session, 'show cdp neighbor | json', delay=2)
    show['show_lldp_nei'] = cli_cmd_json(session, 'show lldp neighbor | json', delay=2)
    show['show_mac_address_table'] = cli_cmd_json(session, 'show mac address-table | json', delay=2)
    show['show_vlan'] = cli_cmd_json(session, 'show vlan | json', delay=2)
    show['show_vrf'] = cli_cmd_json(session, 'show vrf | json', delay=2)
    show['show_vrf_interface'] = cli_cmd_json(session, 'show vrf interface | json', delay=2)
    show['show_spanningtree'] = cli_cmd_json(session, 'show spanning-tree | json', delay=2)
    show['show_bgp_all_summary'] = cli_cmd_json(session, 'show bgp all summary | json', delay=2)
    device = nxosBuildDevice(show)
    return device

def getBackup(session, filename):
    show_run = cli_cmd(session, 'show running-config', delay=5)
    try:
        print(f'\nWriting Backup File: {filename}')
        with open(filename, 'w') as outfile:
            for line in show_run:
                outfile.write(line)
    except:
        print(f'\nError Writing {filename}\n')
    return show_run

def process_json(sw_json):
    pass