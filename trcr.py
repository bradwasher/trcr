#!/usr/local/bin/python3

import subprocess
import csv
import re
import ipaddress
import sys
import os

def main():
    
    # check for command line arguments
    if len(sys.argv) > 1 and get_ip(sys.argv[1]):
        target = sys.argv[1]
    else:
        target = '8.8.8.8'
    
    
    # read in csv from file
    # https://lite.ip2location.com/database/ip-country?lang=en_US
    IP_FILE = os.path.join(os.path.dirname(__file__), 'IP2LOCATION-LITE-DB1.CSV')
    #IP_FILE = "IP2LOCATION-LITE-DB1.CSV"
    ip_list = load_csv(IP_FILE)
    
    # run traceroute
    print(f"\n{bcolors.BOLD}### Executing - traceroute -Tn -p 443 {target} ###{bcolors.ENDC}\n")
    proc = subprocess.Popen(['traceroute', '-Tn', '-p', '443', target],stdout=subprocess.PIPE)
    
    # read stdin until no more lines
    while True:
        line = proc.stdout.readline().decode().strip()
        if not line:
            break
        ip = get_ip(line)
        country = get_country(ip, ip_list)
        
        if ip is not None:
            line = line.replace(ip, f"{bcolors.BLUE}{ip}{bcolors.ENDC}")

        if country == "China":
            print(f"{line} - {bcolors.RED}{country}{bcolors.ENDC}")
        elif country == "unknown":
            print(f"{line} - {bcolors.YELLOW}{country}{bcolors.ENDC}")
        else:

            print(f"{line} - {bcolors.GREEN}{country}{bcolors.ENDC}")


def load_csv(path):
    with open(path, mode='r') as csv_file:
        #csv_reader = csv.DictReader(csv_file, fieldnames=['ip_start','ip_end','country_code','country'])
         data = list(csv.reader(csv_file))
    
    data.sort(key=lambda x: int(x[0]))
    return data

def get_ip(line):
    regex = "((25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9])\.){3}(25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9])"
    match = re.search(regex, line)
    return match.group(0) if match else None


def get_decimal_ip(ip):
    return int(ipaddress.ip_address(ip))

def get_is_private_ip(ip):
    return ipaddress.ip_address(ip).is_private

def get_country(ip, ip_list):
    if ip is None:
        return 'unknown'
    elif get_is_private_ip(ip):
        return 'private ip'
    else:
        dec_ip = get_decimal_ip(ip)
        val = binary_search(ip_list, 0, len(ip_list)-1, dec_ip)
        return val
    
def binary_search(arr, low, high, x):
    # each value in the array is an array itself with the values being as follows:
    # ip_start, ip_end, country_code, country
    

    # Check base case
    if high >= low:
 
        mid = (high + low) // 2
        #print(f"\nlow: {low} high: {high} mid: {mid} x: {x}")
        #print(arr[mid])
        # If element is present at the middle itself
        if int(arr[mid][0]) <= x and int(arr[mid][1]) >= x:
            return arr[mid][3] if arr[mid][3] != '-' else 'unknown'
 
        # If element is smaller than mid, then it can only
        # be present in left subarray
        elif int(arr[mid][0]) > x:
            return binary_search(arr, low, mid - 1, x)
 
        # Else the element can only be present in right subarray
        else:
            return binary_search(arr, mid + 1, high, x)
 
    else:
        # Element is not present in the array
        return 'Not here!!!!'
 

class bcolors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


if __name__ == "__main__":
    main()
