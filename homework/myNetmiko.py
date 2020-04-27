import netmiko
import time
from netmiko.cisco.cisco_ios import CiscoIosBase

class ErrorInCommand(Exception):
    pass

class NetmikoConnectionsHandler()


class MyNetmikoConnections(CiscoIosBase):
    def __init__(self, **device_params)
        super()._init_(**device_params)

    def send_show_commands_parallel(self, commands, workers=6, **kwargs):
        result = super.send_command()

    def send_show_command(self, command, **kwargs):   
        result = super().send_command(command, **kwargs)

class MyNetmiko2(CiscoIosBase):
    def __init__(self, **device_params):
        if not device_params.get('username'):
            device_params['username'] = input('Введите имя пользователя: ')
        if not device_params.get('password'):
            device_params['password'] = getpass(prompt='Введите пароль: ')
        if not device_params.get('secret'):
            device_params['secret'] = getpass(prompt='Введите пароль для режима enable: ') 
        super().__init__(**device_params)
        print(self.host)
        
    def send_command(self, command, ie = False, **kwargs):   
        result = super().send_command(command, **kwargs)
        if not ie:
            self._check_error_in_command(command, result)

    def send_config_set(self, commands, ignore_errors = True):
        if type(commands) == str:
            return self.send_command(commands, ie = ignore_errors)
        elif type(commands) == list:
            for cmd in commands:
                self.send_command(cmd, ie = ignore_errors)

    def _check_error_in_command(self, command, output):
        bad_outputs = ['Invalid input detected', 'Incomplete command', 'Ambiguous command']
        for bo in bad_outputs:
            if bo in output:                
                raise ErrorInCommand(f'При выполнении команды "{command}" на устройстве {self.host} возникла ошибка "{bo}"')

with open('../devices.yaml') as f:
    devices = yaml.safe_load(f)


