### Pulls ACI data together to create Tables for output
### Data processing?
import write.writexlsx.write2excel as w2x
from pprint import pprint

#region Build Portmap (Ethernet and Logical)
badFill = 'FFC7CE'
badFont = '9C0006'
goodFill = 'C6EFCE'
goodFont = '006100'
neutralFill = 'FFEB9C'
neutralFont = '9C5700'
normalFill = 'FFFFFF'
normalFont = '000000'

portTests = [{'data': 'connected', 'fill': goodFill, 'font': goodFont},
             {'data': 'notconnect', 'fill': neutralFill, 'font': neutralFont},
             {'data': 'suspnd', 'fill': badFill, 'font': badFont},
             {'data': 'noOperMem', 'fill': badFill, 'font': badFont},
             {'data': 'down', 'fill': badFill, 'font': badFont},
             {'data': 'errDisable', 'fill': badFill, 'font': badFont},]
portstatus = [{'key': 'state', 'test': portTests}]
#endregion


def hwlist(filename, device_list): ### Build hw list and create excel doc
    wb = w2x.build_workbook(filename, TAB='HW List')
    aciTable = w2x.buildtable(device_list, 'ACI Fabric')
    aciTable.setworksheet(wb.active)
    aciTable.writetable()
    return wb

def aciTable(ws, obj, attr, hl):
    table = ''
    try:
        newobj = getattr(obj, attr)
        table = w2x.buildtable(newobj, hl)
        table.setworksheet(ws)
    except:
        print(f'Failed to build table ({hl}) in Tenant {a.name}')
    return table

def orderTable(priorTable, Table):
    try:
        row = priorTable.row + len(priorTable.rowobject)
        Table.row = row
    except:
        print('Failed for Order Table')



def tenantTabs(wb, tenantList):
    for a in tenantList:
        newtab = w2x.addTab(wb, a.name)
        # Build Tables for Tenant Tab
        bdTable = aciTable(newtab, a, 'bd', 'Bridge Domains')
        epgTable = aciTable(newtab, a, 'epg', 'End-point Groups')
        contractTable = aciTable(newtab, a, 'contract', 'Contracts')

        # Order Tables
        epgTable.orderTable(bdTable)
        contractTable.orderTable(epgTable)

        # Write Tables
        bdTable.writetable()
        epgTable.writetable()
        contractTable.writetable()

def aciBuildExcel(filename, fabricObj):
    newHW = []
    pprint('Building Excel')
    pprint(vars(fabricObj))
    for a in fabricObj.hwlist:
        newHW = newHW + a
    WB = hwlist(filename, newHW)
    # tenantTabs(WB, fabricObj.tenants)


    WB.save(filename)
