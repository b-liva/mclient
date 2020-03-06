import subprocess
import json
from os import system
import requests
import concurrent.futures
import functools
import time
import platform
import logging
from config import config, fake_ips


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

formatter = logging.Formatter('%(asctime)s:%(name)s:%(message)s')

file_handler = logging.FileHandler('debug.log')
# file_handler.setLevel(logging.ERROR)
file_handler.setFormatter(formatter)

stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter)

logger.addHandler(file_handler)
logger.addHandler(stream_handler)


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
    ips_not_in_dns = list()

    def get_ips(self):
        self.check_net_connectivity()
        """gets a list of ips related to the servers"""
        url = config.URLS['get-all-servers']
        # url = "http://ff18da60.ngrok.io/mtph/get-all-servers"
        response = requests.get(url)

        self.conf_id = response.json()
        self.ips = [item['ip'] for item in self.conf_id]

        print('ips: ', self.ips)
        logger.info(f'ips fetched: {self.ips}')

    def get_id_by_ip(self, ip):
        self.check_net_connectivity()
        for item in self.conf_id:
            if item['ip'] == ip:
                id = item['id']
                return id

    def check_ip(self, server, lock):
        """
        pings each ip and return a boolean
        :return: Boolean
        """

        ip = server['ip']
        i = 0
        print('Pinging: %s' % ip)

        status = self.ping(ip)
        if status:
            print(f'{Colors.OKGREEN}***************************{ip} is up *****************************{Colors.ENDC} ')
            i += 1
            print('#: ', i)
            if ip in self.ips_not_in_dns:
                print(f"Adding {ip} to dns was failed before. Now trying to add again.")
                res = self.change_dns(action='add', lock=lock, new_ip=ip)
                self.ips_not_in_dns.remove(ip)
                print(f'ips not in dns: {self.ips_not_in_dns}')
            time.sleep(30)
            return server
        else:
            ip_timing_status = ip in self.ips_not_in_dns
            timing = {
                'count': 1 if ip_timing_status else 2,
                'delay': 1 if ip_timing_status else 2
            }

            self.certainty_check(server, ip, count=timing['count'], delay=timing['delay'])
            # additional_check = False
            # count = 3
            # while count > 0:
            #     print(f'{Colors.WARNING}checking again for certainty: {count} remaining for ip: {ip}{Colors.ENDC}')
            #     additional_check = self.ping(ip)
            #     count -= 1
            #     time.sleep(3)
            #     if additional_check:
            #         return server
            print(f'{Colors.FAIL}*************************** {ip} is down *****************************{Colors.ENDC}')
            i += 1
            old_server = server
            # new_server = self.change_server_with_ip(old_server)
            try:
                # TODO: (3): What if this is the only ip?
                # TODO: Adding error log here.
                logger.info(f"Removing {old_server['ip']} from dns")
                self.change_dns('remove', lock, old_ip=old_server['ip'])
                if ip_timing_status:
                    self.ips_not_in_dns.remove(ip)
                # todo (5): Handling failure.
                new_server = self.change_server_by_id(old_server['id'])
                logger.info(f"New Server Created with ip: {new_server['ip']}")
            except:
                logger.warning('something is wrong, finding newly created server')
                new_server = self.find_new_drop_by_ip(ip)
                if not new_server:
                    logger.info('No server created before. So continue running with old server.')
                    # todo (8): Should we add dns again?
                    return server

            # todo (6): what if first checks fails and other passes.
            self.ping(new_server['ip'])
            time.sleep(5)
            status = self.ping(new_server['ip'])
            if status:
                logger.info(f"{new_server['ip']} is checked and working. prepare to add to dns")
                # else only pass the ip to check and change without changing dns

                res = self.change_dns(action='add', lock=lock, new_ip=new_server['ip'])

                print('new ip: ', new_server)
                print('waiting to change dns...')
                time.sleep(30)
            else:
                if new_server['ip'] not in self.ips_not_in_dns:
                    logger.warning(f"{new_server['ip']} just created but has failed.")
                    self.ips_not_in_dns.append(new_server['ip'])
                    logger.info(f'ips not in dns: {self.ips_not_in_dns}')

            return [old_server, new_server]

    def certainty_check(self, server, ip, count=3, delay=3):
        self.check_net_connectivity()
        additional_check = False
        while count > 0:
            print(f'{Colors.WARNING}checking again for certainty: {count} remaining for ip: {ip}{Colors.ENDC}')
            additional_check = self.ping(ip)
            count -= 1
            time.sleep(delay)
            if additional_check:
                return server

    def make_threads(self):
        """make threads for each of ips"""
        import threading
        print('making %s threads' % len(self.ips))
        lock = threading.Lock()
        with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:

            for server in self.conf_id:
                fu = executor.submit(self.check_ip, server, lock)
                fu.add_done_callback(functools.partial(self._future_completed, index=self.conf_id.index(server), lock=lock))

    def _future_completed(self, future, **kwargs):
        with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
            index = 'no index'
            if 'index' in kwargs:
                index = kwargs['index']
            lock = kwargs['lock']
            result = future.result()
            if result.__class__.__name__ == 'list':
                # server failed and a new one is created.
                old_server = result[0]
                new_server = result[1]
                print(f'new server is created:{new_server}')
                index = self.conf_id.index(old_server)
                self.conf_id[index] = new_server

                fu = executor.submit(self.check_ip, self.conf_id[index], lock)
                fu.add_done_callback(functools.partial(self._future_completed, index=index, lock=lock))
                return fu
            else:
                # server is up
                server = result

                index = self.conf_id.index(server)
                fu = executor.submit(self.check_ip, self.conf_id[index], lock)
                fu.add_done_callback(functools.partial(self._future_completed, index=index, lock=lock))
                return fu

    def ping(self, ip, check_net=True):
        if check_net:
            self.check_net_connectivity()
        output = subprocess.Popen(["ping.exe", ip], stdout=subprocess.PIPE).communicate()[0]
        if str(output).count('Request timed out') > 1:
            return False
        return True

    def check_net_connectivity(self):
        net_status = self.ping('www.google.com', check_net=False)
        while not net_status:
            print('internet connection problem')
            net_status = self.ping('www.google.com')
            time.sleep(5)
        return net_status

    def change_server_by_id(self, id):
        self.check_net_connectivity()
        url = config.URLS['change-server']
        _data = {
            'id': id,
        }
        data = json.dumps(_data)
        response = requests.post(url, data)
        new_serve = response.json()
        print('New server: ', new_serve)
        return new_serve

    def change_dns(self, action, lock, **kwargs):
        self.check_net_connectivity()
        lock.acquire()
        url = config.URLS['change-dns']
        _data = dict()
        if 'old_ip' in kwargs:
            _data['old_ip'] = kwargs['old_ip']
        if 'new_ip' in kwargs:
            _data['new_ip'] = kwargs['new_ip']
        _data['action'] = action
        data = json.dumps(_data)
        response = requests.post(url, data)
        print(f'change dns response: {response}')
        lock.release()
        return response

    def find_new_drop_by_ip(self, ip):
        self.check_net_connectivity()
        url = config.URLS['find-new-drop']
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
