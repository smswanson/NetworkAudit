from output.writexlsx.write_pyxl_nxos import mkXLSX, Headline, write_hl_category, write_obj, write, mkFont, setalignment, write_merge, setfontcolor, setfill, mkPattern
import output.writexlsx.write_pyxl_nxos as wr

from pprint import pprint
deviceHeadline = Headline()
deviceHeadline.keydict = {'name': 'Hostname',
                          'serial': 'S/N',
                          'version': 'Version',
                          'chassis': 'Chassis'}
deviceHeadline.namelist = ['Hostname', 'S/N', 'Version', 'Chassis']
keydict = [{'name': {'data': 'host_name', 'hl': 'Hostname'}},
           {'serial': {'data': 'proc_board_id', 'hl': 'S/N'}},
           {'version': {'data': 'kickstart_ver_str', 'hl': 'Version'}},
           {'chassis': {'data': 'chassis_id', 'hl': 'Chassis'}},
           {'uptime': {'data': 'uptime', 'hl': 'Uptime'}}]



def item2list(item):
    if type(item) is list:
        itemlist = item
    else:
        itemlist = [item]
    return itemlist


def getkeys(dict):
    list = []
    for a in dict.keys():
        list.append(a)
    return list


class RowObject:
    def __init__(self, device, key):
        if key == 'hl':
            # try:
            self.header = True
            for a in device.keylist:
                k = getkeys(a)
                if len(k) == 1:
                    setattr(self, k[0], a[k[0]][key])
            # except:
            #    print('Failed to create Headers Row Object')
        else:
            try:
                for a in device.keylist:
                    k = getkeys(a)
                    if len(k) == 1:
                        if hasattr(device, k[0]):
                            attr = getattr(device, k[0])
                            setattr(self, k[0], attr)
                        else:
                            setattr(self, k[0], '')
            except:
                print('Failed to create data Row Object')

    def setdata(self, key, data):
        try:
            setattr(self, key, data)
        except:
            print(f'Failed to set Data for key: {key}')


class Table:
    # Table object to be printed to excel
    def __init__(self):
        self.headline = ''
        self.keys = []
        self.row = 1
        self.col = 1
        self.endcol = 1
        self.endrow = 1
        self.rowobject = []
        self.hl = False
        self.hltest = []

    def setkeys(self, keylist):
        self.keys = keylist

    def setheadline(self, hl):
        self.headline = hl

    def setrowcol(self, row, col):
        self.row = row
        self.col = col

    def setendcol(self):
        self.endcol = self.col + len(self.keys)

    def writeheadline(self):
        # Uses worksheet function "merge_cells". Need to redo...
        try:
            newrow = write_merge(self.ws, self.row, self.col, self.row, self.endcol, self.headline)
            setalignment(self.ws, self.row, self.col)
            setfontcolor(self.ws, self.row, self.col, COLOR='FFFFFF')
            setfill(self.ws, self.row, self.col, COLOR='0081E2')
            self.setrowcol(newrow, self.col)
        except:
            print(f'Failed to write Headline: {self.headline}')

    def addrow(self, rowobject):
        try:
            self.rowobject.append(rowobject)
        except:
            print('Failed to add Row Object')

    def setworksheet(self, WS):
        try:
            setattr(self, 'ws', WS)
        except:
            print('Failed to set Worksheet')

    def sortrows(self, key):
        pass

    def writerow(self, rowobject, highlight=False):
        col = self.col
        for a in self.keys:
            b = a.keys()
            write(self.ws, self.row, col, a)
            col = col + 1
        self.setrowcol(self.row + 1, self.col)

    def highlight(self, col, testkey, testdata):
        for a in self.hltest:
            key = a['key']
            if testkey == key:
                for b in a['test']:
                    if b['data'] == testdata:
                        setfill(self.ws, self.row, col, b['fill'])
                        setfontcolor(self.ws, self.row, col, b['font'])
                    else:
                        pass


    def writeallrows(self):
        for a in self.rowobject:
            col = self.col
            for b in self.keys:
                bkey = b.keys()
                for d in bkey:
                    e = d
                if hasattr(a, e):
                    c = getattr(a, e)
                else:
                    c = ''
                write(self.ws, self.row, col, c)
                if self.hl:
                    self.highlight(col, d, c)


                try:
                    if a.header:
                        setfill(self.ws, self.row, col, COLOR='33CCFF')
                except:
                    pass
                col = col + 1
            self.setrowcol(self.row + 1, self.col)

    def writetable(self):
        print(f'Building Table: {self.headline}')

        self.writeheadline()
        self.writeallrows()

        #print(f'Failed to build Table: {self.headline}')



def build_workbook(filename, TAB='HW List'):
    wb = wr.mkXLSX(filename, TAB)
    return wb


def addTab(WB, tab):
    ws = wr.addSheet(WB, tab)
    return ws

def getKeys(dict):
    list = []
    for a in dict.keys():
        list.append(a)
    return list


def parseKeys(dict, key):
    list = []
    for a in dict:
        try:
            b = getKeys(a)
            c = b[0]
            item = a[c][key]
            list.append(item)
        except:
            print(f'Not able to parse Dictionary: {b[0]}')
    return list


def writeDevice(devices):
    ROW = 0
    COL = 1
    # Process Device
    device.newattr('show_version', keydict)
    hl = parseKeys(keydict, 'hl')
    data = parseKeys(keydict, 'data')
    filename = device.name + '-' + device.serial + '.xlsx'
    TAB = 'System'
    wb = mkXLSX(filename, TAB)
    system = wb.active
    nxosTable = buildtable(device_list, 'Nexus Switches')
    nxosTable.setworksheet(system)
    nxosTable.writeallrows()
    # ROW = write_hl_category(system, ROW, COL, 'System', hl)
    # ROW = write_obj(system, [device], data, ROW, COL)
    wb.save(filename)


def writePortMap(device):
    pass


def buildtable(devices, headline):
    newTable = Table()
    newTable.setkeys(devices[0].keylist)
    newTable.setheadline(headline)
    newTable.setendcol()
    list = [RowObject(devices[0], 'hl')]
    for a in devices:
        rowdevice = RowObject(a, 'data')
        list.append(rowdevice)
    newTable.rowobject = list
    return newTable


def write_sheet(WB, WS, tables):
    # Tables is list of lists. enables parallel tables.
    tab = wr.addSheet(WB, WS)
    for a in tables:
        for b in a:
            writetable(b, tab)

def old_writetable(table, file, hl=False, TEST=[]):
    filename = file
    TAB = 'System'
    wb = mkXLSX(filename, TAB)
    system = wb.active
    # table = buildtable(device_list, 'Nexus Switches')
    table.setworksheet(system)
    table.writeheadline()
    table.writeallrows(hl=hl, tests=TEST)
    wb.save(filename)

def writetable(table):
    # table = buildtable(device_list, 'Nexus Switches')
    table.writeheadline()
    table.writeallrows()


def setautofitcol(worksheet):
    i = 1
    for col in worksheet.columns:
        max_length = 0
        column = col[0].column  # Get the column name
        column_letter = wr.getcolletter(i)
        for cell in col:
            if cell.coordinate in worksheet.merged_cells:  # not check merge_cells
                continue
            try:  # Necessary to avoid error on empty cells
                if len(str(cell.value)) > max_length:
                    max_length = len(cell.value)
            except:
                pass
        adjusted_width = (max_length + 1) * 1.1

        worksheet.column_dimensions[column_letter].width = adjusted_width
        i = i + 1