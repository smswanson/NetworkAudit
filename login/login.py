from netmiko import ConnectHandler
from cvprac.cvp_client import CvpClient
import time
import datetime
import requests
from urllib3.exceptions import InsecureRequestWarning
import getpass
from pprint import pprint
import os
import csv
#192.168.1.10 is the ip address
''' login.py is used for all '''
api_token = 'eyJhbGciOiJFUzI1NiIsInR5cCI6IkpXVCJ9.eyJkaWQiOjM5MjM1LCJkc24iOiJhaGVhZF9zdmMiLCJkc3QiOiJhY2NvdW50IiwiZXhwIjoxNjQzMzkzNzAwLCJpYXQiOjE2NDA3MTUzMzUsInNpZCI6ImI2YjMwOWNjN2U5OTYzNmExODQzNWMzNmEzZWI5OTkxZjUxZTRkOTE0OGI2M2ZjODA5MDc5OTZkNjczNzdmYjUtTDhNOXRPQXpjcWY4MlhWc1huVjdBbUVYaWhuS2xuWjB2MFZscGh4eiJ9.wPy4qV7s4_rr6uKSOGPYzGCBCPxbSxUlVi3uHWF75V6t0EeYsS4EK3OKC5H6IpTNaU-4YhQkR__XzSw2YRVHRQ'
requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)


def test_ip(ip):
    ping = "ping " + ip + " -w 2000 -n 1"
    ret = os.system(ping)
    if ret == 0:
        print(f'Device: {ip} is responding to pings')
        available = True
    else:
        print(f'Device: {ip} is NOT responding to pings')
        available = False
    return available

def getOffline():
    offlineTest = True
    while offlineTest:
        offline = input(" Is this offline (Yes/No): ")
        offline.lower()
        if offline == 'yes' or offline == 'y':
            upload = True
            offlineTest = False
        elif offline == 'no' or offline == 'n':
            offlineTest = False
            upload = False
        else:
            pprint('Please Enter Yes for No')
    return upload

def get_output_filname(test=True):
    if test:
        filename = 'test-output'
    else:
        filename = input("Output filename w/o .xlsx : ")
    return filename

def getNxosCredentials(test=False):
    login_info = {}
    IP_list = []
    USER = ''
    # PW = 'VMwar3!!'
    PW = ''
    # try:
    if test:
        IP_str = '10.200.250.71,10.200.250.72'

        USER = 'admin'
        PW = 'R0undt0w3r1!'
        excel_file_name = 'ARH-Nexus-3548'
        project = 'ARH'
        offline = False
        IP_test = [x.strip() for x in IP_str.split(',')]
        print(f'Running test credentials: {USER}/{PW}')
    else:
        project = input(" Enter the desired output directory : ")
        excel_file_name = input("Enter filename w/out .xlsx : ")
        offline = getOffline()
        if offline:
            print(f'Loading files from folder: {project}')
        else:
            IP_str = input(" Enter List of Nexus Switch IPs (comma separated) : ")
            USER = input(" Enter Username : ")
            PW = getpass.getpass(" Enter Password : ")
            IP_test = [x.strip() for x in IP_str.split(',')]
    if not offline:
        for a in IP_test:
            if test_ip(a):
                IP_list.append(a)
    login_info = {'ip': '',
                  'ip_list': IP_list,
                  'username': USER,
                  'password': PW,
                  'port': 22,
                  'device_type': 'cisco_ios',
                  "filename": excel_file_name,
                  "project": project,
                  "offline": offline
                  }
    return login_info

