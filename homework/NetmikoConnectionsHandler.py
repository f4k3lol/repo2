


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
import netmiko
import time
from netmiko.cisco.cisco_ios import CiscoIosBase

def log(message):
    logging.basicConfig(
        format='%(threadName)s %(name)s %(levelname)s: %(message)s',
        level=logging.INFO)
    logging.info(message)

class NetmikoConnection(CiscoIosBase):
    def __init__(self, **device_params):       
        super().__init__(**device_params)
        log('inited ' + self.host)
        
    def send_command(self, command, **kwargs):   
        result = super().send_command(command, **kwargs)        
        return result

    def send_show_commands(self, commands):
        results = []
        for cmd in commands:
            results.append(self.send_command(cmd))
        return results

    def send_config_set(self, commands):
        return super().send_config_set(commands)

            
class NetmikoConnectionHandler:
    def __init__(self, devices, workers=6):
        self.devices = devices
        self.workers = workers
        self.connections = []

    def _open_connection(self, device):
        try:
            log("opening connection")
            ssh = NetmikoConnection(**device)            
            return device['ip'], ssh           
        except (netmiko.ssh_exception.NetMikoAuthenticationException, 
            netmiko.ssh_exception.NetMikoTimeoutException) as e:
            msg = 'Error!: ' + str(e)
            log(msg)
            return device['ip'], msg
    
    def open_connections(self):        
        executor = ThreadPoolExecutor(max_workers=self.workers)
        self.connections = list(executor.map(self._open_connection, self.devices))
        #pprint(self.connections)

    def send_command_to_devices(self, command):
        '''con[0] device_ip, con[1] - connection
        RETURNS:
        - - 192.168.0.81
            - connection_is_ok = True
            command = 'sh cloack'
            command_is_ok = False
            output = 'error'
            - command = 'sh clock'
            command_is_ok = True
            output = 'error'
        - 192.168.0.81: False
        '''
        result = {}
        for con in self.connections:
            con_dict = {}
            if type(con[1]) != str: #connection is ok                
                con_dict['connection_is_ok'] = True
                con_dict['command'] = command
                con_dict['command_is_ok'] = True
                con_dict['output'] = con[1]
                result[con[0]] = con_dict
            else:                             
                con_dict = {}
                con_dict['connection_is_ok'] = False
                result[con[0]] = con_dict
        return result

    def send_config_set_to_devices(self, commands):
        result = {}
        for con in self.connections:
            for cmd in commands:
                if type(con[1]) == str:
                    result.append((con[0], cmd, con[1]))
                    continue
                result.append((con[0], cmd, con[1].send_command(cmd)))
        return result

    def close_connections(self):
        for con in self.connections:
            if not type(con[1]) == str:
                con[1].disconnect()

with open('devices.yaml') as f:
    devices = yaml.safe_load(f)

#ssh = NetmikoConnection(**devices[0])
#pprint(ssh.send_command('sh ip int br'))
#pprint(ssh.send_show_commands(['sh clock', 'sh ip int br']))
#pprint(ssh.send_config_set(['ip host aaa 1.1.1.1', 'ip host bbb 2.2.2.2']))
nch = NetmikoConnectionHandler(devices)
nch.open_connections()
pprint(nch.send_command_to_devices('sh clock'))
#pprint(nch.send_config_set_to_devices(['ip host aaa 1.1.1.1', 'ip host bbb 2.2.2.2']))
nch.close_connections()