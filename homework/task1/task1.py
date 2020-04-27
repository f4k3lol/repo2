'''
1. Собрать со всех устройств файлы конфигураций, сохранить их на диск, используя
имя устройства и текущую дату в составе имени файла.

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

def send_show_command(device, command):    
    logging.basicConfig(
        format='%(threadName)s %(name)s %(levelname)s: %(message)s',
        level=logging.INFO)
        
    logging.info('connection to device ' + device['ip'])
    
    try:
        with ConnectHandler(**device) as ssh:
            ssh.enable()
            host = ssh.find_prompt()
            result = ssh.send_command(command) + '\n'
            #print(result)
            return [host[:-1]] + [result]
    except (netmiko.ssh_exception.NetMikoAuthenticationException, 
     netmiko.ssh_exception.NetMikoTimeoutException) as e:
        print('Error!: ', e)        

def send_show_command_to_devices(devices, command, limit=6):
    executor = ThreadPoolExecutor(max_workers=limit)
    results = list(executor.map(send_show_command, devices, [command]*len(devices)))
    pprint(results)
    return results

def get_configs_from_devices(devs):
    cfgs = send_show_command_to_devices(devs, 'sh run')
    for cfg in cfgs:
        filename = './configs/{} {}.txt'.format(cfg[0], str(datetime.now().strftime('%d-%m-%y %H-%M-%S')))
        with open(filename, 'w') as f:
            f.write(cfg[1].replace('Building configuration...',''))

with open('../devices.yaml') as f:
    devices = yaml.safe_load(f)
get_configs_from_devices(devices)

