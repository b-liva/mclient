import random
import json
from os import system
import requests
import concurrent.futures
import config
import functools
import time
from ip2geotools.databases.noncommercial import DbIpCity
from do_handler import DoHandler


class IpHandler:
    ips = []
    my_ip = ''

    # def __init__(self):
    #     do_handler = DoHandler()
    #     self.my_ip = do_handler.my_ip
    #     print('my ip: ', self.my_ip)
    #     response = DbIpCity.get(self.my_ip, api_key='free')
    #     if response.country == 'IR':
    #         print('country: ', response.country)
    #         exit()
    def get_fake_ips(self):
        print('get the list of ips from each service(Amazon, Digital ocean, ...)')
        self.ips = [item['ip'] for item in config.ipds]
        print(self.ips)

    def get_ips(self):
        """gets a list of ips related to the servers"""
        url = "http://localhost:8002/mtph/get-all-servers"
        response = requests.get(url)
        print(response.json())
        self.ips = [item['ip'] for item in response.json()]
        print(self.ips)

    def get_id_by_ip(self, ip):
        for item in config.ipds:
            if item['ip'] == '200.132.169.8':
                id = item['id']
                return id

    def check_ip(self, ip):
        """
        pings each ip and return a boolean
        :return: Boolean
        """
        # for i in range(6):
        i = 0
        print('now pinging: %s' % ip)
        status = self.ping(ip)
        if status:
            print('********************************** ', ip, ' is up ************************************')
            # print(status)
            i += 1
            print('#: ', i)
            time.sleep(60)
            return ip
        else:
            print('********************************** ', ip, ' is down **********************************')
            i += 1
            print('#: ', i)
            old_ip = ip
            new_ip = self.change_server_with_ip(old_ip)
            print('new ip: ', new_ip)

            print('ip counts: ', len(self.ips), self.ips)

            return [old_ip, new_ip]

    def make_threads(self):
        """make threads for each of ips"""
        print('making %s threads' % len(self.ips))
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            for ip in self.ips:
                fu = executor.submit(self.check_ip, ip)
                fu.add_done_callback(functools.partial(self._future_completed, index=self.ips.index(ip)))

    def make_one_thread(self):
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            index = 0
            t1 = executor.submit(self.check_ip, self.ips[index])
            t1.add_done_callback(functools.partial(self._future_completed, index=index))

            index = 1
            t1 = executor.submit(self.check_ip, self.ips[index])
            t1.add_done_callback(functools.partial(self._future_completed, index=index))

    def _future_completed(self, future, **kwargs):
        with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
            index = 'no index'
            if 'index' in kwargs:
                index = kwargs['index']
            result = future.result()
            if len(result) == 2:
                print('call back finished ==> ', result, ' with index: ', index)
                print(result)
                old_ip = result[0]
                new_ip = result[1]
                index = self.ips.index(old_ip)
                self.ips[index] = new_ip
                print(self.ips)
                fu = executor.submit(self.check_ip, self.ips[index])
                fu.add_done_callback(functools.partial(self._future_completed, index=index))
                return fu
            else:
                ip = result

                # Test for failure
                # if ip == '5.144.130.116':
                #     self.ips[self.ips.index(ip)] = '34.5.4.6'
                #     ip = '34.5.4.6'

                index = self.ips.index(ip)
                fu = executor.submit(self.check_ip, self.ips[index])
                fu.add_done_callback(functools.partial(self._future_completed, index=index))
                return fu

    def ping(self, ip):
        response = system('ping ' + ip)
        if response == 0:
            return True
        elif response == 1:
            return False

    def change_server_with_ip(self, ip):
        """if an ip ping shows a failure then a request will be sent to the webapp to change the corresponting server"""
        print('Make a request to change the server with ip: ', ip)
        new_ip = str(int(200 * random.random())) \
                 + '.' + str(int(1000 * random.random())) \
                 + '.' + str(int(1000 * random.random())) \
                 + '.' + str(int(1000 * random.random()))
        return new_ip

    def change_server_by_id(self, id):
        url = 'http://localhost:8002/mtph/change-server'
        _data = {
            'id': id,
        }
        data = json.dumps(_data)
        response = requests.post(url, data)
        print(response)

    def api_request(self, url):
        response = requests.get(url)
        return response


def main():
    """running part of the script"""
    ip_handler = IpHandler()
    ip_handler.get_ips()
    # ip_handler.make_threads()
    # url = 'http://localhost:8002/mtph/test-json'
    # print(ip_handler.api_request(url).json())


    # url = 'http://localhost:8002/mtph/get-droplets'
    # drops = ip_handler.api_request(url).json()
    # drop = drops['droplets'][0]
    # print(drop)

    # id = ip_handler.get_id_by_ip('200.132.169.8')
    # print(id)
    # ip_handler.change_server_by_id(id)

if __name__ == '__main__':
    main()
