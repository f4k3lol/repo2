


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
from ping import ping

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

            
class NetmikoConnectionsHandler:
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

    def send_show_commands(self, commands):
        '''self.connections[i][0] device_ip, self.connections[i][1] - connection
            RETURNS:
            '192.168.0.92': [True,
                  [{'command_is_ok': True,
                    'ip host aaa 1.1.1.1': 'ip host aaa 1.1.1.1',
                    'output': ''},
                   {'command_is_ok': True,
                    'ip host bbb 2.2.2.2': 'ip host bbb 2.2.2.2',
                    'output': ''}]],
 '                  192.168.0.93': [False]}
        '''   
        if type(commands) == str:
            commands = [commands]    
        devices = {}   
        for con in self.connections:
            ip = con[0]
            connection = con[1]
           
            connection_is_ok = type(connection) != str 
            devices[ip] = [connection_is_ok]
            if not connection_is_ok:                
                continue
            connection.exit_config_mode()
            #connection.config_mode()
            results_list = []
            for cmd in commands:
                command_dict = {}
                command_dict['command'] = cmd
                command_dict['output'] = connection.send_command(cmd)
                command_dict['hostname'] = connection.find_prompt()[:-1]
                command_dict['command_is_ok'] = self._command_is_ok(command_dict['output'], command_dict['output'])
                results_list.append(command_dict)
            devices[ip].append(results_list)
                
        #devices.append(connection_dict)
        #pprint(devices)
        return devices

    def send_config_commands(self, commands):
        '''self.connections[i][0] device_ip, self.connections[i][1] - connection
            RETURNS:
            '192.168.0.92': [True,
                  [{'command_is_ok': True,
                    'ip host aaa 1.1.1.1': 'ip host aaa 1.1.1.1',
                    'output': ''},
                   {'command_is_ok': True,
                    'ip host bbb 2.2.2.2': 'ip host bbb 2.2.2.2',
                    'output': ''}]],
 '                  192.168.0.93': [False]}
        '''   
        if type(commands) == str:
            commands = [commands]    
        devices = {}   
        for con in self.connections:
            ip = con[0]
            connection = con[1]
           
            connection_is_ok = type(connection) != str 
            devices[ip] = [connection_is_ok]
            if not connection_is_ok:                
                continue

            connection.config_mode()
            results_list = []
            for cmd in commands:
                command_dict = {}
                command_dict['command'] = cmd
                command_dict['output'] = connection.send_command(cmd)
                command_dict['hostname'] = connection.find_prompt()[:-1]
                command_dict['command_is_ok'] = self._command_is_ok(command_dict['output'], command_dict['output'])
                results_list.append(command_dict)
            devices[ip].append(results_list)
                
        #devices.append(connection_dict)
        #pprint(devices)
        return devices

    def _command_is_ok(self, command, output):
        bad_outputs = ['Invalid input detected', 'Incomplete command', 'Ambiguous command']
        for bo in bad_outputs:
            if bo in output:
                return False
        return True

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
#nch = NetmikoConnectionHandler(devices)
#nch.open_connections()
#pprint(nch.send_command_to_devices('sh clock'))
#pprint(nch.send_config_commands_to_devices(['ip host aaa 1.1.1.1', 'ip host bbb 2.2.2.2']))
#nch.close_connections()