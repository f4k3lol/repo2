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

with open('../devices.yaml') as f:
    devices = yaml.safe_load(f)

try:
    with ConnectHandler(devices) as ssh:
        ssh.enable()
        

except (netmiko.ssh_exception.NetMikoAuthenticationException, 
    netmiko.ssh_exception.NetMikoTimeoutException) as e:
    print('Error!: ', e)        
