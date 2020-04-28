import subprocess 
import ipaddress

def ip_is_valid(ip):
    try:
        ipaddress.ip_address(ip)
        return True
    except ValueError as exc:
        #print(exc)
        return False
    

def ping(ip):    
    if not ip_is_valid(ip):
        #print('false')
        return False
    #print(ip)
    result = subprocess.run(f'ping {ip}', shell=True)#stdout=subprocess.DEVNULL)
    return result.returncode == 0
    #return not os.system('ping %s -n 1' % (ip))

    
def ping_ip_addresses(ips):
    ok = []
    bad = []
    for ip in ips:
        if(ping(ip)):
            ok.append(ip)
            #print(f'ok append = {ip}')
        else:
            bad.append(ip)
        
    return (ok, bad)

#print(ping('2.2.2.2'))