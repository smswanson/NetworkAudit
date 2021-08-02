import xlsxwriter
from colorama import Fore, Back, Style
from pprint import pprint

def write_hl(WS, NAMELIST, ROW, COL, FORMAT): # Input Switch Object
    COL1 = COL
    ROW1 = ROW
    # WS.write(ROW1, COL1, OBJ.name, FORMAT)
    ROW1 = ROW1 + 1

    for h in NAMELIST:
        WS.write(ROW1, COL1, h, FORMAT)
        COL1 = COL1 + 1
    return ROW1 + 1


def write_obj(WS, OBJ, keylist, ROW, COL, FORMAT): # Input Interface Object for OBJ and Switch Object for HL
    COL1 = COL
    ROW1 = ROW
    for a in keylist:
        try:
            b = getattr(OBJ, a)
            WS.write(ROW1, COL1, b, FORMAT)
        except:
            print(a + ' Does not exist in ' + OBJ.name)
        finally:
            COL1 = COL1 + 1
    return ROW1 + 1

def write_portmap(WS, OBJ, ROW, COL, FORMAT): # Input Switch Object
    COL1 = COL
    ROW1 = ROW
    ROW1 = write_hl(WS, OBJ.namelist, ROW1, COL1, FORMAT[0])  # Write Headline
    for i in OBJ.interfaces:
        o = getattr(OBJ, i)
        ROW1 = write_obj(WS, o, OBJ.keylist, ROW1, COL1, FORMAT[1])
    return ROW1 + 1


def write_line(WS, OBJ, KEYLIST, ROW, COL, FORMAT):
    COL1 = COL
    ROW1 = ROW
    for i in KEYLIST:
        b = getattr(OBJ, i)
        WS.write(ROW1, COL1, b, FORMAT)
        COL1 = COL1 + 1
    return ROW1 + 1