from nornir import InitNornir
from nornir.core.filter import F
from nornir.plugins.tasks.networking import netmiko_send_command
from nornir.plugins.functions.text import print_result

nr = InitNornir(config_file='nornir-config-local.yaml')

routers = nr.filter(F(groups__contains='routers')).inventory.hosts
switches = nr.filter(F(groups__contains='switches')).inventory.hosts

results = nr.run(task=netmiko_send_command, command_string='show cdp nei', use_textfsm=True)
print_result(results)