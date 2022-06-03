from pprint import pprint
from cisco.aci.audit.aci_pullConfig import getACIdata
from cisco.aci.audit.aci_device import aciBuildDevice
import cisco.aci.audit.aciAudit as aci






def __main__():
    version = 'ver2.0'
    script_name = 'Configuration Generator'
    pprint('Running ' + script_name + ' Version: ' + version)
    test = True
    upload = False
    offline = 'no'
    aci_dict = getACIdata(test)
    aciFabric = aciBuildDevice(aci_dict)
    print('\nPrint Tests')
    aci.aciBuildExcel('test0020.xlsx', aciFabric)
    #APIC = name_pwd['APIC']
    #excel_file = name_pwd['filename'] + '.xlsx'
    podList = [1,2]
    podDictList = []
    worksheetNames = ['HW Overview', 'System', 'Fabric Access', 'Faults']

__main__()