from netmiko import ConnectHandler
import time
import datetime
# import re
import getpass
from pprint import pprint
import os
#192.168.1.10 is the ip address

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




def get_login(test=False):
    login_info = {}
    try:
        if test:
            IP_str = '192.168.10.102,192.168.10.101,192.168.10.201'
            #IP_str = '10.253.254.125,10.253.254.126'
            USER = 'admin'
            PW = 'VMwar3!!'
            #PW = 'R0undt0w3r!'
            print(f'Running test credentials: {USER}/{PW}')
        else:
            IP_str = input(" Enter List of Switch IPs (comma separated) : ")
            USER = input(" Enter Username : ")
            pprint('getting password')
            PW= getpass.getpass(" Password : ")

        IP_list = [x.strip() for x in IP_str.split(',')]
        login_info = {'ip': '',
                      'ip_list': IP_list,
                      'username': USER,
                      'password': PW,
                      'port': 22,
                      'device_type': 'cisco_ios',
                      }
        return login_info
    except:
        pprint("Username and password collection had errors")

def nx_ssh(login_dict):
    connect = ConnectHandler(**login_dict)
    return connect


def create_session(test=False):
    pprint('Getting Credentials')
    creds = get_login(test)
    user = creds['username']
    session = []
    ip_list = creds['ip_list']
    del creds['ip_list']
    for ip in ip_list:
        creds['ip'] = ip
        if test_ip(creds['ip']):
            try:
                print(f'Logging in to {ip} as {user}')
                tmp_session = nx_ssh(creds)
                session.append({'device': ip, 'session': tmp_session})
            except:
                print(f'Failed Login for {ip}....Skipping')

    return session


'''def nx_napalm(ip, user='admin', pw='password'):
    driver = get_network_driver('nxos_ssh')
    optional_args = {'port': 22}
    device = driver(hostname=ip, username=user, password=pw, optional_args=optional_args)
    return device'''


'''def nx_ssh(ip, user='admin', pw='password'):
    try:
        date_time = datetime.datetime.now().strftime("%Y-%m-%d")
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(ip, port=22, username=user, password=pw, look_for_keys=False, timeout=None)
        connection = ssh.invoke_shell()
        connection.send("terminal length 0\n")
        time.sleep(5)
        connection.send("\n")
        connection.send('show interface status\n')
        pprint('command sent')
        file_output2 = connection.recv(9999).decode(encoding='ascii')
        pprint(file_output2)
        return ssh
        print("Switch is connected")

    except paramiko.AuthenticationException:
        print("User or password incorrect, Please try again!!!")
'''
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