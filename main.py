import subprocess
import random
import json
from os import system
import requests
import concurrent.futures
import functools
import time
import platform
from config import config, fake_ips


class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


class IpHandler:
    ips = []
    conf_id = []
    my_ip = ''

    def get_fake_ips(self):
        print('get the list of ips from each service(Amazon, Digital ocean, ...)')
        self.ips = [item['ip'] for item in fake_ips.ipds]
        print(self.ips)

    def get_ips(self):
        """gets a list of ips related to the servers"""
        url = config.urls['get-all-servers']
        # url = "http://ff18da60.ngrok.io/mtph/get-all-servers"
        response = requests.get(url)
        print(response)
        self.conf_id = response.json()
        self.ips = [item['ip'] for item in self.conf_id]
        print(self.conf_id)
        print(self.ips)

    def get_id_by_ip(self, ip):
        for item in self.conf_id:
            if item['ip'] == ip:
                id = item['id']
                return id

    def check_ip(self, server, lock):
        print('server: ', server)
        """
        pings each ip and return a boolean
        :return: Boolean
        """
        # for i in range(6):
        ip = server['ip']
        i = 0
        print('now pinging: %s' % ip)
        net_status = self.ping('www.google.com')
        while not net_status:
            print('internet connection problem')
            net_status = self.ping('www.google.com')
            time.sleep(15)
        status = self.ping(ip)
        if status:
            print(f'{Colors.OKGREEN}**********************************{ip} is up ************************************{Colors.ENDC} ')
            # print(status)
            i += 1
            print('#: ', i)
            time.sleep(60)
            return server
        else:
            additional_check = False
            count = 5
            while count > 0:
                print(f'{Colors.WARNING}checking for again for certainty: {count} remaining for ip: {ip}{Colors.ENDC}')
                additional_check = self.ping(ip)
                count -= 1
                time.sleep(5)
            if additional_check:
                return server
            print(f'{Colors.FAIL}********************************** {ip} is down **********************************{Colors.ENDC}')
            i += 1
            print('#: ', i)
            old_server = server
            # new_server = self.change_server_with_ip(old_server)
            try:
                new_server = self.change_server_by_id(old_server['id'])
            except:
                print('something is wrong, finding newly created server')
                new_server = self.find_new_drop_by_ip(ip)
                if not new_server:
                    print('no server created before.')
                    return server

            lock.acquire()
            res = self.change_dns(old_server['ip'], new_server['ip'])
            lock.release()
            print('new ip: ', new_server)
            print('waiting to change dns...')
            time.sleep(90)
            print('ip counts: ', len(self.ips), self.ips)

            return [old_server, new_server]

    def make_threads(self):
        """make threads for each of ips"""
        import threading
        print('making %s threads' % len(self.ips))
        lock = threading.Lock()
        with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:

            for server in self.conf_id:
                fu = executor.submit(self.check_ip, server, lock)
                fu.add_done_callback(functools.partial(self._future_completed, index=self.conf_id.index(server), lock=lock))

    def make_one_thread(self):
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            index = 0
            t1 = executor.submit(self.check_ip, self.conf_id[index])
            t1.add_done_callback(functools.partial(self._future_completed, index=index))

            index = 1
            t1 = executor.submit(self.check_ip, self.conf_id[index])
            t1.add_done_callback(functools.partial(self._future_completed, index=index))

    def _future_completed(self, future, **kwargs):
        print('kwargs: ', kwargs)
        with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
            index = 'no index'
            if 'index' in kwargs:
                index = kwargs['index']
            lock = kwargs['lock']
            result = future.result()
            print('***********result:', result)
            if result.__class__.__name__ == 'list':
                # server failed and a new one is created.
                print('call back finished ==> ', result[0], ' with index: ', index)
                old_server = result[0]
                new_server = result[1]
                index = self.conf_id.index(old_server)
                self.conf_id[index] = new_server
                print(self.conf_id)
                fu = executor.submit(self.check_ip, self.conf_id[index], lock)
                fu.add_done_callback(functools.partial(self._future_completed, index=index, lock=lock))
                return fu
            else:
                # server is up
                server = result
                print('upserver: ', server)

                index = self.conf_id.index(server)
                fu = executor.submit(self.check_ip, self.conf_id[index], lock)
                fu.add_done_callback(functools.partial(self._future_completed, index=index, lock=lock))
                return fu

    def ping(self, ip):
        output = subprocess.Popen(["ping.exe", ip], stdout=subprocess.PIPE).communicate()[0]
        if str(output).count('Request timed out') > 1:
            return False
        return True

    def ping2(self, ip):

        if platform.system() == 'Windows':
            response = system('ping ' + ip)
        else:
            response = system('ping -c 4 ' + ip)

        if response == 0:
            return True
        else:
            return False

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

    def change_server_by_id(self, id):
        url = config.urls['change-server']
        _data = {
            'id': id,
        }
        data = json.dumps(_data)
        response = requests.post(url, data)
        new_serve = response.json()
        print('this is response with status: ', response)
        print('this is response only: ', new_serve)
        return new_serve

    def change_dns(self, old_ip, new_ip):
        url = config.urls['change-dns']
        _data = {
            'old_ip': old_ip,
            'new_ip': new_ip,
        }
        data = json.dumps(_data)
        response = requests.post(url, data)
        print(f'changing dns status: {response}')
        return response

    def find_new_drop_by_ip(self, ip):
        url = config.urls['find-new-drop']
        print(url)
        _data = {
            'old_ip': ip
        }
        data = json.dumps(_data)
        response = requests.post(url, data)
        print(response)
        new_server = response.json()
        return new_server

    def api_request(self, url):
        response = requests.get(url)
        return response


def main():
    """running part of the script"""
    ip_handler = IpHandler()
    ip_handler.get_ips()
    # ip_handler.ips = [item['ip'] for item in fake_ips.ipds]
    # ip_handler.conf_id = fake_ips.ipds
    # print(ip_handler.ips)

    ip_handler.make_threads()


if __name__ == '__main__':
    main()
