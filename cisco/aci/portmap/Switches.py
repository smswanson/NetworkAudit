import ACI_PortMap
import write.writexlsx.write_data as write_data
import time
import requests
import json
import copy
import inspect
import getpass
from pprint import pprint
from operator import itemgetter
import xlsxwriter
from colorama import Fore, Back, Style
def __main__():
    version = 'ver0.3'
    pprint('Running Portmap Generator Version: ' + version)
    test = True
    if test:
        APIC = '192.168.10.1'
        #APIC = '10.200.250.11'
        USER = 'admin'
        PW = 'R0undt0w3r!'
        excel_file_name = 'test999'
    else:
        APIC = input(" Enter APIC IP : ")
        USER = input(" Enter Username : ")
        PW= getpass.getpass(" Password : ")
        excel_file_name = input("Input filename w/o .xlsx : ")
    excel_file = excel_file_name + '.xlsx'
    podList = [1]

    name_pwd = {"aaaUser": {"attributes": {"name": USER, "pwd": PW}}}
    aci_data = ACI_PortMap.AciJsonCollect(uname_pwd=name_pwd, apic=APIC)
    hl = ACI_PortMap.Headline()
    # Collect Switch data
    aci_data.get_aci_fabric_json()
    aci_data.get_aci_infra_json()
    # pprint(aci_data.infranode)
    #TEST = ACI_PortMap.LeafIntProfile()
    #TEST.get_profiles(aci_data.infraport)
    # Process fabric switch Data

    leaf_profiles = ACI_PortMap.add_profiles(aci_data)
    pprint(leaf_profiles)
    fabric_switches = ACI_PortMap.add_switches(aci_data)
    pprint('switchs: \n')
    pprint(fabric_switches)
    fabric_switches.pop('', None)
    sorted_sw = sorted(fabric_switches.keys())
    for s in sorted_sw:
        fabric_switches[s].set_headline(hl.keylist, hl.namelist)
        interface_json = aci_data.get_aci_interfaces_json(fabric_switches[s])
        cdp_json = aci_data.get_aci_cdp_json(fabric_switches[s])
        lldp_json = aci_data.get_aci_lldp_json(fabric_switches[s])
        fabric_switches[s].add_interfaces(interface_json, cdp_json, lldp_json, aci_data.infraport)
        fabric_switches[s].add_intselectors(leaf_profiles)
        pprint('Finished: ' + fabric_switches[s].name)
        time.sleep(3)


    pprint('Creating Excel File: '+ excel_file)
    wb = xlsxwriter.Workbook(excel_file)

    HL_FORMAT = wb.add_format({'border': 2,'bold': True, 'font_color': 'white','bg_color': 'green'})
    D_FORMAT = wb.add_format({'border': 1,'bold': True, 'font_color': 'black','bg_color': 'white'})
    UP_FORMAT = wb.add_format({'bold': True, 'font_color': 'black','bg_color': 'white'})

    switch_hl_keylist = ['name', 'nodeId', 'podId', 'id', 'nodeRole', 'model', 'runningVer']
    switch_hl_namelist = ['Name', 'Node ID', 'Pod', 'ID', 'Role', 'Model', 'Version']

    cell_format = [HL_FORMAT, D_FORMAT]
    ws1 = wb.add_worksheet('HW Overview')
    write_data.write_hl(ws1, switch_hl_namelist, 0, 1, HL_FORMAT)
    worksheet_list = [ws1]
    pprint(worksheet_list)
    ROW = 1
    COL = 1
    SW_ROW = 2
    # fabric_switches.sort(key=itemgetter('nodeId'))  # Create list of sorted switches
    for i in sorted_sw:
        WS = wb.add_worksheet(fabric_switches[i].name)
        pprint('Switch name: ' + fabric_switches[i].name)
        pprint('int Profile: ' + fabric_switches[i].intProfile)
        worksheet_list.append(WS)
        ROW_END = write_data.write_portmap(WS, fabric_switches[i], ROW, COL,cell_format)
        SW_ROW = write_data.write_line(ws1, fabric_switches[i], switch_hl_keylist, SW_ROW, COL, D_FORMAT)

    wb.worksheets_objs.sort(key=lambda x: x.name)
    print('Closing Excel File')
    wb.close()
    pprint('Portmap Generator Version: ' + version + '--- Complete')
    AnyKey = input("Press Enter")









__main__()