'''
Необходимо:
1. Собрать со всех устройств файлы конфигураций, сохранить их на диск, используя
имя устройства и текущую дату в составе имени файла.
2. Проверить на всех коммутаторах - включен ли протокол CDP и есть ли у процесса
CDP на каждом из устройств данные о соседях.
3. Проверить, какой тип программного обеспечения (NPE или PE)* используется на
устройствах и собрать со всех устройств данные о версии используемого ПО.
4. Настроить на всех устройствах timezone GMT+0, получение данных для
синхронизации времени от источника во внутренней сети, предварительно проверив
его доступность.
5. Вывести отчет в виде нескольких строк, каждая из которых имеет следующий
формат, близкий к такому:
Имя устройства - тип устройства - версия ПО - NPE/PE - CDP on/off, X peers - NTP in
sync/not sync. 
'''
import netmiko
import jinja2
import textfsm
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
import yaml
from netmiko import ConnectHandler
import netmiko
from pprint import pprint
import logging
import os
import sys
from NetmikoConnectionsHandler import NetmikoConnectionsHandler
import re
from ping import ping

with open('devices.yaml') as f:
    devices = yaml.safe_load(f)

def convert_output_to_list(output):
    #returns  [('hostname', '192.168.0.81', 'command', 'output'), ('192.168.0.81', 'output'),...]    
    result = []
    for ip in output.keys():
        for all_outputs_for_ip in output[ip][1:]:
            for output_for_command in all_outputs_for_ip:
                if output_for_command['command_is_ok']:
                    temp = (output_for_command['hostname'], ip, output_for_command['command'], output_for_command['output'])
                    result.append(temp)

    return result

def save_configs_to_files():
    outputs_dict = nch.send_show_commands('sh run')
    outputs_list = convert_output_to_list(outputs_dict)
    #pprint(outputs_list)

    for output in outputs_list:
        hostname, ip, command, command_output = output
        filename = './/configs//' + hostname + ' ' + datetime.now().strftime('%d-%m-%Y %H-%M-%S') + '.txt'
        with open(filename, 'w') as f:
            f.write(command_output)
        summary[hostname] = []

def get_cdp_info():
    outputs_dict = nch.send_show_commands('sh cdp nei')
    outputs_list = convert_output_to_list(outputs_dict)
    for output in outputs_list:
        hostname, ip, command, command_output = output
        if 'CDP is not enabled' in command_output:
            summary[hostname].append('CDP is OFF')
        else:
            m=re.search(r'Total cdp entries displayed : (\d+)', command_output)
            summary[hostname].append(f'CDP is ON, {m[1]} peers')

def get_ios_info():
    outputs_dict = nch.send_show_commands('sh ver')
    outputs_list = convert_output_to_list(outputs_dict)
    for output in outputs_list:
        hostname, ip, command, command_output = output
        m=re.search(r'Version (\S+),', command_output)
        version = m[1]
        if 'NPE' in version:
            encryption = 'NPE'
        else: 
            encryption = 'PE'
        summary[hostname].append(f"{version} |{encryption}")

def set_ntp(ntp_server):
    bad_ntp = ''
    if ping(ntp_server):    
        nch.send_config_commands(f'ntp server {ntp_server}')
    else:
        print('ping failed')
        bad_ntp += 'Bad NTP Server, '
    outputs_dict = nch.send_show_commands('sh ntp status')
    outputs_list = convert_output_to_list(outputs_dict)
    #pprint(outputs_dict)
    for output in outputs_list:
        hostname, ip, command, command_output = output
        if 'Clock is unsynchronized' in command_output:
            result = bad_ntp + 'Clock not in Sync'
        elif 'Clock is synchronized' in command_output:
            result = bad_ntp + 'Clock in Sync'
        summary[hostname].append(result)
    
    
    #pprint(outputs_list)
        
   

nch = NetmikoConnectionsHandler(devices, workers=6)
nch.open_connections()

summary = {}
save_configs_to_files()
get_ios_info()
get_cdp_info()
set_ntp('192.168.0.81')

nch.close_connections()

#ms-gw-01|ISR4451/K9|BLD_V154_3_S_XE313_THROTTLE_LATEST |PE|CDP is ON,5peers|Clock in Sync 
#ms-gw-02|ISR4451/K9|BLD_V154_3_S_XE313_THROTTLE_LATEST |NPE|CDP is ON,0 peers|Clock in Sync
for i in summary.items():
    line = '#' + i[0] + '|'
    for j in i[1]:
        line += j + '|'
    print(line)





