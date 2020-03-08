import subprocess
import re

with open('is.txt', 'r') as fh:
    all_ips = fh.read().splitlines()

cmd = ['fping', '-c', '20']
cmd.extend(all_ips)

ping = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
items = ping.communicate()
result = items[-1].splitlines()
result = result[2:]
# for item in result:
#     print(item)


def statistics(res):
    status = True
    # print(res)
    last_array = res.split()
    # print(last_array)
    ip = last_array[0].decode()
    # if len(last_array) > 2:
    percentage = last_array[4].decode().split('/')[-1].replace('%,', '')
    # if int(percentage) > 50:
    #     status = False
    print(ip, percentage)

statistics(result[-1])

for res in result:
    statistics(res)