import json
import xmltodict
from pprint import pprint
''' Custom script for Gulfstream to convert xml output from nexus switches to json for audit'''
switch = 'techcomp-core-1'
path = 'project/' + switch + '/'
writepath = 'project/nxos_json/'
outputfile = writepath + switch + '.json'


def convertToJson(xml_doc):

    outjson = {}
    with open(path + xml_doc) as xml_file:
        data_dict = xmltodict.parse(xml_file.read())
        xml_file.close()
        json_data = json.dumps(data_dict)
        json_file = xml_doc.split('.')
        outfile = path + 'json/' + json_file[0] + '.json'
        with open(outfile, "w") as json_file:
            json_file.write(json_data)
            json_file.close()
        with open(outfile, "r") as dict_file:
            dict = json.load(dict_file)
            data = dict['nf:rpc-reply']["nf:data"]
            if 'cdp' in xml_doc:
                cdp_data = data['show']['cdp']['neighbors']['__XML__OPT_Cmd_show_cdp_neighbors_interface'][
                    '__XML__OPT_Cmd_show_cdp_neighbors___readonly__']['__readonly__']
                outjson.update({'show_cdp_nei': cdp_data})
            if 'version' in xml_doc:
                ver_data = data['show']['version']['__XML__OPT_Cmd_sysmgr_show_version___readonly__']['__readonly__']
                outjson.update({'show_version': ver_data})
            if 'hostname' in xml_doc:
                host_data = data['show']['__XML__BLK_Cmd_SHOW_HOSTNAME_hostname']['__XML__OPT_Cmd_SHOW_HOSTNAME___readonly__']['__readonly__']
                outjson.update({'show_hostname': host_data})
            if 'interface_status' in xml_doc:
                stat_data = data['show']['interface']['status']['__XML__OPT_Cmd_show_interface_status_down'][
                    '__XML__OPT_Cmd_show_interface_status___readonly__']['__readonly__']
                outjson.update({'show_int_status': stat_data})
            if 'ip_interface_vrf' in xml_doc:
                ipint_data = data['show']['ip']['interface']['__XML__BLK_Cmd_ip_show_interface_command_brief'][
                    '__XML__OPT_Cmd_ip_show_interface_command_operational'][
                    '__XML__OPT_Cmd_ip_show_interface_command_vrf'][
                    '__XML__OPT_Cmd_ip_show_interface_command___readonly__']['__readonly__']
                outjson.update({'show_ip_int': ipint_data})
            if 'spanning' in xml_doc:
                spanning_data = data['show']['spanning-tree']['__XML__OPT_Cmd_show_stp_vlan_vlan'][
                    '__XML__OPT_Cmd_show_stp_vlan___readonly__'][
                    '__readonly__']
                outjson.update({'show_spanningtree': spanning_data})
            if 'vlan' in xml_doc:
                vlan_data = data['show']['vlan']['__XML__OPT_Cmd_show_vlan___readonly__']['__readonly__']
                outjson.update({'show_vlan': vlan_data})
            if 'vlan' in xml_doc:
                vlan_data = data['show']['vlan']['__XML__OPT_Cmd_show_vlan___readonly__']['__readonly__']
                outjson.update({'show_vlan': vlan_data})
            if 'vrf_interface' in xml_doc:
                vrfint_data = data['show']['vrf']['__XML__OPT_Cmd_l3vm_show_vrf_cmd_vrf-name']['interface'][
                    '__XML__OPT_Cmd_l3vm_show_if_cmd_interface']['__XML__OPT_Cmd_l3vm_show_if_cmd___readonly__'][
                    '__readonly__']
                outjson.update({'show_vrf_interface': vrfint_data})
            if '_' not in xml_doc and 'vrf' in xml_doc:
                vrf_data = data['show']['vrf']['__XML__OPT_Cmd_l3vm_show_vrf_cmd_vrf-name'][
                    '__XML__OPT_Cmd_l3vm_show_vrf_cmd_detail']['__XML__OPT_Cmd_l3vm_show_vrf_cmd___readonly__'][
                        '__readonly__']
                outjson.update({'show_vrf': vrf_data})
    return outjson


def getCollectionXml(folder):
    list = []
    '''try:'''
    directory = folder
    for file in os.listdir(directory):
        convertToJson(file)


def getCollectionJson(project):
    list = []
    '''try:'''
    directory = project + '/nxos_json'
    for file in os.listdir(directory):
        filepath = os.path.join(directory, file)
        jsonData = openJson(filepath)
        device = nxosBuildDevice(jsonData)
        list.append(device)
    '''except:
        pprint('Failed to Open Folder: ' + project)'''
    return list

if __name__ == '__main__':
    list = ['cdp_neighbours.txt', 'hostname.txt', 'interface_status.txt', 'ip_interface_vrf.txt',
            'ip_route_vrf.txt', 'spanning_tree.txt', 'version.txt',
            'vlan.txt', 'vrf.txt', 'vrf_interface.txt']
    outjson = {}
    for a in list:
        print(a)
        out = convertToJson(a)
        outjson.update(out)
    with open(outputfile, 'w', encoding='utf-8') as f:
        print(f'\nWriting JSON File: {outputfile}')
        json.dump(outjson, f, ensure_ascii=False, indent=4)