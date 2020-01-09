import random
import concurrent.futures
from config import fake_ips
from os import system
import concurrent.futures
import functools
import platform


class SandBox:

    def get_fake_ips(self):
        print('get the list of ips from each service(Amazon, Digital ocean, ...)')
        self.ips = [item['ip'] for item in fake_ips.ipds]
        print(self.ips)

    def change_server_with_ip(self, server):
        """if an ip ping shows a failure then a request will be sent to the webapp to change the corresponting server"""
        ip = server['ip']
        id = server['id']
        print('Make a request to change the server with ip: ', ip)
        new_id = str(int(10000000 * random.random()))
        new_ip = str(int(200 * random.random())) \
                 + '.' + str(int(1000 * random.random())) \
                 + '.' + str(int(1000 * random.random())) \
                 + '.' + str(int(1000 * random.random()))
        return {
        'id': new_id,
        'ip': new_ip,
        }

    def make_one_thread(self):
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            index = 0
            t1 = executor.submit(self.check_ip, self.conf_id[index])
            t1.add_done_callback(functools.partial(self._future_completed, index=index))

            index = 1
            t1 = executor.submit(self.check_ip, self.conf_id[index])
            t1.add_done_callback(functools.partial(self._future_completed, index=index))

    def ping2(self, ip):

        if platform.system() == 'Windows':
            response = system('ping ' + ip)
        else:
            response = system('ping -c 4 ' + ip)

        if response == 0:
            return True
        else:
            return False