def get_login(type, test=False):  # 'type' should be aci, nxos, or eos
    login_info = {}
    IP_list = []
    # try:
    if type == 'nxos':
        if test:
            IP_str = '10.1.1.15,10.1.1.17,10.1.1.18,10.1.1.19,10.1.1.20'
            #,10.4.1.3,10.4.1.12,10.4.1.13,10.4.1.15,10.4.1.17'
            #IP_str = '10.1.1.11,10.1.1.12,10.1.1.13,10.1.1.14,10.1.1.15,10.1.1.16,10.1.1.17,10.1.1.18,10.1.1.19,10.1.1.20,'
            USER = 'v-sswanson'
            #PW = 'VMwar3!!'
            PW = 'H7m&1asGH7!!'
            excel_file_name = 'nxos-Test'
            print(f'Running test credentials: {USER}/{PW}')
        else:
            IP_str = input(" Enter List of Switch IPs (comma separated) : ")
            USER = input(" Enter Username : ")
            pprint('getting password')
            PW= getpass.getpass(" Password : ")
            excel_file_name = input("Input filename w/o .xlsx : ")
        IP_test = [x.strip() for x in IP_str.split(',')]
        for a in IP_test:
            if test_ip(a):
                IP_list.append(a)
        login_info = {'ip': '',
                      'ip_list': IP_list,
                      'username': USER,
                      'password': PW,
                      'port': 22,
                      'device_type': 'cisco_ios',
                      "filename": excel_file_name
                      }
    elif type == 'eos':
        if test:
            IP_str = '10.90.64.3, 10.90.64.31, 10.90.64.11'
            list = []
            with open('./login/galic_ips.csv', 'r') as csv_file:
                pprint('Opening CSV')
                csvreader = csv.reader(csv_file)
                for row in csvreader:
                    list.append(str(row[0]))
            #IP_str = ','.join(list)
            IP_str = '10.90.64.11,10.90.64.12'
            USER = 'ahead'
            PW = 'Ahead123!'
            # PW = 'R0undt0w3r!'
            # excel_file_name = 'eos-test'
            print(f'Running test credentials: {USER}/{PW}')
        else:
            IP_str = input(" Enter List of Switch IPs (comma separated) : ")
            USER = input(" Enter Username : ")
            pprint('getting password')
            PW= getpass.getpass(" Password : ")
            # excel_file_name = input("Input filename w/o .xlsx : ")
        IP_test = [x.strip() for x in IP_str.split(',')]
        for a in IP_test:
            if test_ip(a):
                IP_list.append(a)
        login_info = {'ip': '',
                      'ip_list': IP_list,
                      'username': USER,
                      'password': PW,
                      'port': 22,
                      'device_type': 'arista_eos',
                      }
    elif type == 'eoscvaas':
        if test:
            IP_str = '10.90.64.3, 10.90.64.31, 10.90.64.11'
            list = []
            '''with open('./login/galic_ips.csv', 'r') as csv_file:
                pprint('Opening CSV')
                csvreader = csv.reader(csv_file)
                for row in csvreader:
                    list.append(str(row[0]))'''
            #IP_str = ','.join(list)
            # IP_str = '10.253.254.125,10.253.254.126'
            USER = 'ahead'
            PW = 'Ahead123!'
            # PW = 'R0undt0w3r!'
            # excel_file_name = 'eos-test'
            print(f'Running test credentials: {USER}/{PW}')
        else:
            IP_str = input(" Enter List of Switch IPs (comma separated) : ")
            USER = input(" Enter Username : ")
            pprint('getting password')
            PW= getpass.getpass(" Password : ")
            # excel_file_name = input("Input filename w/o .xlsx : ")
        IP_test = [x.strip() for x in IP_str.split(',')]
        for a in IP_test:
            if test_ip(a):
                IP_list.append(a)
        login_info = {'ip': '',
                      'ip_list': IP_list,
                      'username': USER,
                      'password': PW,
                      'port': 22,
                      'device_type': 'arista_eos',
                      }
    elif type == 'aci':
        if test:
            APIC = '192.168.10.1'
            APIC = '10.200.250.11'
            # IP_str = '10.253.254.125,10.253.254.126'
            USER = 'admin'
            # PW = 'VMwar3!!'
            PW = 'R0undt0w3r!'
            USER = 'roundtower'
            # PW = 'VMwar3!!'
            #PW = "JC2y'EtzGN~dCu{b"
            # excel_file_name = 'aci-test'
            print(f'Running test credentials: {USER}/{PW}')
        else:
            APIC = input(" Enter IP Address of APIC: ")
            USER = input(" Enter Username : ")
            pprint('getting password')
            PW = getpass.getpass(" Password : ")
            # excel_file_name = input("Input filename w/o .xlsx : ")
        if test_ip(APIC):
            login_info = {"filename": excel_file_name,
                          "APIC": APIC,
                          "aaaUser": {"attributes": {"name": USER, "pwd": PW}}}
        else:
            print(f'APIC: {APIC} is not accessable')
    else:
        print(f'Device type ({typelower}) incorrect.')
    return login_info
    #except:
    #    pprint("Username and password collection had errors")

def sw_ssh(login_dict):
    connect = ConnectHandler(**login_dict)
    time.sleep(2)
    return connect

def getNxosSession(ip, creds):
    '''if test_ip(ip):'''
    try:
        creds['ip'] = ip
        print(f'Logging in to {ip} as {creds["username"]}')
        tmp_session = sw_ssh(creds)
        #session = {'device': ip, 'session': tmp_session}
        session = tmp_session
    except:
        print(f'Failed Login for {ip}....Skipping')
        session = {}
    return session
    '''else:
        print(f'{ip} is not pinging....SKIPPING')'''

def create_session(type='nxos', test=False, ips=[]):
    pprint('Getting Credentials')
    creds = get_login(type=type, test=test)
    user = creds['username']
    session = []
    if ips == []:
        ip_list = creds['ip_list']
    else:
        ip_list = ips
    del creds['ip_list']
    for ip in ip_list:
        creds['ip'] = ip
        time.sleep(5)
        if test_ip(creds['ip']):
            try:
                print(f'Logging in to {ip} as {user}')
                tmp_session = sw_ssh(creds)
                session.append({'device': ip, 'session': tmp_session})
            except:
                print(f'Failed Login for {ip}....Skipping')

    return session

def create_aci_session(type='aci', test=True):
    pprint('Getting Credentials')
    upload = False
    creds = get_login(type=type, test=test)
    aci_session = {}
    aci_session['creds'] = creds
    return aci_session


def show_cli(connection, show_text):
    if show_text.startswith('show'):
        command = show_text
    else:
        command = 'show ' + show_text
    try:
        connection.send("\n")
        connection.send(command)
        pprint('command sent')
        file_output2 = connection.recv(9999).decode(encoding='ascii')
        connection.send("\n")
        time.sleep(3)
        file_output = connection.recv(999999).decode(encoding='ascii')
        return file_output
    except:
        pprint('Sending CLI command: ' + command + '---Failed')

def file_output(file_output):
    print(file_output)
    outFile = open(hostname + "-" + str(date_time) + ".txt", "w")
    outFile = open("test" + ".txt", "w")
    outFile.writelines(file_output)

    outFile.close()

def writeFile(filename, data):
    date = datetime.date.today()
    outFile = open(filename + '-' + str(date) + ".txt", "w")
    outFile.write(data)
    outFile.close()

def cvaasLogin(cvaas, token):
    clnt = CvpClient()
    clnt.connect(nodes=[cvaas], username='', password='', is_cvaas=True, api_token=token)
    return clnt